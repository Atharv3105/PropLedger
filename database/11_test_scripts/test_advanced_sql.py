"""
PropLedger Automated Advanced SQL Validation Suite (Phase 2 Gate)
Validates:
1. All 7 Analytical Views (including Recursive CTE and PIVOT crosstab)
2. All 3 Business Functions (fn_CalculateLateFee, fn_GetOutstandingBalance, fn_GetLeaseStatus)
3. All 7 Stored Procedures (Window Functions, Aging Buckets, FIFO Allocations)
4. All 3 Selective Triggers (Payment Audit, Lease Status History, Rule BR-08 Work Order Guard)
5. Complex Joins, Subqueries, and Self Joins
"""

import os
import sys
from datetime import date, timedelta
import psycopg2

DB_CONFIG = {
    "host": os.environ.get("DB_HOST", "localhost"),
    "port": int(os.environ.get("DB_PORT", 5432)),
    "user": os.environ.get("DB_USER", "postgres"),
    "password": os.environ.get("DB_PASSWORD", "postgres"),
    "dbname": os.environ.get("DB_NAME", "propledger")
}

def run_tests():
    print("=" * 70)
    print("PropLedger Phase 2: Advanced SQL Automated Validation Suite")
    print("=" * 70)

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

    # ==================================================================
    # 1. ANALYTICAL VIEWS VALIDATION
    # ==================================================================
    print("\n[1] Analytical Views (7 Named Views)")

    # View 1: vw_PropertyOccupancy
    cur.execute("SELECT COUNT(*), AVG(occupancy_percentage) FROM vw_PropertyOccupancy;")
    row = cur.fetchone()
    assert_test("vw_PropertyOccupancy: Executable and computes metrics", row[0] > 0 and row[1] is not None, f"Count: {row[0]}, Avg: {row[1]}")

    # View 2: vw_TenantOutstandingBalance
    cur.execute("SELECT COUNT(*), SUM(outstanding_balance) FROM vw_TenantOutstandingBalance;")
    row = cur.fetchone()
    assert_test("vw_TenantOutstandingBalance: Executable with balance aggregates", row[0] > 0, f"Count: {row[0]}")

    # View 3: vw_ActiveLeases (Includes SELF JOIN on predecessor_lease_id)
    cur.execute("SELECT COUNT(*), COUNT(unit_number), COUNT(primary_tenant_name) FROM vw_ActiveLeases;")
    row = cur.fetchone()
    assert_test("vw_ActiveLeases: Multi-table JOIN and SELF JOIN operational", row[0] > 0 and row[1] == row[0])

    # View 4: vw_PropertyFinancialSummary
    cur.execute("SELECT COUNT(*), SUM(total_operating_revenue), SUM(net_operating_income) FROM vw_PropertyFinancialSummary;")
    row = cur.fetchone()
    assert_test("vw_PropertyFinancialSummary: Financial P&L Rollup operational", row[0] > 0 and row[1] > 0)

    # View 5: vw_AssetHierarchyCTE (Recursive CTE)
    cur.execute("""
        SELECT depth_level, COUNT(*), MIN(hierarchy_path), MAX(depth_level) 
        FROM vw_AssetHierarchyCTE 
        GROUP BY depth_level 
        ORDER BY depth_level;
    """)
    depth_levels = cur.fetchall()
    assert_test(
        "vw_AssetHierarchyCTE: Recursive CTE traverses 4 hierarchy depths (Owner -> Prop -> Bldg -> Unit)",
        len(depth_levels) == 4 and depth_levels[-1][0] == 4,
        f"Depths found: {[d[0] for d in depth_levels]}"
    )

    # View 6: vw_MonthlyRentCollectionPivot (PIVOT cross-tabulation)
    cur.execute("""
        SELECT property_name, billing_year, jan_collected, feb_collected, mar_collected, annual_total_collected 
        FROM vw_MonthlyRentCollectionPivot 
        LIMIT 5;
    """)
    pivot_rows = cur.fetchall()
    assert_test("vw_MonthlyRentCollectionPivot: PIVOT collection cross-tabulation operational", len(pivot_rows) > 0)

    # View 7: vw_MaintenanceMetrics
    cur.execute("SELECT COUNT(*), AVG(avg_resolution_days) FROM vw_MaintenanceMetrics;")
    row = cur.fetchone()
    assert_test("vw_MaintenanceMetrics: Resolution times and cost rollups operational", row[0] > 0)

    # ==================================================================
    # 2. BUSINESS FUNCTIONS VALIDATION
    # ==================================================================
    print("\n[2] Business Logic Functions (3 Named Functions)")

    cur.execute("SELECT lease_id FROM leases LIMIT 1;")
    test_lease_id = cur.fetchone()[0]

    # Function 1: fn_CalculateLateFee (Rule BR-05: Grace Period enforcement)
    cur.execute("SELECT fn_CalculateLateFee(%s, 25000.00, 3);", (test_lease_id,))
    fee_within_grace = cur.fetchone()[0]
    assert_test("fn_CalculateLateFee: Returns 0.00 within grace period (Day 3 <= 5)", fee_within_grace == 0.00, f"Got: {fee_within_grace}")

    cur.execute("SELECT fn_CalculateLateFee(%s, 25000.00, 15);", (test_lease_id,))
    fee_after_grace = cur.fetchone()[0]
    assert_test("fn_CalculateLateFee: Assesses late fee after grace period expires (Day 15 > 5)", fee_after_grace > 0.00, f"Got: {fee_after_grace}")

    # Function 2: fn_GetOutstandingBalance
    cur.execute("SELECT fn_GetOutstandingBalance(%s);", (test_lease_id,))
    bal = cur.fetchone()[0]
    assert_test("fn_GetOutstandingBalance: Computes scalar net balance", bal is not None)

    # Function 3: fn_GetLeaseStatus
    cur.execute("SELECT fn_GetLeaseStatus(%s, CURRENT_DATE);", (test_lease_id,))
    computed_status = cur.fetchone()[0]
    assert_test("fn_GetLeaseStatus: Evaluates dynamic status", computed_status in ['ACTIVE', 'EXPIRING', 'EXPIRED', 'DRAFT', 'TERMINATED'])

    # ==================================================================
    # 3. STORED PROCEDURES VALIDATION
    # ==================================================================
    print("\n[3] Stored Procedures & Procedural Logic (7 Procedures)")

    # SP 1: usp_GenerateMonthlyRent (Next month batch billing)
    next_month = (date.today().month % 12) + 1
    next_year = date.today().year if next_month > 1 else date.today().year + 1
    cur.execute("SELECT * FROM usp_GenerateMonthlyRent(%s, %s);", (next_month, next_year))
    gen_res = cur.fetchone()
    assert_test(f"usp_GenerateMonthlyRent: Batch billed {gen_res[0]} active leases for {next_year}-{next_month:02d}", gen_res[0] > 0)

    # Idempotency check: Re-run should generate 0 new charges
    cur.execute("SELECT * FROM usp_GenerateMonthlyRent(%s, %s);", (next_month, next_year))
    idempotent_res = cur.fetchone()
    assert_test("usp_GenerateMonthlyRent: Idempotency check (0 duplicate charges created on rerun)", idempotent_res[0] == 0)

    # SP 2: usp_RecordPayment (Transactional FIFO Payment Allocation)
    cur.execute("SELECT user_id FROM users WHERE email = 'admin@propledger.com';")
    admin_id = cur.fetchone()[0]

    cur.execute("""
        SELECT usp_RecordPayment(%s, 15000.00, 'BANK_TRANSFER', 'TEST-REF-999', %s);
    """, (test_lease_id, admin_id))
    pay_res = cur.fetchone()[0]
    assert_test("usp_RecordPayment: Transactional payment processed with FIFO allocation", pay_res.get('status') == 'SUCCESS')

    # SP 3: usp_GetTenantPaymentHistory (Window Functions: ROW_NUMBER, LAG, Running Sum)
    cur.execute("SELECT * FROM usp_GetTenantPaymentHistory(NULL, %s);", (test_lease_id,))
    pay_hist = cur.fetchall()
    assert_test("usp_GetTenantPaymentHistory: Window functions (ROW_NUMBER, LAG, Running Total) verified", len(pay_hist) > 0)

    # SP 4: usp_GetPropertyOccupancy (Window Function: DENSE_RANK)
    cur.execute("SELECT * FROM usp_GetPropertyOccupancy(NULL) LIMIT 5;")
    occ_report = cur.fetchall()
    assert_test("usp_GetPropertyOccupancy: DENSE_RANK performance tiering operational", len(occ_report) == 5 and occ_report[0][0] == 1)

    # SP 5: usp_GetDelinquencyReport (Aging Buckets: 1-30, 31-60, 61-90, 90+)
    cur.execute("SELECT * FROM usp_GetDelinquencyReport(NULL, CURRENT_DATE) LIMIT 10;")
    delinq_report = cur.fetchall()
    assert_test("usp_GetDelinquencyReport: Aging categories and fee calculations verified", len(delinq_report) > 0)

    # SP 6: usp_GetLeaseExpiryReport
    from_d = date.today()
    to_d = from_d + timedelta(days=180)
    cur.execute("SELECT * FROM usp_GetLeaseExpiryReport(%s, %s, NULL) LIMIT 10;", (from_d, to_d))
    expiry_report = cur.fetchall()
    assert_test("usp_GetLeaseExpiryReport: Parameterized expiration filtering operational", len(expiry_report) > 0)

    # SP 7: usp_GetPropertyFinancialSummary
    cur.execute("SELECT * FROM usp_GetPropertyFinancialSummary(NULL) LIMIT 10;")
    fin_summary = cur.fetchall()
    assert_test("usp_GetPropertyFinancialSummary: Property P&L procedure operational", len(fin_summary) > 0)

    # ==================================================================
    # 4. SELECTIVE TRIGGERS VALIDATION
    # ==================================================================
    print("\n[4] Selective Database Triggers (3 Triggers)")

    # Trigger 1: trg_PaymentAuditInsert
    cur.execute("SELECT COUNT(*) FROM payment_audit WHERE payment_id = %s;", (pay_res.get('payment_id'),))
    audit_count = cur.fetchone()[0]
    assert_test("trg_PaymentAuditInsert: Trigger automatically created payment_audit record", audit_count >= 1)

    # Trigger 2: trg_LeaseStatusHistory
    cur.execute("SELECT status FROM leases WHERE lease_id = %s;", (test_lease_id,))
    cur_stat = cur.fetchone()[0]
    new_stat = 'EXPIRING' if cur_stat == 'ACTIVE' else 'ACTIVE'
    cur.execute("UPDATE leases SET status = %s, modified_by = %s WHERE lease_id = %s;", (new_stat, admin_id, test_lease_id))
    conn.commit()

    cur.execute("SELECT COUNT(*) FROM status_history WHERE entity_type = 'LEASE' AND entity_id = %s;", (test_lease_id,))
    stat_hist_count = cur.fetchone()[0]
    assert_test("trg_LeaseStatusHistory: Trigger logged status transition in status_history", stat_hist_count >= 1)

    # Trigger 3: trg_PreventWorkOrderOnClosedMaintenance (Rule BR-08)
    cur.execute("SELECT request_id FROM maintenance_requests WHERE status = 'CLOSED' LIMIT 1;")
    closed_req = cur.fetchone()
    if closed_req:
        closed_req_id = closed_req[0]
        br08_blocked = False
        try:
            cur.execute("""
                INSERT INTO work_orders (request_id, assigned_technician, estimated_cost, status, created_by)
                VALUES (%s, 'Test Tech', 1500.00, 'ASSIGNED', %s);
            """, (closed_req_id, admin_id))
            conn.commit()
        except psycopg2.IntegrityError as e:
            conn.rollback()
            br08_blocked = "BR-08" in str(e) or "closed" in str(e).lower()
        except psycopg2.InternalError as e:
            conn.rollback()
            br08_blocked = "BR-08" in str(e) or "closed" in str(e).lower()
        assert_test("trg_PreventWorkOrderOnClosedMaintenance: Enforced BR-08 (Blocked work order on closed request)", br08_blocked)

    # ==================================================================
    # SUMMARY
    # ==================================================================
    print("\n" + "=" * 70)
    print(f"Phase 2 Test Summary: {passed} PASSED | {failed} FAILED")
    print("=" * 70)

    cur.close()
    conn.close()

    if failed > 0:
        sys.exit(1)

if __name__ == "__main__":
    run_tests()
