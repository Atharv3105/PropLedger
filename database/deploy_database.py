"""
PropLedger Database Migration & Deployment Runner
Executes modular DDL and seed scripts in strict order.
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

SCRIPTS_ORDER = [
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

def deploy():
    print("=" * 60)
    print("PropLedger Database Deployment")
    print(f"Target: {DB_CONFIG['dbname']} on {DB_CONFIG['host']}:{DB_CONFIG['port']}")
    print("=" * 60)

    db_url = os.environ.get("DATABASE_URL") or os.environ.get("POSTGRES_URL")
    try:
        if db_url:
            if db_url.startswith("postgres://"):
                db_url = db_url.replace("postgres://", "postgresql://", 1)
            conn = psycopg2.connect(dsn=db_url)
        else:
            conn = psycopg2.connect(**DB_CONFIG)
        conn.autocommit = True
        cur = conn.cursor()
    except Exception as e:
        print(f"[ERROR] Failed to connect to database: {e}")
        sys.exit(1)

    for rel_path in SCRIPTS_ORDER:
        full_path = os.path.join(BASE_DIR, rel_path)
        if not os.path.exists(full_path):
            print(f"[ERROR] Script not found: {full_path}")
            sys.exit(1)

        print(f"--> Executing: {rel_path} ...", end=" ", flush=True)
        with open(full_path, "r", encoding="utf-8") as f:
            sql = f.read()

        try:
            cur.execute(sql)
            print("[OK]")
        except Exception as e:
            print(f"\n[FAILED] Error in {rel_path}:\n{e}")
            sys.exit(1)

    # Validate deployed tables
    cur.execute("""
        SELECT COUNT(*) 
        FROM information_schema.tables 
        WHERE table_schema = 'public' AND table_type = 'BASE TABLE';
    """)
    table_count = cur.fetchone()[0]

    # Validate foreign keys
    cur.execute("""
        SELECT COUNT(*) 
        FROM information_schema.table_constraints 
        WHERE constraint_type = 'FOREIGN KEY' AND table_schema = 'public';
    """)
    fk_count = cur.fetchone()[0]

    # Validate check constraints
    cur.execute("""
        SELECT COUNT(*) 
        FROM information_schema.table_constraints 
        WHERE constraint_type = 'CHECK' AND table_schema = 'public';
    """)
    chk_count = cur.fetchone()[0]

    print("=" * 60)
    print(f"Deployment Complete! Deployed Tables: {table_count} | FKs: {fk_count} | Check Constraints: {chk_count}")
    print("=" * 60)

    cur.close()
    conn.close()

if __name__ == "__main__":
    deploy()
