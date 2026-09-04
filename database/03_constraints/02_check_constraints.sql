-- ======================================================================
-- PropLedger Database Schema: Business Rule Check Constraints
-- Target: PostgreSQL 16
-- ======================================================================

-- Business Rule BR-02: A lease cannot begin after its end date
ALTER TABLE leases ADD CONSTRAINT chk_lease_dates CHECK (start_date <= end_date);

-- Rent and deposit amounts must be non-negative
ALTER TABLE leases ADD CONSTRAINT chk_lease_rent CHECK (monthly_rent >= 0.00);
ALTER TABLE leases ADD CONSTRAINT chk_lease_deposit CHECK (security_deposit >= 0.00);
ALTER TABLE leases ADD CONSTRAINT chk_lease_rent_day CHECK (rent_due_day BETWEEN 1 AND 31);

-- Units pricing and geometry
ALTER TABLE units ADD CONSTRAINT chk_unit_market_rent CHECK (market_rent >= 0.00);
ALTER TABLE units ADD CONSTRAINT chk_unit_target_rent CHECK (target_rent >= 0.00);
ALTER TABLE units ADD CONSTRAINT chk_unit_sqft CHECK (square_feet > 0.00);

-- Billing & Payment validations
ALTER TABLE rent_charges ADD CONSTRAINT chk_rc_amount CHECK (charge_amount >= 0.00);
ALTER TABLE rent_charges ADD CONSTRAINT chk_rc_month CHECK (billing_month BETWEEN 1 AND 12);
ALTER TABLE rent_charges ADD CONSTRAINT chk_rc_due_date CHECK (due_date >= charge_date);
ALTER TABLE payments ADD CONSTRAINT chk_payment_amount CHECK (amount > 0.00);
ALTER TABLE payment_allocations ADD CONSTRAINT chk_allocation_amount CHECK (allocated_amount > 0.00);
ALTER TABLE late_fees ADD CONSTRAINT chk_late_fee_amount CHECK (fee_amount >= 0.00);

-- Maintenance & Work order costs
ALTER TABLE work_orders ADD CONSTRAINT chk_wo_est_cost CHECK (estimated_cost >= 0.00);
ALTER TABLE work_orders ADD CONSTRAINT chk_wo_act_cost CHECK (actual_cost >= 0.00);

-- Expenses & Invoices
ALTER TABLE expenses ADD CONSTRAINT chk_expense_amount CHECK (amount > 0.00);
ALTER TABLE invoices ADD CONSTRAINT chk_invoice_total CHECK (total_amount >= 0.00);
ALTER TABLE invoice_items ADD CONSTRAINT chk_item_quantity CHECK (quantity > 0.00);
ALTER TABLE invoice_items ADD CONSTRAINT chk_item_unit_price CHECK (unit_price >= 0.00);
