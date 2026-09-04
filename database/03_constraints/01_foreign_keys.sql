-- ======================================================================
-- PropLedger Database Schema: Foreign Key Constraints
-- Target: PostgreSQL 16
-- ======================================================================

-- RBAC
ALTER TABLE role_permissions ADD CONSTRAINT fk_rp_role FOREIGN KEY (role_id) REFERENCES roles(role_id) ON DELETE CASCADE;
ALTER TABLE role_permissions ADD CONSTRAINT fk_rp_permission FOREIGN KEY (permission_id) REFERENCES permissions(permission_id) ON DELETE CASCADE;
ALTER TABLE user_roles ADD CONSTRAINT fk_ur_user FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE;
ALTER TABLE user_roles ADD CONSTRAINT fk_ur_role FOREIGN KEY (role_id) REFERENCES roles(role_id) ON DELETE CASCADE;

-- Property Hierarchy
ALTER TABLE properties ADD CONSTRAINT fk_properties_owner FOREIGN KEY (owner_id) REFERENCES owners(owner_id) ON DELETE RESTRICT;
ALTER TABLE buildings ADD CONSTRAINT fk_buildings_property FOREIGN KEY (property_id) REFERENCES properties(property_id) ON DELETE CASCADE;
ALTER TABLE units ADD CONSTRAINT fk_units_building FOREIGN KEY (building_id) REFERENCES buildings(building_id) ON DELETE CASCADE;

-- Tenant Contacts
ALTER TABLE tenant_contacts ADD CONSTRAINT fk_contacts_tenant FOREIGN KEY (tenant_id) REFERENCES tenants(tenant_id) ON DELETE CASCADE;

-- Leases
ALTER TABLE leases ADD CONSTRAINT fk_leases_unit FOREIGN KEY (unit_id) REFERENCES units(unit_id) ON DELETE RESTRICT;
ALTER TABLE leases ADD CONSTRAINT fk_leases_late_fee_policy FOREIGN KEY (late_fee_policy_id) REFERENCES late_fee_policies(policy_id) ON DELETE RESTRICT;
ALTER TABLE leases ADD CONSTRAINT fk_leases_predecessor FOREIGN KEY (predecessor_lease_id) REFERENCES leases(lease_id) ON DELETE SET NULL;
ALTER TABLE lease_tenants ADD CONSTRAINT fk_lt_lease FOREIGN KEY (lease_id) REFERENCES leases(lease_id) ON DELETE CASCADE;
ALTER TABLE lease_tenants ADD CONSTRAINT fk_lt_tenant FOREIGN KEY (tenant_id) REFERENCES tenants(tenant_id) ON DELETE RESTRICT;

-- Billing & Payments
ALTER TABLE rent_charges ADD CONSTRAINT fk_rc_lease FOREIGN KEY (lease_id) REFERENCES leases(lease_id) ON DELETE RESTRICT;
ALTER TABLE late_fees ADD CONSTRAINT fk_lf_charge FOREIGN KEY (charge_id) REFERENCES rent_charges(charge_id) ON DELETE CASCADE;
ALTER TABLE payments ADD CONSTRAINT fk_payments_lease FOREIGN KEY (lease_id) REFERENCES leases(lease_id) ON DELETE RESTRICT;
ALTER TABLE payment_allocations ADD CONSTRAINT fk_pa_payment FOREIGN KEY (payment_id) REFERENCES payments(payment_id) ON DELETE CASCADE;
ALTER TABLE payment_allocations ADD CONSTRAINT fk_pa_charge FOREIGN KEY (charge_id) REFERENCES rent_charges(charge_id) ON DELETE RESTRICT;
ALTER TABLE tenant_balances ADD CONSTRAINT fk_tb_tenant FOREIGN KEY (tenant_id) REFERENCES tenants(tenant_id) ON DELETE RESTRICT;
ALTER TABLE tenant_balances ADD CONSTRAINT fk_tb_lease FOREIGN KEY (lease_id) REFERENCES leases(lease_id) ON DELETE RESTRICT;
ALTER TABLE security_deposits ADD CONSTRAINT fk_sd_lease FOREIGN KEY (lease_id) REFERENCES leases(lease_id) ON DELETE RESTRICT;
ALTER TABLE security_deposits ADD CONSTRAINT fk_sd_tenant FOREIGN KEY (tenant_id) REFERENCES tenants(tenant_id) ON DELETE RESTRICT;

-- Maintenance & Vendors
ALTER TABLE maintenance_requests ADD CONSTRAINT fk_mr_unit FOREIGN KEY (unit_id) REFERENCES units(unit_id) ON DELETE RESTRICT;
ALTER TABLE maintenance_requests ADD CONSTRAINT fk_mr_tenant FOREIGN KEY (tenant_id) REFERENCES tenants(tenant_id) ON DELETE SET NULL;
ALTER TABLE work_orders ADD CONSTRAINT fk_wo_request FOREIGN KEY (request_id) REFERENCES maintenance_requests(request_id) ON DELETE CASCADE;
ALTER TABLE work_orders ADD CONSTRAINT fk_wo_vendor FOREIGN KEY (vendor_id) REFERENCES vendors(vendor_id) ON DELETE SET NULL;

-- Accounting & Collections
ALTER TABLE expenses ADD CONSTRAINT fk_exp_property FOREIGN KEY (property_id) REFERENCES properties(property_id) ON DELETE RESTRICT;
ALTER TABLE expenses ADD CONSTRAINT fk_exp_vendor FOREIGN KEY (vendor_id) REFERENCES vendors(vendor_id) ON DELETE SET NULL;
ALTER TABLE invoices ADD CONSTRAINT fk_inv_property FOREIGN KEY (property_id) REFERENCES properties(property_id) ON DELETE RESTRICT;
ALTER TABLE invoices ADD CONSTRAINT fk_inv_vendor FOREIGN KEY (vendor_id) REFERENCES vendors(vendor_id) ON DELETE RESTRICT;
ALTER TABLE invoice_items ADD CONSTRAINT fk_ii_invoice FOREIGN KEY (invoice_id) REFERENCES invoices(invoice_id) ON DELETE CASCADE;

ALTER TABLE collection_cases ADD CONSTRAINT fk_cc_lease FOREIGN KEY (lease_id) REFERENCES leases(lease_id) ON DELETE RESTRICT;
ALTER TABLE collection_cases ADD CONSTRAINT fk_cc_tenant FOREIGN KEY (tenant_id) REFERENCES tenants(tenant_id) ON DELETE RESTRICT;
ALTER TABLE collection_activities ADD CONSTRAINT fk_ca_case FOREIGN KEY (case_id) REFERENCES collection_cases(case_id) ON DELETE CASCADE;

-- History
ALTER TABLE lease_history ADD CONSTRAINT fk_lh_lease FOREIGN KEY (lease_id) REFERENCES leases(lease_id) ON DELETE CASCADE;
ALTER TABLE payment_audit ADD CONSTRAINT fk_pa_payment_ref FOREIGN KEY (payment_id) REFERENCES payments(payment_id) ON DELETE CASCADE;
