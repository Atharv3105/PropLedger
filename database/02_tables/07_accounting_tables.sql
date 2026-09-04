-- ======================================================================
-- PropLedger Database Schema: Expenses, Invoices & Collections
-- Target: PostgreSQL 16
-- ======================================================================

CREATE TABLE IF NOT EXISTS expenses (
    expense_id BIGSERIAL PRIMARY KEY,
    property_id BIGINT NOT NULL,
    vendor_id BIGINT,
    category VARCHAR(100) NOT NULL, -- 'MAINTENANCE', 'UTILITIES', 'ADMIN', 'INSURANCE', 'TAXES'
    amount NUMERIC(12, 2) NOT NULL,
    expense_date DATE NOT NULL,
    description TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by BIGINT,
    modified_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    modified_by BIGINT
);

CREATE TABLE IF NOT EXISTS invoices (
    invoice_id BIGSERIAL PRIMARY KEY,
    property_id BIGINT NOT NULL,
    vendor_id BIGINT NOT NULL,
    invoice_number VARCHAR(100) NOT NULL,
    invoice_date DATE NOT NULL,
    due_date DATE NOT NULL,
    total_amount NUMERIC(12, 2) NOT NULL,
    payment_status VARCHAR(50) NOT NULL DEFAULT 'PENDING',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by BIGINT,
    modified_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    modified_by BIGINT,
    CONSTRAINT uq_vendor_invoice UNIQUE (vendor_id, invoice_number)
);

CREATE TABLE IF NOT EXISTS invoice_items (
    item_id BIGSERIAL PRIMARY KEY,
    invoice_id BIGINT NOT NULL,
    description TEXT NOT NULL,
    quantity NUMERIC(10, 2) NOT NULL DEFAULT 1.00,
    unit_price NUMERIC(10, 2) NOT NULL,
    total_amount NUMERIC(12, 2) NOT NULL
);

CREATE TABLE IF NOT EXISTS collection_cases (
    case_id BIGSERIAL PRIMARY KEY,
    lease_id BIGINT NOT NULL,
    tenant_id BIGINT NOT NULL,
    overdue_amount NUMERIC(12, 2) NOT NULL,
    days_overdue INT NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'OPEN',
    opened_date DATE NOT NULL,
    resolved_date DATE,
    settlement_amount NUMERIC(12, 2),
    write_off_amount NUMERIC(12, 2),
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by BIGINT,
    modified_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    modified_by BIGINT
);

CREATE TABLE IF NOT EXISTS collection_activities (
    activity_id BIGSERIAL PRIMARY KEY,
    case_id BIGINT NOT NULL,
    activity_type VARCHAR(50) NOT NULL, -- 'PHONE_CALL', 'DEMAND_LETTER', 'LEGAL_NOTICE', 'SETTLEMENT_OFFER'
    activity_date TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    notes TEXT NOT NULL,
    performed_by BIGINT NOT NULL
);
