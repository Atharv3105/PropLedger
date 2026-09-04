-- ======================================================================
-- PropLedger Database Schema: Maintenance & Vendor Tables
-- Target: PostgreSQL 16
-- ======================================================================

CREATE TABLE IF NOT EXISTS vendors (
    vendor_id BIGSERIAL PRIMARY KEY,
    company_name VARCHAR(150) NOT NULL,
    trade_category VARCHAR(100) NOT NULL, -- 'PLUMBING', 'ELECTRICAL', 'HVAC', 'ROOFING', 'GENERAL'
    contact_name VARCHAR(150) NOT NULL,
    phone VARCHAR(50) NOT NULL,
    email VARCHAR(255) NOT NULL,
    address TEXT,
    tax_id VARCHAR(50),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by BIGINT,
    modified_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    modified_by BIGINT
);

CREATE TABLE IF NOT EXISTS maintenance_requests (
    request_id BIGSERIAL PRIMARY KEY,
    unit_id BIGINT NOT NULL,
    tenant_id BIGINT,
    category VARCHAR(100) NOT NULL,
    priority VARCHAR(50) NOT NULL DEFAULT 'MEDIUM',
    description TEXT NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'OPEN',
    reported_date TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    resolved_date TIMESTAMPTZ,
    closed_date TIMESTAMPTZ,
    resolution_notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by BIGINT,
    modified_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    modified_by BIGINT
);

CREATE TABLE IF NOT EXISTS work_orders (
    work_order_id BIGSERIAL PRIMARY KEY,
    request_id BIGINT NOT NULL,
    vendor_id BIGINT,
    assigned_technician VARCHAR(150),
    estimated_cost NUMERIC(10, 2) NOT NULL DEFAULT 0.00,
    actual_cost NUMERIC(10, 2) NOT NULL DEFAULT 0.00,
    scheduled_date DATE,
    completed_date DATE,
    status VARCHAR(50) NOT NULL DEFAULT 'ASSIGNED',
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by BIGINT,
    modified_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    modified_by BIGINT
);
