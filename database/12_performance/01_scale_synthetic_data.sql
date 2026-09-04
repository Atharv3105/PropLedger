-- ======================================================================
-- PropLedger Phase 8: Synthetic Dataset Scaling Script
-- Target: PostgreSQL 16
-- Purpose: Scale financial transactions to >100,000 records for
--          realistic execution plan profiling and performance benchmarks.
-- ======================================================================

BEGIN;

-- ----------------------------------------------------------------------
-- 1. Scale Rent Charges (2022 to 2025 across all leases)
-- ----------------------------------------------------------------------
INSERT INTO rent_charges (
    lease_id, 
    billing_month, 
    billing_year, 
    charge_date, 
    due_date, 
    charge_amount, 
    amount_paid, 
    status, 
    created_at, 
    created_by
)
SELECT 
    l.lease_id,
    m.month,
    y.year,
    make_date(y.year, m.month, 1),
    make_date(y.year, m.month, 5),
    l.monthly_rent,
    CASE 
        WHEN (l.lease_id + m.month + y.year) % 20 = 0 THEN 0.00                              -- 5% overdue
        WHEN (l.lease_id + m.month + y.year) % 20 = 1 THEN ROUND(l.monthly_rent * 0.50, 2)  -- 5% partially paid
        ELSE l.monthly_rent                                                                   -- 90% fully paid
    END AS amount_paid,
    CASE 
        WHEN (l.lease_id + m.month + y.year) % 20 = 0 THEN 'Overdue'
        WHEN (l.lease_id + m.month + y.year) % 20 = 1 THEN 'PartiallyPaid'
        ELSE 'Paid'
    END AS status,
    CURRENT_TIMESTAMP - (INTERVAL '1 month' * ((2026 - y.year) * 12 + (6 - m.month))),
    32
FROM leases l
CROSS JOIN generate_series(2022, 2025) AS y(year)
CROSS JOIN generate_series(1, 12) AS m(month)
WHERE NOT EXISTS (
    SELECT 1 FROM rent_charges rc 
    WHERE rc.lease_id = l.lease_id 
      AND rc.billing_year = y.year 
      AND rc.billing_month = m.month
);

-- ----------------------------------------------------------------------
-- 2. Scale Payments & Payment Audit for Paid / PartiallyPaid Charges
-- ----------------------------------------------------------------------
-- Temporarily disable payment audit trigger for bulk performance
ALTER TABLE payments DISABLE TRIGGER trg_paymentauditinsert;

INSERT INTO payments (
    lease_id,
    payment_date,
    amount,
    payment_method,
    reference_number,
    notes,
    recorded_by,
    created_at
)
SELECT 
    rc.lease_id,
    rc.due_date + CAST(((rc.charge_id % 4) - 1) AS integer),
    rc.amount_paid,
    CASE (rc.charge_id % 4)
        WHEN 0 THEN 'ACH'
        WHEN 1 THEN 'CreditCard'
        WHEN 2 THEN 'Check'
        ELSE 'BankTransfer'
    END,
    'AUTO-RC-' || rc.charge_id,
    'Automated batch rent payment for charge ' || rc.charge_id,
    32,
    rc.due_date::timestamp with time zone
FROM rent_charges rc
WHERE rc.amount_paid > 0
  AND NOT EXISTS (
      SELECT 1 FROM payments p 
      WHERE p.reference_number = 'AUTO-RC-' || rc.charge_id
  );

-- Re-enable trigger
ALTER TABLE payments ENABLE TRIGGER trg_paymentauditinsert;

-- Populate payment_audit in set-based operation for scaled rows
INSERT INTO payment_audit (
    payment_id,
    lease_id,
    action,
    payment_amount,
    recorded_by,
    recorded_at,
    client_ip,
    audit_notes
)
SELECT 
    p.payment_id,
    p.lease_id,
    'RECORDED',
    p.amount,
    p.recorded_by,
    p.created_at,
    '127.0.0.1',
    'Auto-audited payment transaction ref: ' || p.reference_number
FROM payments p
WHERE p.reference_number LIKE 'AUTO-RC-%'
  AND NOT EXISTS (
      SELECT 1 FROM payment_audit pa 
      WHERE pa.payment_id = p.payment_id
  );

-- ----------------------------------------------------------------------
-- 3. Populate Payment Allocations
-- ----------------------------------------------------------------------
INSERT INTO payment_allocations (
    payment_id,
    charge_id,
    allocated_amount,
    allocated_at
)
SELECT 
    p.payment_id,
    CAST(SUBSTRING(p.reference_number FROM 9) AS bigint) AS charge_id,
    p.amount,
    p.payment_date::timestamp with time zone
FROM payments p
WHERE p.reference_number LIKE 'AUTO-RC-%'
  AND NOT EXISTS (
      SELECT 1 FROM payment_allocations pa 
      WHERE pa.payment_id = p.payment_id
  );

-- ----------------------------------------------------------------------
-- 4. Scale Property Expenses (2022 to 2025 across all 501 properties)
-- ----------------------------------------------------------------------
INSERT INTO expenses (
    property_id,
    vendor_id,
    category,
    amount,
    expense_date,
    description,
    created_at,
    created_by
)
SELECT 
    p.property_id,
    (p.property_id % 20) + 1,
    CASE (p.property_id + m.month + y.year) % 6
        WHEN 0 THEN 'Utilities'
        WHEN 1 THEN 'Repairs'
        WHEN 2 THEN 'Landscaping'
        WHEN 3 THEN 'Management Fee'
        WHEN 4 THEN 'Insurance'
        ELSE 'Legal'
    END,
    ROUND(CAST(350.00 + ((p.property_id * 17 + m.month * 31) % 1850) AS numeric), 2),
    make_date(y.year, m.month, 15),
    'Monthly operational outlay for ' || p.name,
    make_date(y.year, m.month, 15)::timestamp with time zone,
    32
FROM properties p
CROSS JOIN generate_series(2022, 2025) AS y(year)
CROSS JOIN generate_series(1, 12) AS m(month)
WHERE NOT EXISTS (
    SELECT 1 FROM expenses e 
    WHERE e.property_id = p.property_id 
      AND EXTRACT(YEAR FROM e.expense_date) = y.year 
      AND EXTRACT(MONTH FROM e.expense_date) = m.month
);

-- ----------------------------------------------------------------------
-- 5. Refresh PostgreSQL Catalog Statistics
-- ----------------------------------------------------------------------
ANALYZE properties;
ANALYZE buildings;
ANALYZE units;
ANALYZE leases;
ANALYZE tenants;
ANALYZE rent_charges;
ANALYZE payments;
ANALYZE payment_audit;
ANALYZE payment_allocations;
ANALYZE expenses;

COMMIT;
