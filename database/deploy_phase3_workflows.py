"""
PropLedger Phase 3 Workflow Procedures Deployment Runner
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
    os.path.join("07_stored_procedures", "08_usp_RenewLease.sql"),
    os.path.join("07_stored_procedures", "09_usp_EscalateToCollection.sql"),
    os.path.join("07_stored_procedures", "10_usp_ReopenMaintenanceRequest.sql")
]

def deploy():
    print("=" * 65)
    print("PropLedger Phase 3: Business Workflow Procedures Deployment")
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

    print("=" * 65)
    print("Phase 3 Workflow Procedures Deployed Successfully!")
    print("=" * 65)

    cur.close()
    conn.close()

if __name__ == "__main__":
    deploy()
