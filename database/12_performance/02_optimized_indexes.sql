-- ======================================================================
-- PropLedger Phase 8: Targeted Performance Indexes
-- Target: PostgreSQL 16
-- Purpose: Optimize 5 critical operational & analytical workloads
--          addressing Sort elimination, Index-Only Scans, and Partial Indexing.
-- ======================================================================

-- 1. Partial Covering Index on Active Leases (PL-132: Property Occupancy)
CREATE INDEX IF NOT EXISTS idx_leases_active_units 
ON leases(unit_id) 
INCLUDE (monthly_rent, start_date, end_date) 
WHERE status = 'Active';

-- 2. Covering Index on Units for Building Aggregation (PL-132: Property Occupancy)
CREATE INDEX IF NOT EXISTS idx_units_building_status_cov 
ON units(building_id, status) 
INCLUDE (unit_number, market_rent, square_feet);

-- 3. Composite Covering Index on Payments (PL-133: Payment History Ledger)
-- Eliminates explicit Sort node before WindowAgg in running balance calculations
CREATE INDEX IF NOT EXISTS idx_payments_lease_date_id_cov 
ON payments(lease_id, payment_date ASC, payment_id ASC) 
INCLUDE (amount, payment_method, reference_number);

-- 4. Composite Covering Index on Rent Charges (PL-134: Rent Collection Aggregation)
-- Enables Index-Only Scans for monthly collection summaries
CREATE INDEX IF NOT EXISTS idx_rent_charges_year_month_cov 
ON rent_charges(billing_year, billing_month, lease_id) 
INCLUDE (charge_id, charge_amount, amount_paid, status);

-- 5. Partial Filtered Index on Delinquent Rent Charges (PL-135: Delinquency Aging)
-- Indexes only the ~10% delinquent subset of 132k charges
CREATE INDEX IF NOT EXISTS idx_rent_charges_delinquent_partial 
ON rent_charges(lease_id, due_date) 
INCLUDE (charge_amount, amount_paid, status) 
WHERE status IN ('PENDING', 'PARTIALLY_PAID', 'OVERDUE');

-- 6. Covering Index on Expenses for P&L Reporting (PL-136: Financial Summary)
CREATE INDEX IF NOT EXISTS idx_expenses_date_prop_cat_cov 
ON expenses(expense_date, property_id) 
INCLUDE (amount, category);

-- 7. Covering Index on Rent Charges Due Date (PL-136: Financial Summary)
CREATE INDEX IF NOT EXISTS idx_rent_charges_due_date_cov 
ON rent_charges(due_date) 
INCLUDE (lease_id, amount_paid);

-- Update statistics
ANALYZE leases;
ANALYZE units;
ANALYZE payments;
ANALYZE rent_charges;
ANALYZE expenses;
