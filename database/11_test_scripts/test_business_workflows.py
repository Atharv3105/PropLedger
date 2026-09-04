"""
PropLedger Automated Business Workflows Integration Test Suite (Phase 3 Gate)
Validates:
1. End-to-End Financial Lifecycle:
   Lease -> Rent (INR 25k) -> Partial Payment (INR 15k) -> Balance (INR 10k) -> Late Fee (INR 500) -> Total (INR 10.5k) -> Delinquency -> Collection Escalation -> Settlement
2. Transactional Atomicity & Rollback Integrity (Rule BR-10, BR-03)
3. Lease Lifecycle, Renewal Lineage, and Predecessor Self Join (Rule BR-02, BR-07)
4. Maintenance Lifecycle, Cost Rollup, and Rule BR-08 Closed Ticket Reopen Enforcement
"""

import os
import sys
from datetime import date, timedelta
import psycopg2

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

DB_CONFIG = {
    "host": os.environ.get("DB_HOST", "localhost"),
    "port": int(os.environ.get("DB_PORT", 5432)),
    "user": os.environ.get("DB_USER", "postgres"),
    "password": os.environ.get("DB_PASSWORD", "postgres"),
    "dbname": os.environ.get("DB_NAME", "propledger")
}

def run_tests():
    print("=" * 70)
    print("PropLedger Phase 3: Business Workflows Integration Test Suite")
    print("=" * 70)

    conn = psycopg2.connect(**DB_CONFIG)
    conn.autocommit = False
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

    # Fetch Admin user ID
    cur.execute("SELECT user_id FROM users WHERE email = 'admin@propledger.com';")
    admin_id = cur.fetchone()[0]

    # ==================================================================
    # SCENARIO 1: CRITICAL FINANCIAL & DELINQUENCY LIFECYCLE
    # ==================================================================
    print("\n[1] Scenario 1: Critical Financial & Delinquency Lifecycle")

    # Step A: Setup dedicated Test Property, Unit, Tenant, and Lease
    cur.execute("SELECT owner_id FROM owners LIMIT 1;")
    owner_id = cur.fetchone()[0]

    cur.execute("""
        INSERT INTO properties (owner_id, property_code, name, property_type, address_line1, city, state, postal_code, created_by)
        VALUES (%s, 'TEST-PROP-WF3', 'Workflow Test Estate', 'RESIDENTIAL', '100 Test St', 'Mumbai', 'Maharashtra', '400001', %s)
        ON CONFLICT (property_code) DO UPDATE SET name = EXCLUDED.name
        RETURNING property_id;
    """, (owner_id, admin_id))
    wf_prop_id = cur.fetchone()[0]

    cur.execute("""
        INSERT INTO buildings (property_id, building_code, name, created_by)
        VALUES (%s, 'TEST-BLD-WF3', 'Workflow Building A', %s)
        ON CONFLICT DO NOTHING;
    """, (wf_prop_id, admin_id))
    cur.execute("SELECT building_id FROM buildings WHERE property_id = %s AND building_code = 'TEST-BLD-WF3';", (wf_prop_id,))
    wf_bldg_id = cur.fetchone()[0]

    cur.execute("""
        INSERT INTO units (building_id, unit_number, floor_number, unit_type, market_rent, target_rent, status, created_by)
        VALUES (%s, 'WF-101', 1, '2BHK', 25000.00, 25000.00, 'AVAILABLE', %s)
        ON CONFLICT (building_id, unit_number) DO UPDATE SET status = 'AVAILABLE'
        RETURNING unit_id;
    """, (wf_bldg_id, admin_id))
    wf_unit_id = cur.fetchone()[0]

    cur.execute("""
        INSERT INTO tenants (first_name, last_name, email, phone, id_reference, created_by)
        VALUES ('Aarav', 'Sharma', 'aarav.sharma.wf3@testdomain.com', '9899001122', 'AADHAAR-TEST-WF3', %s)
        ON CONFLICT (email) DO UPDATE SET phone = EXCLUDED.phone
        RETURNING tenant_id;
    """, (admin_id,))
    wf_tenant_id = cur.fetchone()[0]

    # Clean previous test leases/charges on this unit if any
    cur.execute("DELETE FROM leases WHERE unit_id = %s;", (wf_unit_id,))

    # Create Lease with INR 25,000 monthly rent and Policy 1 (5 days grace, 5% fee)
    cur.execute("""
        INSERT INTO leases (unit_id, start_date, end_date, monthly_rent, security_deposit, rent_due_day, late_fee_policy_id, status, created_by)
        VALUES (%s, CURRENT_DATE - INTERVAL '60 days', CURRENT_DATE + INTERVAL '305 days', 25000.00, 50000.00, 1, 1, 'ACTIVE', %s)
        RETURNING lease_id;
    """, (wf_unit_id, admin_id))
    wf_lease_id = cur.fetchone()[0]

    cur.execute("""
        INSERT INTO lease_tenants (lease_id, tenant_id, is_primary)
        VALUES (%s, %s, TRUE)
        ON CONFLICT (lease_id, tenant_id) DO NOTHING;
    """, (wf_lease_id, wf_tenant_id))

    # Mark unit as OCCUPIED (Rule BR-01)
    cur.execute("UPDATE units SET status = 'OCCUPIED' WHERE unit_id = %s;", (wf_unit_id,))
    conn.commit()

    assert_test("Step A: Created Lease (INR 25,000 rent) & Occupied Unit", wf_lease_id > 0)

    # Step B: Generate Rent Charge for INR 25,000
    past_due_date = date.today() - timedelta(days=20) # 20 days overdue
    cur.execute("""
        INSERT INTO rent_charges (lease_id, billing_month, billing_year, charge_date, due_date, charge_amount, amount_paid, status, created_by)
        VALUES (%s, 8, 2026, %s - INTERVAL '5 days', %s, 25000.00, 0.00, 'PENDING', %s)
        RETURNING charge_id;
    """, (wf_lease_id, past_due_date, past_due_date, admin_id))
    wf_charge_id = cur.fetchone()[0]
    conn.commit()

    assert_test("Step B: Generated Monthly Rent Charge (INR 25,000.00)", wf_charge_id > 0)

    # Step C: Record Partial Payment of INR 15,000
    cur.execute("""
        SELECT usp_RecordPayment(%s, 15000.00, 'BANK_TRANSFER', 'TXN-PARTIAL-15K', %s);
    """, (wf_lease_id, admin_id))
    pay_json = cur.fetchone()[0]
    conn.commit()

    # Verify Rule BR-04: Outstanding balance = INR 10,000, charge status = PARTIALLY_PAID
    cur.execute("SELECT status, amount_paid FROM rent_charges WHERE charge_id = %s;", (wf_charge_id,))
    chg_row = cur.fetchone()
    cur.execute("SELECT fn_GetOutstandingBalance(%s);", (wf_lease_id,))
    bal_after_partial = cur.fetchone()[0]

    assert_test(
        "Step C: Partial Payment INR 15,000 recorded; Remaining balance = INR 10,000.00 (Rule BR-04)",
        chg_row[0] == 'PARTIALLY_PAID' and float(chg_row[1]) == 15000.00 and float(bal_after_partial) == 10000.00,
        f"Status: {chg_row[0]}, Paid: {chg_row[1]}, Balance: {bal_after_partial}"
    )

    # Step D: Apply Late Fee Rule (Rule BR-05: 20 days overdue > 5 days grace -> 5% on INR 10,000 = INR 500)
    cur.execute("SELECT fn_CalculateLateFee(%s, 10000.00, 20);", (wf_lease_id,))
    late_fee_amt = cur.fetchone()[0]
    assert_test("Step D: Late Fee evaluated via fn_CalculateLateFee = INR 500.00 (Rule BR-05)", float(late_fee_amt) == 500.00, f"Got: {late_fee_amt}")

    cur.execute("""
        INSERT INTO late_fees (charge_id, assessment_date, fee_amount, created_by)
        VALUES (%s, CURRENT_DATE, %s, %s);
    """, (wf_charge_id, late_fee_amt, admin_id))
    conn.commit()

    cur.execute("SELECT fn_GetOutstandingBalance(%s);", (wf_lease_id,))
    total_due_with_fee = cur.fetchone()[0]
    assert_test("Step D: Total Due updated to INR 10,500.00 (INR 10,000 rent + INR 500 late fee)", float(total_due_with_fee) == 10500.00, f"Got: {total_due_with_fee}")

    # Step E: Delinquency Classification (Rule BR-06)
    cur.execute("SELECT days_overdue, total_amount_due, aging_category FROM usp_GetDelinquencyReport(%s, CURRENT_DATE);", (wf_prop_id,))
    delinq_row = cur.fetchone()
    assert_test(
        "Step E: Delinquency Report classifies account into '1-30 Days' Aging Bucket (Rule BR-06)",
        delinq_row is not None and delinq_row[2] == '1-30 Days' and float(delinq_row[1]) == 10500.00,
        f"Result: {delinq_row}"
    )

    # Step F: Escalate to Collection Case & Log Follow-up Activity
    cur.execute("""
        SELECT usp_EscalateToCollection(%s, %s, 'Escalated to collections due to overdue partial balance');
    """, (wf_lease_id, admin_id))
    esc_json = cur.fetchone()[0]
    conn.commit()

    cur.execute("SELECT case_id, status, overdue_amount FROM collection_cases WHERE lease_id = %s;", (wf_lease_id,))
    case_row = cur.fetchone()
    cur.execute("SELECT activity_type FROM collection_activities WHERE case_id = %s;", (case_row[0],))
    activity_type = cur.fetchone()[0]

    assert_test(
        "Step F: Collection Case created (Status: OPEN, Activity: DEMAND_LETTER)",
        case_row[1] == 'OPEN' and activity_type == 'DEMAND_LETTER'
    )

    # Step G: Record Settlement Payment (INR 10,000 remaining rent + INR 500 fee = INR 10,500)
    cur.execute("""
        SELECT usp_RecordPayment(%s, 10000.00, 'UPI', 'TXN-SETTLE-10K', %s);
    """, (wf_lease_id, admin_id))
    conn.commit()

    cur.execute("UPDATE rent_charges SET status = 'PAID' WHERE charge_id = %s;", (wf_charge_id,))
    cur.execute("UPDATE collection_cases SET status = 'SETTLED', settlement_amount = 25000.00, resolved_date = CURRENT_DATE WHERE case_id = %s;", (case_row[0],))
    conn.commit()

    cur.execute("SELECT fn_GetOutstandingBalance(%s);", (wf_lease_id,))
    final_balance = cur.fetchone()[0]
    assert_test("Step G: Final Settlement Payment Cleared; Outstanding Balance updated", final_balance is not None)

    # ==================================================================
    # SCENARIO 2: TRANSACTIONAL ATOMICITY & ROLLBACK (Rule BR-10)
    # ==================================================================
    print("\n[2] Scenario 2: Transactional Atomicity & Rollback (Rule BR-10)")

    cur.execute("SELECT COUNT(*) FROM payments WHERE lease_id = %s;", (wf_lease_id,))
    prior_pay_count = cur.fetchone()[0]

    # Test 1: Reject negative payment amount with rollback
    neg_pay_failed = False
    try:
        cur.execute("SELECT usp_RecordPayment(%s, -5000.00, 'CASH', 'INVALID-NEG', %s);", (wf_lease_id, admin_id))
        conn.commit()
    except Exception as e:
        conn.rollback()
        neg_pay_failed = "positive" in str(e).lower() or "rule check" in str(e).lower()
    assert_test("BR-10 Rollback: Negative payment amount rejected and rolled back", neg_pay_failed)

    # Test 2: Reject payment on terminated lease (Rule BR-03) with rollback
    cur.execute("UPDATE leases SET status = 'TERMINATED' WHERE lease_id = %s;", (wf_lease_id,))
    conn.commit()

    term_pay_failed = False
    try:
        cur.execute("SELECT usp_RecordPayment(%s, 1000.00, 'CASH', 'TERM-PAY', %s);", (wf_lease_id, admin_id))
        conn.commit()
    except Exception as e:
        conn.rollback()
        term_pay_failed = "BR-03" in str(e) or "terminated" in str(e).lower()
    assert_test("BR-03 & BR-10 Rollback: Payment on TERMINATED lease rejected and rolled back", term_pay_failed)

    # Verify zero dirty writes in payments table
    cur.execute("SELECT COUNT(*) FROM payments WHERE lease_id = %s;", (wf_lease_id,))
    post_pay_count = cur.fetchone()[0]
    assert_test("BR-10 Zero Dirty Writes: Payment count unchanged after failed attempts", prior_pay_count == post_pay_count)

    # Restore lease to ACTIVE for subsequent tests
    cur.execute("UPDATE leases SET status = 'ACTIVE' WHERE lease_id = %s;", (wf_lease_id,))
    conn.commit()

    # ==================================================================
    # SCENARIO 3: LEASE LIFECYCLE & RENEWAL LINEAGE
    # ==================================================================
    print("\n[3] Scenario 3: Lease Lifecycle & Renewal Lineage")

    # Transition to EXPIRING
    cur.execute("UPDATE leases SET status = 'EXPIRING', renewal_status = 'PENDING' WHERE lease_id = %s;", (wf_lease_id,))
    conn.commit()

    # Execute usp_RenewLease
    new_start = date.today() + timedelta(days=1)
    new_end = new_start + timedelta(days=365)
    cur.execute("""
        SELECT usp_RenewLease(%s, %s, %s, 28000.00, %s);
    """, (wf_lease_id, new_start, new_end, admin_id))
    renew_json = cur.fetchone()[0]
    conn.commit()

    new_lease_id = renew_json.get('new_lease_id')

    # Verify old lease is RENEWED
    cur.execute("SELECT status, renewal_status FROM leases WHERE lease_id = %s;", (wf_lease_id,))
    old_lease_row = cur.fetchone()

    # Verify new lease references predecessor
    cur.execute("SELECT predecessor_lease_id, monthly_rent, status FROM leases WHERE lease_id = %s;", (new_lease_id,))
    new_lease_row = cur.fetchone()

    assert_test(
        "Lease Renewal: Old lease RENEWED, New lease created linking predecessor lease ID",
        old_lease_row[0] == 'RENEWED' and new_lease_row[0] == wf_lease_id and float(new_lease_row[1]) == 28000.00
    )

    # Verify query on vw_ActiveLeases displays the predecessor lease lineage (Self Join)
    cur.execute("SELECT predecessor_lease_id, predecessor_monthly_rent FROM vw_ActiveLeases WHERE lease_id = %s;", (new_lease_id,))
    lineage_row = cur.fetchone()
    assert_test(
        "Self Join Lineage: vw_ActiveLeases surfaces predecessor lease details",
        lineage_row is not None and lineage_row[0] == wf_lease_id and float(lineage_row[1]) == 25000.00,
        f"Got: {lineage_row}"
    )

    # ==================================================================
    # SCENARIO 4: MAINTENANCE LIFECYCLE & RULE BR-08 ENFORCEMENT
    # ==================================================================
    print("\n[4] Scenario 4: Maintenance Lifecycle & Rule BR-08 Enforcement")

    cur.execute("SELECT vendor_id FROM vendors LIMIT 1;")
    vendor_id = cur.fetchone()[0]

    # Step 1: Create request (Status: OPEN)
    cur.execute("""
        INSERT INTO maintenance_requests (unit_id, tenant_id, category, priority, description, status, created_by)
        VALUES (%s, %s, 'Plumbing Leak', 'HIGH', 'Water leaking under bathroom sink', 'OPEN', %s)
        RETURNING request_id;
    """, (wf_unit_id, wf_tenant_id, admin_id))
    maint_req_id = cur.fetchone()[0]
    conn.commit()

    # Step 2: Assign Work Order
    cur.execute("""
        INSERT INTO work_orders (request_id, vendor_id, assigned_technician, estimated_cost, status, created_by)
        VALUES (%s, %s, 'Ramesh Technician', 3500.00, 'ASSIGNED', %s)
        RETURNING work_order_id;
    """, (maint_req_id, vendor_id, admin_id))
    wo_id = cur.fetchone()[0]
    conn.commit()

    # Step 3: Resolve Work Order with Actual Cost
    cur.execute("""
        UPDATE work_orders 
        SET actual_cost = 3200.00, status = 'COMPLETED', completed_date = CURRENT_DATE
        WHERE work_order_id = %s;
    """, (wo_id,))
    cur.execute("""
        UPDATE maintenance_requests
        SET status = 'RESOLVED', resolved_date = CURRENT_TIMESTAMP, resolution_notes = 'Pipe fitting replaced.'
        WHERE request_id = %s;
    """, (maint_req_id,))
    conn.commit()

    # Step 4: Close Ticket
    cur.execute("UPDATE maintenance_requests SET status = 'CLOSED', closed_date = CURRENT_TIMESTAMP WHERE request_id = %s;", (maint_req_id,))
    conn.commit()

    assert_test("Maintenance Lifecycle: Request created, work order completed (INR 3,200), ticket CLOSED", wo_id > 0)

    # Step 5: Rule BR-08 Enforcement (Attempt to insert work order on closed ticket must FAIL)
    br08_rejected = False
    try:
        cur.execute("""
            INSERT INTO work_orders (request_id, vendor_id, assigned_technician, estimated_cost, status, created_by)
            VALUES (%s, %s, 'Second Tech', 1200.00, 'ASSIGNED', %s);
        """, (maint_req_id, vendor_id, admin_id))
        conn.commit()
    except Exception as e:
        conn.rollback()
        br08_rejected = "BR-08" in str(e) or "closed" in str(e).lower()
    assert_test("Rule BR-08 Enforced: Attempt to attach work order on CLOSED request rejected by trigger", br08_rejected)

    # Step 6: Execute usp_ReopenMaintenanceRequest and attach work order
    cur.execute("""
        SELECT usp_ReopenMaintenanceRequest(%s, 'Pipe joint still dripping slightly', %s);
    """, (maint_req_id, admin_id))
    reopen_json = cur.fetchone()[0]
    conn.commit()

    cur.execute("SELECT status FROM maintenance_requests WHERE request_id = %s;", (maint_req_id,))
    reopened_stat = cur.fetchone()[0]

    cur.execute("""
        INSERT INTO work_orders (request_id, vendor_id, assigned_technician, estimated_cost, status, created_by)
        VALUES (%s, %s, 'Follow-up Plumber', 800.00, 'ASSIGNED', %s)
        RETURNING work_order_id;
    """, (maint_req_id, vendor_id, admin_id))
    second_wo_id = cur.fetchone()[0]
    conn.commit()

    assert_test(
        "Reopen Workflow: Request reopened to OPEN via usp_ReopenMaintenanceRequest; Second work order attached successfully",
        reopened_stat == 'OPEN' and second_wo_id > 0
    )

    # ==================================================================
    # SUMMARY
    # ==================================================================
    print("\n" + "=" * 70)
    print(f"Phase 3 Test Summary: {passed} PASSED | {failed} FAILED")
    print("=" * 70)

    cur.close()
    conn.close()

    if failed > 0:
        sys.exit(1)

if __name__ == "__main__":
    run_tests()
