-- ======================================================================
-- PropLedger Database Schema: Billing, Rent & Payment Tables
-- Target: PostgreSQL 16
-- ======================================================================

CREATE TABLE IF NOT EXISTS rent_charges (
    charge_id BIGSERIAL PRIMARY KEY,
    lease_id BIGINT NOT NULL,
    billing_month INT NOT NULL,
    billing_year INT NOT NULL,
    charge_date DATE NOT NULL,
    due_date DATE NOT NULL,
    charge_amount NUMERIC(12, 2) NOT NULL,
    amount_paid NUMERIC(12, 2) NOT NULL DEFAULT 0.00,
    status VARCHAR(50) NOT NULL DEFAULT 'PENDING',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by BIGINT,
    modified_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    modified_by BIGINT,
    CONSTRAINT uq_lease_billing_period UNIQUE (lease_id, billing_month, billing_year)
);

CREATE TABLE IF NOT EXISTS late_fees (
    late_fee_id BIGSERIAL PRIMARY KEY,
    charge_id BIGINT NOT NULL,
    assessment_date DATE NOT NULL,
    fee_amount NUMERIC(10, 2) NOT NULL,
    is_waived BOOLEAN NOT NULL DEFAULT FALSE,
    waived_reason TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by BIGINT
);

CREATE TABLE IF NOT EXISTS payments (
    payment_id BIGSERIAL PRIMARY KEY,
    lease_id BIGINT NOT NULL,
    payment_date DATE NOT NULL,
    amount NUMERIC(12, 2) NOT NULL,
    payment_method VARCHAR(50) NOT NULL DEFAULT 'BANK_TRANSFER', -- 'BANK_TRANSFER', 'CHECK', 'UPI', 'CREDIT_CARD', 'CASH'
    reference_number VARCHAR(100),
    notes TEXT,
    recorded_by BIGINT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS payment_allocations (
    allocation_id BIGSERIAL PRIMARY KEY,
    payment_id BIGINT NOT NULL,
    charge_id BIGINT NOT NULL,
    allocated_amount NUMERIC(12, 2) NOT NULL,
    allocated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS tenant_balances (
    balance_id BIGSERIAL PRIMARY KEY,
    tenant_id BIGINT NOT NULL,
    lease_id BIGINT NOT NULL UNIQUE,
    total_billed NUMERIC(14, 2) NOT NULL DEFAULT 0.00,
    total_paid NUMERIC(14, 2) NOT NULL DEFAULT 0.00,
    total_late_fees NUMERIC(14, 2) NOT NULL DEFAULT 0.00,
    outstanding_balance NUMERIC(14, 2) NOT NULL DEFAULT 0.00,
    last_updated TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS security_deposits (
    deposit_id BIGSERIAL PRIMARY KEY,
    lease_id BIGINT NOT NULL UNIQUE,
    tenant_id BIGINT NOT NULL,
    amount_received NUMERIC(12, 2) NOT NULL,
    received_date DATE NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'HELD', -- 'HELD', 'PARTIALLY_REFUNDED', 'FULLY_REFUNDED', 'FORFEITED'
    deduction_amount NUMERIC(12, 2) NOT NULL DEFAULT 0.00,
    deduction_reason TEXT,
    refund_amount NUMERIC(12, 2) NOT NULL DEFAULT 0.00,
    refund_date DATE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by BIGINT,
    modified_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    modified_by BIGINT
);
