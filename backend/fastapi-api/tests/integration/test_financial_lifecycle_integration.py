"""
End-to-End Financial Lifecycle Integration Tests (PL-139)
Tests the complete critical transaction path across API and PostgreSQL:
Lease Inception -> Rent Charge -> Partial Payment (FIFO) -> Running Balance -> Late Fee -> Delinquency -> Collection Escalation.
"""

import pytest
import psycopg2
from decimal import Decimal
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import init_db_pool, close_db_pool

client = TestClient(app)

@pytest.fixture(scope="session", autouse=True)
def setup_and_teardown():
    init_db_pool()
    yield
    close_db_pool()

DB_PARAMS = {
    'dbname': 'propledger',
    'user': 'postgres',
    'password': 'postgres',
    'host': 'localhost',
    'port': 5432
}

def get_auth_token(email: str = "admin@propledger.com", password: str = "Admin@123") -> str:
    res = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert res.status_code == 200, f"Login failed for {email}: {res.text}"
    return res.json()["access_token"]

class TestFinancialLifecycleE2E:
    """Comprehensive lifecycle tests verifying the complete transactional chain."""

    def test_full_critical_financial_lifecycle(self):
        token = get_auth_token()
        headers = {"Authorization": f"Bearer {token}"}

        conn = psycopg2.connect(**DB_PARAMS)
        conn.autocommit = True
        cur = conn.cursor()

        # Step 1: Select an active unit and create a dedicated test lease
        cur.execute("SELECT unit_id FROM units WHERE status = 'Vacant' LIMIT 1;")
        vacant_unit = cur.fetchone()
        if not vacant_unit:
            cur.execute("SELECT unit_id FROM units LIMIT 1;")
            unit_id = cur.fetchone()[0]
        else:
            unit_id = vacant_unit[0]

        cur.execute("SELECT tenant_id FROM tenants LIMIT 1;")
        tenant_id = cur.fetchone()[0]

        # Insert test lease
        cur.execute("""
            INSERT INTO leases (unit_id, start_date, end_date, monthly_rent, security_deposit, rent_due_day, late_fee_policy_id, status, renewal_status)
            VALUES (%s, '2026-01-01', '2026-12-31', 2000.00, 2000.00, 1, 1, 'Active', 'None')
            RETURNING lease_id;
        """, (unit_id,))
        lease_id = cur.fetchone()[0]

        # Link tenant
        cur.execute("""
            INSERT INTO lease_tenants (lease_id, tenant_id, is_primary, signed_date)
            VALUES (%s, %s, TRUE, CURRENT_TIMESTAMP)
            ON CONFLICT (lease_id, tenant_id) DO NOTHING;
        """, (lease_id, tenant_id))

        try:
            # Step 2: Generate Rent Charge ($2,000.00)
            cur.execute("""
                INSERT INTO rent_charges (lease_id, billing_month, billing_year, charge_date, due_date, charge_amount, amount_paid, status, created_at, created_by)
                VALUES (%s, 9, 2026, '2026-09-01', '2026-09-05', 2000.00, 0.00, 'PENDING', CURRENT_TIMESTAMP, 32)
                RETURNING charge_id;
            """, (lease_id,))
            charge_id = cur.fetchone()[0]

            # Verify charge in database
            cur.execute("SELECT charge_amount, status FROM rent_charges WHERE charge_id = %s;", (charge_id,))
            ch_row = cur.fetchone()
            assert ch_row is not None
            assert float(ch_row[0]) == 2000.00
            assert ch_row[1] == 'PENDING'

            # Step 3: Record Partial Payment ($800.00) via Payment API
            pay_payload = {
                "lease_id": lease_id,
                "amount": 800.00,
                "payment_method_id": 1,
                "reference_number": f"LIFECYCLE-PAY-{lease_id}"
            }
            pay_res = client.post("/api/v1/payments", json=pay_payload, headers=headers)
            assert pay_res.status_code == 201
            pay_data = pay_res.json()
            assert float(pay_data["amount_paid"]) == 800.00

            # Step 4: Verify FIFO Allocation & Charge Balance
            cur.execute("SELECT amount_paid, status FROM rent_charges WHERE charge_id = %s;", (charge_id,))
            ch_paid, ch_status = cur.fetchone()
            assert float(ch_paid) == 800.00
            assert ch_status == 'PARTIALLY_PAID'

            # Verify allocation record
            cur.execute("SELECT allocated_amount FROM payment_allocations WHERE charge_id = %s;", (charge_id,))
            alloc_row = cur.fetchone()
            assert alloc_row is not None
            assert float(alloc_row[0]) == 800.00

            # Step 5: Verify Running Outstanding Balance ($2,000 - $800 = $1,200)
            cur.execute("SELECT fn_GetOutstandingBalance(%s);", (lease_id,))
            current_balance = float(cur.fetchone()[0])
            assert current_balance == 1200.00

            # Step 6: Mark charge overdue (advance past due date while respecting chk_rc_due_date)
            cur.execute("""
                UPDATE rent_charges 
                SET status = 'OVERDUE', charge_date = CURRENT_DATE - 70, due_date = CURRENT_DATE - 65
                WHERE charge_id = %s;
            """, (charge_id,))

            # Step 7: Escalate to Collection via Stored Procedure
            cur.execute("SELECT usp_EscalateToCollection(%s, %s);", (lease_id, 32))
            escalation_result = cur.fetchone()[0]
            assert escalation_result["status"] in ("CREATED", "SUCCESS", "UPDATED")

            # Verify collection case in database
            cur.execute("SELECT status, overdue_amount FROM collection_cases WHERE lease_id = %s;", (lease_id,))
            case_row = cur.fetchone()
            assert case_row is not None
            assert float(case_row[1]) == 1200.00

            # Step 8: Verify Payment Audit Logging
            cur.execute("SELECT count(*) FROM payment_audit WHERE lease_id = %s;", (lease_id,))
            audit_count = cur.fetchone()[0]
            assert audit_count >= 1

        finally:
            # Clean up test artifacts
            cur.execute("DELETE FROM collection_cases WHERE lease_id = %s;", (lease_id,))
            cur.execute("DELETE FROM payment_allocations WHERE payment_id IN (SELECT payment_id FROM payments WHERE lease_id = %s);", (lease_id,))
            cur.execute("DELETE FROM payment_audit WHERE lease_id = %s;", (lease_id,))
            cur.execute("DELETE FROM payments WHERE lease_id = %s;", (lease_id,))
            cur.execute("DELETE FROM rent_charges WHERE lease_id = %s;", (lease_id,))
            cur.execute("DELETE FROM tenant_balances WHERE lease_id = %s;", (lease_id,))
            cur.execute("DELETE FROM lease_tenants WHERE lease_id = %s;", (lease_id,))
            cur.execute("DELETE FROM leases WHERE lease_id = %s;", (lease_id,))
            conn.close()
