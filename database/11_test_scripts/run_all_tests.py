#!/usr/bin/env python3
"""
PropLedger Database Test Runner (PL-140)
Executes all SQL constraint, trigger, transaction, and stored procedure test scripts.
"""

import os
import sys
import psycopg2

DB_PARAMS = {
    'dbname': 'propledger',
    'user': 'postgres',
    'password': 'postgres',
    'host': 'localhost',
    'port': 5432
}

TEST_FILES = [
    '01_constraints_and_triggers.sql',
    '02_stored_procedure_atomicity.sql'
]

def run_db_tests():
    conn = psycopg2.connect(**DB_PARAMS)
    conn.autocommit = True
    cur = conn.cursor()
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    passed = 0
    failed = 0
    
    print("=" * 80)
    print("PROPLEDGER DATABASE TEST RUNNER — CONSTRAINTS, TRIGGERS & SP ATOMICITY")
    print("=" * 80)
    
    for fname in TEST_FILES:
        fpath = os.path.join(script_dir, fname)
        if not os.path.exists(fpath):
            print(f"[ERROR] Test script not found: {fpath}")
            failed += 1
            continue
            
        print(f"\nExecuting: {fname}...")
        with open(fpath, 'r', encoding='utf-8') as f:
            sql = f.read()
            
        try:
            cur.execute(sql)
            # Print database notices
            for notice in conn.notices:
                print(f"  {notice.strip()}")
            del conn.notices[:]
            print(f"[PASS] {fname} completed successfully.")
            passed += 1
        except Exception as e:
            print(f"[FAIL] {fname} failed with error: {e}")
            failed += 1
            
    conn.close()
    
    print("\n" + "=" * 80)
    print(f"RESULTS: {passed} PASSED | {failed} FAILED | TOTAL: {passed + failed}")
    print("=" * 80)
    
    if failed > 0:
        sys.exit(1)

if __name__ == '__main__':
    run_db_tests()
