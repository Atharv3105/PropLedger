-- ======================================================================
-- PropLedger Database Schema: System Lookups & Initial Catalogs
-- Target: PostgreSQL 16
-- ======================================================================

-- Roles (All 7 required roles from PRD Part D)
INSERT INTO roles (role_id, role_name, description) VALUES
(1, 'ADMIN', 'Complete system control and administration'),
(2, 'PROPERTY_MANAGER', 'Manages properties, units, leases, tenants and operational workflows'),
(3, 'LEASING_STAFF', 'Handles prospective tenants, lease creation and renewals'),
(4, 'ACCOUNTANT', 'Handles rent billing, payments, invoices, expenses and financial reports'),
(5, 'MAINTENANCE_STAFF', 'Handles maintenance requests, work orders, technician dispatches'),
(6, 'OWNER', 'Views property-level operational and financial performance reports'),
(7, 'TENANT', 'Tenant self-service: lease view, payment submission, maintenance ticketing')
ON CONFLICT (role_name) DO NOTHING;

SELECT setval('roles_role_id_seq', (SELECT MAX(role_id) FROM roles));

-- Core Permissions
INSERT INTO permissions (permission_code, module, description) VALUES
('property:create', 'PROPERTY', 'Create new properties and buildings'),
('property:edit', 'PROPERTY', 'Modify property and unit details'),
('property:view', 'PROPERTY', 'View property listings'),
('lease:create', 'LEASE', 'Create and sign leases'),
('lease:renew', 'LEASE', 'Renew or terminate leases'),
('payment:record', 'BILLING', 'Record payments and apply credits'),
('report:financial', 'FINANCE', 'Access financial statements and delinquency data'),
('maintenance:create', 'MAINTENANCE', 'Create maintenance requests'),
('maintenance:assign', 'MAINTENANCE', 'Assign work orders to vendors')
ON CONFLICT (permission_code) DO NOTHING;

-- Map Admin to all permissions
INSERT INTO role_permissions (role_id, permission_id)
SELECT 1, permission_id FROM permissions
ON CONFLICT DO NOTHING;

-- Property Types
INSERT INTO property_types (code, name, description) VALUES
('RESIDENTIAL', 'Residential', 'Apartments, condos, single-family homes'),
('COMMERCIAL', 'Commercial', 'Office spaces, retail shops, warehouses'),
('MIXED', 'Mixed Use', 'Combined commercial ground floor with residential towers')
ON CONFLICT (code) DO NOTHING;

-- Unit Types
INSERT INTO unit_types (code, name, default_bedrooms, default_bathrooms) VALUES
('STUDIO', 'Studio Apartment', 0, 1.0),
('1BHK', '1 Bedroom Hall Kitchen', 1, 1.0),
('2BHK', '2 Bedroom Hall Kitchen', 2, 2.0),
('3BHK', '3 Bedroom Hall Kitchen', 3, 2.5),
('OFFICE_SMALL', 'Small Commercial Office', 1, 1.0),
('OFFICE_LARGE', 'Large Corporate Suite', 5, 2.0),
('RETAIL_SHOP', 'Ground Floor Retail Storefront', 1, 1.0)
ON CONFLICT (code) DO NOTHING;

-- Unit Statuses
INSERT INTO unit_statuses (code, name, description) VALUES
('AVAILABLE', 'Available', 'Vacant and ready for lease'),
('OCCUPIED', 'Occupied', 'Currently leased with active contract'),
('RESERVED', 'Reserved', 'Deposit received, lease pending signature'),
('MAINTENANCE', 'Under Maintenance', 'Turnover repairs or refurbishment in progress'),
('INACTIVE', 'Inactive', 'Decommissioned or off-market')
ON CONFLICT (code) DO NOTHING;

-- Lease Statuses
INSERT INTO lease_statuses (code, name, description) VALUES
('DRAFT', 'Draft', 'Under preparation'),
('ACTIVE', 'Active', 'Fully executed and active'),
('EXPIRING', 'Expiring Soon', 'Within 60 days of scheduled termination'),
('EXPIRED', 'Expired', 'Past end date without renewal'),
('TERMINATED', 'Terminated', 'Early termination or eviction'),
('RENEWED', 'Renewed', 'Renewed into successor lease term')
ON CONFLICT (code) DO NOTHING;

-- Default Late Fee Policies
INSERT INTO late_fee_policies (policy_name, grace_period_days, fee_type, fee_amount, fee_percentage, max_fee_cap) VALUES
('Standard Residential (5-day grace, 5%)', 5, 'PERCENTAGE', 500.00, 5.00, 2500.00),
('Strict Commercial (3-day grace, 10%)', 3, 'PERCENTAGE', 1000.00, 10.00, 10000.00),
('Flat Fee Grace (7-day grace, ₹500 flat)', 7, 'FLAT', 500.00, 0.00, 500.00)
ON CONFLICT (policy_name) DO NOTHING;
