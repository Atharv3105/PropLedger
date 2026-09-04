"""
PropLedger Advanced SQL Deployment Runner
Deploys all analytical views, functions, stored procedures, and triggers.
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

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SQL_FILES = [
    # 1. Functions first (needed by views and procedures)
    os.path.join("06_functions", "01_fn_CalculateLateFee.sql"),
    os.path.join("06_functions", "02_fn_GetOutstandingBalance.sql"),
    os.path.join("06_functions", "03_fn_GetLeaseStatus.sql"),

    # 2. Views
    os.path.join("05_views", "01_vw_PropertyOccupancy.sql"),
    os.path.join("05_views", "02_vw_TenantOutstandingBalance.sql"),
    os.path.join("05_views", "03_vw_ActiveLeases.sql"),
    os.path.join("05_views", "04_vw_PropertyFinancialSummary.sql"),
    os.path.join("05_views", "05_vw_AssetHierarchyCTE.sql"),
    os.path.join("05_views", "06_vw_MonthlyRentCollectionPivot.sql"),
    os.path.join("05_views", "07_vw_MaintenanceMetrics.sql"),

    # 3. Stored Procedures
    os.path.join("07_stored_procedures", "01_usp_GenerateMonthlyRent.sql"),
    os.path.join("07_stored_procedures", "02_usp_RecordPayment.sql"),
    os.path.join("07_stored_procedures", "03_usp_GetTenantPaymentHistory.sql"),
    os.path.join("07_stored_procedures", "04_usp_GetPropertyOccupancy.sql"),
    os.path.join("07_stored_procedures", "05_usp_GetDelinquencyReport.sql"),
    os.path.join("07_stored_procedures", "06_usp_GetLeaseExpiryReport.sql"),
    os.path.join("07_stored_procedures", "07_usp_GetPropertyFinancialSummary.sql"),

    # 4. Triggers
    os.path.join("08_triggers", "01_trg_PaymentAuditInsert.sql"),
    os.path.join("08_triggers", "02_trg_LeaseStatusHistory.sql"),
    os.path.join("08_triggers", "03_trg_PreventWorkOrderOnClosedMaintenance.sql")
]

def deploy():
    print("=" * 65)
    print("PropLedger Phase 2: Advanced SQL Deployment")
    print(f"Target Database: {DB_CONFIG['dbname']} on {DB_CONFIG['host']}:{DB_CONFIG['port']}")
    print("=" * 65)

    db_url = os.environ.get("DATABASE_URL") or os.environ.get("POSTGRES_URL")
    if db_url:
        if db_url.startswith("postgres://"):
            db_url = db_url.replace("postgres://", "postgresql://", 1)
        conn = psycopg2.connect(dsn=db_url)
    else:
        conn = psycopg2.connect(**DB_CONFIG)
    conn.autocommit = True
    cur = conn.cursor()

    for rel_path in SQL_FILES:
        full_path = os.path.join(BASE_DIR, rel_path)
        print(f"--> Deploying: {rel_path} ...", end=" ", flush=True)
        with open(full_path, "r", encoding="utf-8") as f:
            sql = f.read()

        try:
            cur.execute(sql)
            print("[OK]")
        except Exception as e:
            print(f"\n[FAILED] Error in {rel_path}:\n{e}")
            sys.exit(1)

    # Validate deployed views
    cur.execute("""
        SELECT COUNT(*) 
        FROM information_schema.views 
        WHERE table_schema = 'public';
    """)
    view_count = cur.fetchone()[0]

    # Validate deployed routines (functions & procedures)
    cur.execute("""
        SELECT COUNT(*) 
        FROM information_schema.routines 
        WHERE routine_schema = 'public';
    """)
    routine_count = cur.fetchone()[0]

    # Validate triggers
    cur.execute("""
        SELECT COUNT(*) 
        FROM information_schema.triggers 
        WHERE trigger_schema = 'public';
    """)
    trigger_count = cur.fetchone()[0]

    print("=" * 65)
    print(f"Phase 2 Deployment Complete! Views: {view_count} | Routines: {routine_count} | Triggers: {trigger_count}")
    print("=" * 65)

    cur.close()
    conn.close()

if __name__ == "__main__":
    deploy()
