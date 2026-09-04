#!/usr/bin/env python3
"""
PropLedger Phase 8: Performance Benchmark Harness (PL-142)
Executes before/after EXPLAIN (ANALYZE, BUFFERS) benchmarks on 5 operational queries.
Measures Execution Time, Planning Time, Shared Buffer Hits/Reads, and Plan Nodes.
"""

import os
import sys
import json
import time
import psycopg2

DB_PARAMS = {
    'dbname': 'propledger',
    'user': 'postgres',
    'password': 'postgres',
    'host': 'localhost',
    'port': 5432
}

BENCHMARK_DIR = 'D:/PropLedger/performance/benchmarks'
BEFORE_DIR = 'D:/PropLedger/performance/before'
AFTER_DIR = 'D:/PropLedger/performance/after'
INDEXES_SQL = 'D:/PropLedger/database/12_performance/02_optimized_indexes.sql'

QUERIES = [
    ('01_occupancy', '01_occupancy.sql', 'PL-132: Property Occupancy & Portfolio Aggregation'),
    ('02_payment_history', '02_payment_history.sql', 'PL-133: Large Payment History Ledger & Running Balances'),
    ('03_rent_collection', '03_rent_collection.sql', 'PL-134: Monthly Rent Collection Aggregation'),
    ('04_delinquency', '04_delinquency.sql', 'PL-135: Delinquency Aging Report under Heavy Volume'),
    ('05_financial_summary', '05_financial_summary.sql', 'PL-136: Multi-Year Property Financial Performance Summary')
]

OPTIMIZED_INDEX_NAMES = [
    'idx_leases_active_units',
    'idx_units_building_status_cov',
    'idx_payments_lease_date_id_cov',
    'idx_rent_charges_year_month_cov',
    'idx_rent_charges_delinquent_partial',
    'idx_expenses_date_prop_cat_cov',
    'idx_rent_charges_due_date_cov'
]

def drop_optimized_indexes(conn):
    print("Dropping Phase 8 optimized indexes (setting baseline BEFORE state)...")
    cur = conn.cursor()
    for idx in OPTIMIZED_INDEX_NAMES:
        cur.execute(f"DROP INDEX IF EXISTS {idx};")
    conn.commit()
    cur.execute("ANALYZE leases; ANALYZE units; ANALYZE payments; ANALYZE rent_charges; ANALYZE expenses;")
    conn.commit()
    print("Baseline state set.")

def apply_optimized_indexes(conn):
    print("Applying Phase 8 optimized indexes (setting AFTER state)...")
    cur = conn.cursor()
    with open(INDEXES_SQL, 'r', encoding='utf-8') as f:
        sql = f.read()
    cur.execute(sql)
    conn.commit()
    print("Optimized indexes applied successfully.")

def extract_buffer_stats(plan_node):
    hit = plan_node.get('Shared Hit Blocks', 0)
    read = plan_node.get('Shared Read Blocks', 0)
    dirtied = plan_node.get('Shared Dirtied Blocks', 0)
    
    for subplan in plan_node.get('Plans', []):
        sub_hit, sub_read, sub_dirtied = extract_buffer_stats(subplan)
        hit += sub_hit
        read += sub_read
        dirtied += sub_dirtied
        
    return hit, read, dirtied

def benchmark_query(conn, sql, runs=3):
    cur = conn.cursor()
    exec_times = []
    plan_times = []
    json_plan = None
    
    for _ in range(runs):
        cur.execute(f"EXPLAIN (ANALYZE, BUFFERS, VERBOSE, FORMAT JSON) {sql}")
        res = cur.fetchone()[0]
        exec_times.append(res[0]['Execution Time'])
        plan_times.append(res[0]['Planning Time'])
        json_plan = res[0]
        
    cur.execute(f"EXPLAIN (ANALYZE, BUFFERS, VERBOSE) {sql}")
    raw_text_lines = [row[0] for row in cur.fetchall()]
    raw_text = "\n".join(raw_text_lines)
    
    root_node = json_plan['Plan']
    total_hit, total_read, total_dirtied = extract_buffer_stats(root_node)
    
    avg_exec_time = sum(exec_times) / len(exec_times)
    avg_plan_time = sum(plan_times) / len(plan_times)
    
    return {
        'avg_execution_time_ms': round(avg_exec_time, 2),
        'avg_planning_time_ms': round(avg_plan_time, 2),
        'shared_hit_blocks': total_hit,
        'shared_read_blocks': total_read,
        'total_shared_blocks': total_hit + total_read,
        'root_node_type': root_node.get('Node Type'),
        'raw_text_plan': raw_text,
        'json_plan': json_plan
    }

def main():
    conn = psycopg2.connect(**DB_PARAMS)
    conn.autocommit = True
    
    # 1. BASELINE BENCHMARKS (BEFORE)
    drop_optimized_indexes(conn)
    print("\n" + "="*80)
    print("RUNNING BASELINE BENCHMARKS (BEFORE OPTIMIZATION)")
    print("="*80)
    
    before_metrics = {}
    for q_id, q_file, q_desc in QUERIES:
        q_path = os.path.join(BENCHMARK_DIR, q_file)
        with open(q_path, 'r', encoding='utf-8') as f:
            sql = f.read()
        print(f"Benchmarking {q_desc}...")
        m = benchmark_query(conn, sql, runs=3)
        before_metrics[q_id] = m
        
        out_path = os.path.join(BEFORE_DIR, f"{q_id}_before.txt")
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(m['raw_text_plan'])
        print(f"  -> Exec Time: {m['avg_execution_time_ms']} ms | Blocks: {m['total_shared_blocks']} | Root: {m['root_node_type']}")
        
    # 2. APPLY OPTIMIZED INDEXES (AFTER)
    print("\n" + "="*80)
    print("APPLYING INDEXES & RUNNING OPTIMIZED BENCHMARKS (AFTER OPTIMIZATION)")
    print("="*80)
    apply_optimized_indexes(conn)
    
    after_metrics = {}
    for q_id, q_file, q_desc in QUERIES:
        q_path = os.path.join(BENCHMARK_DIR, q_file)
        with open(q_path, 'r', encoding='utf-8') as f:
            sql = f.read()
        print(f"Benchmarking {q_desc}...")
        m = benchmark_query(conn, sql, runs=3)
        after_metrics[q_id] = m
        
        out_path = os.path.join(AFTER_DIR, f"{q_id}_after.txt")
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(m['raw_text_plan'])
        print(f"  -> Exec Time: {m['avg_execution_time_ms']} ms | Blocks: {m['total_shared_blocks']} | Root: {m['root_node_type']}")

    # 3. COMPARATIVE ANALYSIS
    print("\n" + "="*115)
    header = f"{'Case Study':<25} | {'Metric':<18} | {'Before':<14} | {'After':<14} | {'Delta':<14} | {'Gain / Speedup':<18}"
    print(header)
    print("-" * 115)
    
    summary = []
    for q_id, q_file, q_desc in QUERIES:
        b = before_metrics[q_id]
        a = after_metrics[q_id]
        
        t_b = b['avg_execution_time_ms']
        t_a = a['avg_execution_time_ms']
        t_diff = t_b - t_a
        pct_time = ((t_b - t_a) / t_b * 100) if t_b > 0 else 0
        speedup = (t_b / t_a) if t_a > 0 else 1.0
        
        blk_b = b['total_shared_blocks']
        blk_a = a['total_shared_blocks']
        blk_diff = blk_b - blk_a
        pct_blk = ((blk_b - blk_a) / blk_b * 100) if blk_b > 0 else 0
        
        row1 = f"{q_id:<25} | {'Exec Time':<18} | {t_b:>11.2f} ms | {t_a:>11.2f} ms | {-t_diff:>11.2f} ms | {speedup:>5.1f}x ({pct_time:.1f}% faster)"
        row2 = f"{q_id:<25} | {'Shared Buffers':<18} | {blk_b:>14,} | {blk_a:>14,} | {-blk_diff:>14,} | {pct_blk:.1f}% I/O saved"
        print(row1)
        print(row2)
        print("-" * 115)
        
        summary.append({
            'case_study_id': q_id,
            'description': q_desc,
            'before': {
                'execution_time_ms': t_b,
                'planning_time_ms': b['avg_planning_time_ms'],
                'shared_buffer_blocks': blk_b,
                'root_node': b['root_node_type']
            },
            'after': {
                'execution_time_ms': t_a,
                'planning_time_ms': a['avg_planning_time_ms'],
                'shared_buffer_blocks': blk_a,
                'root_node': a['root_node_type']
            },
            'speedup_factor': round(speedup, 2),
            'execution_time_reduction_pct': round(pct_time, 2),
            'buffer_io_reduction_pct': round(pct_blk, 2)
        })
        
    results_path = os.path.join(BENCHMARK_DIR, 'benchmark_results.json')
    with open(results_path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)
    print(f"\nSaved full comparative results to {results_path}")
    
    conn.close()

if __name__ == '__main__':
    main()
