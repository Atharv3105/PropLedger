-- ======================================================================
-- PropLedger Database Schema: Audit & History Tables (PRD Part L)
-- Target: PostgreSQL 16
-- ======================================================================

CREATE TABLE IF NOT EXISTS lease_history (
    history_id BIGSERIAL PRIMARY KEY,
    lease_id BIGINT NOT NULL,
    action VARCHAR(50) NOT NULL, -- 'CREATED', 'STATUS_CHANGE', 'RENT_ADJUSTED', 'RENEWED', 'TERMINATED'
    old_rent NUMERIC(12, 2),
    new_rent NUMERIC(12, 2),
    old_status VARCHAR(50),
    new_status VARCHAR(50),
    changed_by BIGINT,
    changed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS payment_audit (
    audit_id BIGSERIAL PRIMARY KEY,
    payment_id BIGINT NOT NULL,
    lease_id BIGINT NOT NULL,
    action VARCHAR(50) NOT NULL DEFAULT 'RECORDED', -- 'RECORDED', 'ADJUSTED', 'VOIDED', 'REFUNDED'
    payment_amount NUMERIC(12, 2) NOT NULL,
    recorded_by BIGINT NOT NULL,
    recorded_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    client_ip VARCHAR(50),
    audit_notes TEXT
);

CREATE TABLE IF NOT EXISTS status_history (
    history_id BIGSERIAL PRIMARY KEY,
    entity_type VARCHAR(50) NOT NULL, -- 'UNIT', 'LEASE', 'MAINTENANCE_REQUEST', 'COLLECTION_CASE'
    entity_id BIGINT NOT NULL,
    old_status VARCHAR(50),
    new_status VARCHAR(50) NOT NULL,
    changed_by BIGINT,
    changed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    reason TEXT
);

CREATE TABLE IF NOT EXISTS system_audit_log (
    log_id BIGSERIAL PRIMARY KEY,
    table_name VARCHAR(100) NOT NULL,
    record_id BIGINT NOT NULL,
    action VARCHAR(20) NOT NULL, -- 'INSERT', 'UPDATE', 'DELETE'
    old_values JSONB,
    new_values JSONB,
    performed_by BIGINT,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
