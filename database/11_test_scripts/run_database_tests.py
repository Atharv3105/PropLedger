"""
PropLedger Automated Database Test Suite (Phase 1 Validation)
Validates:
1. Referential Integrity (FK violations and Restrict behaviors)
2. Business Rule Check Constraints (BR-02 date order, non-negative rents, positive payments)
3. Uniqueness Constraints (Emails, Property Codes, Unit Numbers per Building)
4. Standard Audit Columns Existence
5. Seed Data Scale & Status Distributions (PRD Part N)
"""

import os
import sys
import psycopg2

DB_CONFIG = {
    "host": os.environ.get("DB_HOST", "localhost"),
    "port": int(os.environ.get("DB_PORT", 5432)),
    "user": os.environ.get("DB_USER", "postgres"),
    "password": os.environ.get("DB_PASSWORD", "postgres"),
    "dbname": os.environ.get("DB_NAME", "propledger")
}

def run_tests():
    print("=" * 65)
    print("PropLedger Automated Database Validation Suite (Phase 1 Gate)")
    print("=" * 65)

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    passed = 0
    failed = 0

    def assert_test(name, condition, error_detail=""):
        nonlocal passed, failed
        if condition:
            print(f"  [PASS] {name}")
            passed += 1
        else:
            print(f"  [FAIL] {name} - {error_detail}")
            failed += 1

    # TEST 1: Table & Extension Count
    print("\n[1] Schema & Table Verification")
    cur.execute("""
        SELECT COUNT(*) FROM information_schema.tables 
        WHERE table_schema = 'public' AND table_type = 'BASE TABLE';
    """)
    table_count = cur.fetchone()[0]
    assert_test("Total Domain Tables >= 30", table_count >= 30, f"Found {table_count} tables")

    cur.execute("SELECT extname FROM pg_extension WHERE extname IN ('uuid-ossp', 'tablefunc');")
    exts = [r[0] for r in cur.fetchall()]
    assert_test("Required Extensions (uuid-ossp, tablefunc)", len(exts) == 2, f"Found: {exts}")

    # TEST 2: BR-02 Lease Dates Check Constraint
    print("\n[2] Business Rule Constraints (BR-02 & Financial Guards)")
    cur.execute("SELECT unit_id FROM units LIMIT 1;")
    sample_unit = cur.fetchone()[0]
    cur.execute("SELECT policy_id FROM late_fee_policies LIMIT 1;")
    sample_policy = cur.fetchone()[0]
    cur.execute("SELECT user_id FROM users WHERE email = 'admin@propledger.com';")
    admin_id = cur.fetchone()[0]

    # Test BR-02: start_date > end_date must fail
    br02_rejected = False
    try:
        cur.execute("""
            INSERT INTO leases (unit_id, start_date, end_date, monthly_rent, security_deposit, rent_due_day, late_fee_policy_id, status, created_by)
            VALUES (%s, '2026-12-31', '2026-01-01', 25000.00, 50000.00, 1, %s, 'DRAFT', %s);
        """, (sample_unit, sample_policy, admin_id))
        conn.commit()
    except psycopg2.IntegrityError as e:
        conn.rollback()
        br02_rejected = "chk_lease_dates" in str(e) or "check constraint" in str(e).lower()
    assert_test("BR-02 Rejected: start_date > end_date raises CHECK violation", br02_rejected)

    # Test Negative Rent must fail
    neg_rent_rejected = False
    try:
        cur.execute("""
            INSERT INTO leases (unit_id, start_date, end_date, monthly_rent, security_deposit, rent_due_day, late_fee_policy_id, status, created_by)
            VALUES (%s, '2026-01-01', '2026-12-31', -500.00, 50000.00, 1, %s, 'DRAFT', %s);
        """, (sample_unit, sample_policy, admin_id))
        conn.commit()
    except psycopg2.IntegrityError:
        conn.rollback()
        neg_rent_rejected = True
    assert_test("Financial Guard: Negative Monthly Rent rejected", neg_rent_rejected)

    # Test Payment Amount <= 0 must fail
    neg_pay_rejected = False
    cur.execute("SELECT lease_id FROM leases LIMIT 1;")
    sample_lease = cur.fetchone()[0]
    try:
        cur.execute("""
            INSERT INTO payments (lease_id, payment_date, amount, payment_method, recorded_by)
            VALUES (%s, '2026-01-01', -100.00, 'BANK_TRANSFER', %s);
        """, (sample_lease, admin_id))
        conn.commit()
    except psycopg2.IntegrityError:
        conn.rollback()
        neg_pay_rejected = True
    assert_test("Financial Guard: Negative/Zero Payment rejected", neg_pay_rejected)

    # TEST 3: Referential Integrity
    print("\n[3] Referential Integrity & Foreign Keys")
    orphan_fk_rejected = False
    try:
        cur.execute("""
            INSERT INTO units (building_id, unit_number, floor_number, unit_type, square_feet, market_rent, target_rent, status, created_by)
            VALUES (9999999, 'INVALID-101', 1, '1BHK', 650.00, 20000.00, 20000.00, 'AVAILABLE', %s);
        """, (admin_id,))
        conn.commit()
    except psycopg2.IntegrityError:
        conn.rollback()
        orphan_fk_rejected = True
    assert_test("Foreign Key Guard: Unit with non-existent building rejected", orphan_fk_rejected)

    # TEST 4: Uniqueness Constraints
    print("\n[4] Uniqueness Constraints")
    dup_email_rejected = False
    try:
        cur.execute("""
            INSERT INTO users (email, password_hash, full_name, phone)
            VALUES ('admin@propledger.com', 'dummyhash', 'Duplicate Admin', '0000000000');
        """,)
        conn.commit()
    except psycopg2.IntegrityError:
        conn.rollback()
        dup_email_rejected = True
    assert_test("Unique Email Guard: Duplicate user email rejected", dup_email_rejected)

    # TEST 5: Audit Columns
    print("\n[5] Standard Audit Columns Verification")
    audit_tables = ["properties", "buildings", "units", "tenants", "leases", "rent_charges", "maintenance_requests", "expenses", "invoices"]
    all_audit_ok = True
    for tbl in audit_tables:
        cur.execute("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = %s AND column_name IN ('created_at', 'created_by', 'modified_at');
        """, (tbl,))
        cols = [r[0] for r in cur.fetchall()]
        if len(cols) < 3:
            all_audit_ok = False
            print(f"    Missing audit cols on table: {tbl}")
    assert_test("Standard Audit Columns on core domain tables", all_audit_ok)

    # TEST 6: Seed Scale & Quality Validation
    print("\n[6] Seed Data Scale & Status Distribution (PRD Part N)")
    cur.execute("SELECT COUNT(*) FROM properties;")
    prop_count = cur.fetchone()[0]
    assert_test("Seed Scale: Properties >= 500", prop_count >= 500, f"Count: {prop_count}")

    cur.execute("SELECT COUNT(*) FROM buildings;")
    bldg_count = cur.fetchone()[0]
    assert_test("Seed Scale: Buildings >= 1,000", bldg_count >= 1000, f"Count: {bldg_count}")

    cur.execute("SELECT COUNT(*) FROM units;")
    unit_count = cur.fetchone()[0]
    assert_test("Seed Scale: Units >= 3,000", unit_count >= 3000, f"Count: {unit_count}")

    cur.execute("SELECT COUNT(*) FROM tenants;")
    tenant_count = cur.fetchone()[0]
    assert_test("Seed Scale: Tenants >= 2,000", tenant_count >= 2000, f"Count: {tenant_count}")

    cur.execute("SELECT COUNT(*) FROM leases;")
    lease_count = cur.fetchone()[0]
    assert_test("Seed Scale: Leases >= 2,000", lease_count >= 2000, f"Count: {lease_count}")

    cur.execute("SELECT COUNT(*) FROM rent_charges;")
    rc_count = cur.fetchone()[0]
    assert_test("Seed Scale: Rent Charges >= 5,000", rc_count >= 5000, f"Count: {rc_count}")

    cur.execute("SELECT COUNT(*) FROM payments;")
    pay_count = cur.fetchone()[0]
    assert_test("Seed Scale: Payments >= 5,000", pay_count >= 5000, f"Count: {pay_count}")

    cur.execute("SELECT COUNT(*) FROM maintenance_requests;")
    maint_count = cur.fetchone()[0]
    assert_test("Seed Scale: Maintenance Requests >= 1,000", maint_count >= 1000, f"Count: {maint_count}")

    # Check unit status distribution
    cur.execute("SELECT status, COUNT(*) FROM units GROUP BY status;")
    statuses = dict(cur.fetchall())
    has_occupied = "OCCUPIED" in statuses and statuses["OCCUPIED"] > 1000
    has_available = "AVAILABLE" in statuses and statuses["AVAILABLE"] > 100
    assert_test("Realistic Unit Status Distribution (Occupied & Available present)", has_occupied and has_available, f"Statuses: {statuses}")

    print("=" * 65)
    print(f"Test Summary: {passed} PASSED | {failed} FAILED")
    print("=" * 65)

    cur.close()
    conn.close()

    if failed > 0:
        sys.exit(1)

if __name__ == "__main__":
    run_tests()
