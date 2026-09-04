-- ======================================================================
-- PropLedger Database Schema: Baseline Foreign Key and Lookup Indexes
-- Target: PostgreSQL 16
-- ======================================================================

-- Foreign key indexes for join performance
CREATE INDEX IF NOT EXISTS idx_properties_owner_id ON properties(owner_id);
CREATE INDEX IF NOT EXISTS idx_buildings_property_id ON buildings(property_id);
CREATE INDEX IF NOT EXISTS idx_units_building_id ON units(building_id);
CREATE INDEX IF NOT EXISTS idx_units_status ON units(status);
CREATE INDEX IF NOT EXISTS idx_units_type ON units(unit_type);

CREATE INDEX IF NOT EXISTS idx_leases_unit_id ON leases(unit_id);
CREATE INDEX IF NOT EXISTS idx_leases_status ON leases(status);
CREATE INDEX IF NOT EXISTS idx_leases_dates ON leases(start_date, end_date);
CREATE INDEX IF NOT EXISTS idx_lease_tenants_tenant_id ON lease_tenants(tenant_id);

CREATE INDEX IF NOT EXISTS idx_rent_charges_lease_id ON rent_charges(lease_id);
CREATE INDEX IF NOT EXISTS idx_rent_charges_status ON rent_charges(status);
CREATE INDEX IF NOT EXISTS idx_rent_charges_period ON rent_charges(billing_year, billing_month);

CREATE INDEX IF NOT EXISTS idx_payments_lease_id ON payments(lease_id);
CREATE INDEX IF NOT EXISTS idx_payments_date ON payments(payment_date);
CREATE INDEX IF NOT EXISTS idx_payment_allocations_payment_id ON payment_allocations(payment_id);
CREATE INDEX IF NOT EXISTS idx_payment_allocations_charge_id ON payment_allocations(charge_id);

CREATE INDEX IF NOT EXISTS idx_maintenance_unit_id ON maintenance_requests(unit_id);
CREATE INDEX IF NOT EXISTS idx_maintenance_status ON maintenance_requests(status);
CREATE INDEX IF NOT EXISTS idx_work_orders_request_id ON work_orders(request_id);
CREATE INDEX IF NOT EXISTS idx_work_orders_vendor_id ON work_orders(vendor_id);

CREATE INDEX IF NOT EXISTS idx_expenses_property_id ON expenses(property_id);
CREATE INDEX IF NOT EXISTS idx_invoices_property_id ON invoices(property_id);
CREATE INDEX IF NOT EXISTS idx_invoices_vendor_id ON invoices(vendor_id);
