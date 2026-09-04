-- ======================================================================
-- PropLedger Database Schema: Lease Management Tables
-- Target: PostgreSQL 16
-- ======================================================================

CREATE TABLE IF NOT EXISTS late_fee_policies (
    policy_id BIGSERIAL PRIMARY KEY,
    policy_name VARCHAR(100) NOT NULL UNIQUE,
    grace_period_days INT NOT NULL DEFAULT 5,
    fee_type VARCHAR(20) NOT NULL DEFAULT 'PERCENTAGE', -- 'FLAT', 'PERCENTAGE'
    fee_amount NUMERIC(10, 2) NOT NULL DEFAULT 500.00,
    fee_percentage NUMERIC(5, 2) NOT NULL DEFAULT 5.00,
    max_fee_cap NUMERIC(10, 2) DEFAULT 2500.00,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS lease_statuses (
    status_id BIGSERIAL PRIMARY KEY,
    code VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    description TEXT
);

CREATE TABLE IF NOT EXISTS leases (
    lease_id BIGSERIAL PRIMARY KEY,
    unit_id BIGINT NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    monthly_rent NUMERIC(12, 2) NOT NULL,
    security_deposit NUMERIC(12, 2) NOT NULL DEFAULT 0.00,
    rent_due_day INT NOT NULL DEFAULT 1,
    late_fee_policy_id BIGINT NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'DRAFT',
    renewal_status VARCHAR(50) NOT NULL DEFAULT 'PENDING', -- 'PENDING', 'RENEWED', 'NON_RENEWAL'
    predecessor_lease_id BIGINT,
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by BIGINT,
    modified_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    modified_by BIGINT
);

CREATE TABLE IF NOT EXISTS lease_tenants (
    lease_id BIGINT NOT NULL,
    tenant_id BIGINT NOT NULL,
    is_primary BOOLEAN NOT NULL DEFAULT TRUE,
    signed_date TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (lease_id, tenant_id)
);
