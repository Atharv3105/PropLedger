"""
PropLedger Unified Cloud Database Provisioning & Seed Script
Deploys all schema, tables, constraints, analytical views, stored procedures,
triggers, and synthetic seed data to any PostgreSQL instance (Railway, Render, Supabase, Neon, etc.).

Usage:
    python database/deploy_to_cloud_db.py "postgresql://user:pass@host:port/dbname"
Or:
    $env:DATABASE_URL="postgresql://user:pass@host:port/dbname"
    python database/deploy_to_cloud_db.py
"""

import os
import sys
import psycopg2

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def get_db_connection(dsn_arg: str = None):
    raw_url = dsn_arg or os.environ.get("DATABASE_URL") or os.environ.get("POSTGRES_URL")
    if not raw_url:
        print("[ERROR] No database URL provided!")
        print("Usage: python database/deploy_to_cloud_db.py <DATABASE_URL>")
        print("Or set the DATABASE_URL environment variable.")
        sys.exit(1)
    
    if raw_url.startswith("postgres://"):
        raw_url = raw_url.replace("postgres://", "postgresql://", 1)
    
    print(f"Connecting to target database...")
    try:
        conn = psycopg2.connect(dsn=raw_url)
        conn.autocommit = True
        return conn, raw_url
    except Exception as e:
        print(f"[ERROR] Could not connect to database: {e}")
        sys.exit(1)

def run_script_list(conn, file_list, phase_title):
    print("\n" + "=" * 70)
    print(f"--> {phase_title}")
    print("=" * 70)
    cur = conn.cursor()
    for rel_path in file_list:
        full_path = os.path.join(BASE_DIR, rel_path)
        if not os.path.exists(full_path):
            print(f"[ERROR] Missing file: {full_path}")
            sys.exit(1)
        print(f"  Executing: {rel_path} ...", end=" ", flush=True)
        with open(full_path, "r", encoding="utf-8") as f:
            sql = f.read()
        try:
            cur.execute(sql)
            print("[OK]")
        except Exception as e:
            print(f"\n[FAILED] Error in {rel_path}:\n{e}")
            sys.exit(1)
    cur.close()

def main():
    dsn_arg = sys.argv[1] if len(sys.argv) > 1 else None
    conn, raw_url = get_db_connection(dsn_arg)

    # Phase 1: Core Tables & Constraints
    phase1_files = [
        os.path.join("01_schema", "01_extensions_and_types.sql"),
        os.path.join("02_tables", "01_auth_tables.sql"),
        os.path.join("02_tables", "02_property_tables.sql"),
        os.path.join("02_tables", "03_tenant_tables.sql"),
        os.path.join("02_tables", "04_lease_tables.sql"),
        os.path.join("02_tables", "05_billing_tables.sql"),
        os.path.join("02_tables", "06_maintenance_tables.sql"),
        os.path.join("02_tables", "07_accounting_tables.sql"),
        os.path.join("02_tables", "08_history_tables.sql"),
        os.path.join("03_constraints", "01_foreign_keys.sql"),
        os.path.join("03_constraints", "02_check_constraints.sql"),
        os.path.join("09_indexes", "01_baseline_indexes.sql"),
        os.path.join("04_seed_data", "01_system_lookups.sql")
    ]
    run_script_list(conn, phase1_files, "PHASE 1: Core Schema, 36 Tables, Constraints & System Lookups")

    # Phase 2: Views, Functions, Stored Procedures, Triggers
    phase2_files = [
        os.path.join("06_functions", "01_fn_CalculateLateFee.sql"),
        os.path.join("06_functions", "02_fn_GetOutstandingBalance.sql"),
        os.path.join("06_functions", "03_fn_GetLeaseStatus.sql"),
        os.path.join("05_views", "01_vw_PropertyOccupancy.sql"),
        os.path.join("05_views", "02_vw_TenantOutstandingBalance.sql"),
        os.path.join("05_views", "03_vw_ActiveLeases.sql"),
        os.path.join("05_views", "04_vw_PropertyFinancialSummary.sql"),
        os.path.join("05_views", "05_vw_AssetHierarchyCTE.sql"),
        os.path.join("05_views", "06_vw_MonthlyRentCollectionPivot.sql"),
        os.path.join("05_views", "07_vw_MaintenanceMetrics.sql"),
        os.path.join("07_stored_procedures", "01_usp_GenerateMonthlyRent.sql"),
        os.path.join("07_stored_procedures", "02_usp_RecordPayment.sql"),
        os.path.join("07_stored_procedures", "03_usp_GetTenantPaymentHistory.sql"),
        os.path.join("07_stored_procedures", "04_usp_GetPropertyOccupancy.sql"),
        os.path.join("07_stored_procedures", "05_usp_GetDelinquencyReport.sql"),
        os.path.join("07_stored_procedures", "06_usp_GetLeaseExpiryReport.sql"),
        os.path.join("07_stored_procedures", "07_usp_GetPropertyFinancialSummary.sql"),
        os.path.join("08_triggers", "01_trg_PaymentAuditInsert.sql"),
        os.path.join("08_triggers", "02_trg_LeaseStatusHistory.sql"),
        os.path.join("08_triggers", "03_trg_PreventWorkOrderOnClosedMaintenance.sql")
    ]
    run_script_list(conn, phase2_files, "PHASE 2: 7 Analytical Views, Functions, SPs & Audit Triggers")

    # Phase 3: Workflow Stored Procedures
    phase3_files = [
        os.path.join("07_stored_procedures", "08_usp_RenewLease.sql"),
        os.path.join("07_stored_procedures", "09_usp_EscalateToCollection.sql"),
        os.path.join("07_stored_procedures", "10_usp_ReopenMaintenanceRequest.sql")
    ]
    run_script_list(conn, phase3_files, "PHASE 3: Business Workflow Stored Procedures")

    # Phase 4: Seed Data (Demo Users, Properties, Leases, Maintenance, Financials)
    print("\n" + "=" * 70)
    print("--> PHASE 4: Synthetic Enterprise Seed Data (500 Properties & Demo Users)")
    print("=" * 70)
    conn.close()
    
    # Run seed data generator with DATABASE_URL in environment
    os.environ["DATABASE_URL"] = raw_url
    sys.path.insert(0, os.path.join(BASE_DIR, "04_seed_data"))
    from generate_seed_data import run_seed
    run_seed()

    # Final Verification
    verify_conn = psycopg2.connect(dsn=raw_url)
    vcur = verify_conn.cursor()
    vcur.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public' AND table_type='BASE TABLE';")
    tables = vcur.fetchone()[0]
    vcur.execute("SELECT COUNT(*) FROM information_schema.views WHERE table_schema='public';")
    views = vcur.fetchone()[0]
    vcur.execute("SELECT COUNT(*) FROM users;")
    users = vcur.fetchone()[0]
    vcur.execute("SELECT COUNT(*) FROM properties;")
    properties = vcur.fetchone()[0]
    vcur.close()
    verify_conn.close()

    print("\n" + "=" * 70)
    print("CLOUD DATABASE PROVISIONING COMPLETE!")
    print(f"  Base Tables : {tables}")
    print(f"  Views       : {views}")
    print(f"  Users       : {users} (Admin, Manager, Accountant, Owner, Tenant, Staff)")
    print(f"  Properties  : {properties}")
    print("=" * 70)
    print("\nAll endpoints and role-aware dashboards are now fully supported.")

if __name__ == "__main__":
    main()
