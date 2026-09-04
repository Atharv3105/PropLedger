-- ======================================================================
-- PropLedger Database Schema: Property & Unit Tables
-- Target: PostgreSQL 16
-- ======================================================================

CREATE TABLE IF NOT EXISTS owners (
    owner_id BIGSERIAL PRIMARY KEY,
    company_name VARCHAR(150),
    contact_name VARCHAR(150) NOT NULL,
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(50) NOT NULL,
    tax_id VARCHAR(50),
    address TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by BIGINT,
    modified_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    modified_by BIGINT
);

CREATE TABLE IF NOT EXISTS property_types (
    property_type_id BIGSERIAL PRIMARY KEY,
    code VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    description TEXT
);

CREATE TABLE IF NOT EXISTS properties (
    property_id BIGSERIAL PRIMARY KEY,
    owner_id BIGINT NOT NULL,
    property_code VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(150) NOT NULL,
    property_type VARCHAR(50) NOT NULL DEFAULT 'RESIDENTIAL',
    address_line1 VARCHAR(255) NOT NULL,
    address_line2 VARCHAR(255),
    city VARCHAR(100) NOT NULL,
    state VARCHAR(100) NOT NULL,
    postal_code VARCHAR(20) NOT NULL,
    total_area_sqft NUMERIC(12, 2),
    year_built INT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by BIGINT,
    modified_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    modified_by BIGINT
);

CREATE TABLE IF NOT EXISTS buildings (
    building_id BIGSERIAL PRIMARY KEY,
    property_id BIGINT NOT NULL,
    building_code VARCHAR(50),
    name VARCHAR(150) NOT NULL,
    total_floors INT NOT NULL DEFAULT 1,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by BIGINT,
    modified_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    modified_by BIGINT
);

CREATE TABLE IF NOT EXISTS unit_types (
    unit_type_id BIGSERIAL PRIMARY KEY,
    code VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    default_bedrooms INT DEFAULT 1,
    default_bathrooms NUMERIC(3, 1) DEFAULT 1.0
);

CREATE TABLE IF NOT EXISTS unit_statuses (
    status_id BIGSERIAL PRIMARY KEY,
    code VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    description TEXT
);

CREATE TABLE IF NOT EXISTS units (
    unit_id BIGSERIAL PRIMARY KEY,
    building_id BIGINT NOT NULL,
    unit_number VARCHAR(50) NOT NULL,
    floor_number INT NOT NULL DEFAULT 1,
    unit_type VARCHAR(50) NOT NULL DEFAULT '1BHK',
    square_feet NUMERIC(10, 2) NOT NULL DEFAULT 650.00,
    market_rent NUMERIC(12, 2) NOT NULL DEFAULT 0.00,
    target_rent NUMERIC(12, 2) NOT NULL DEFAULT 0.00,
    status VARCHAR(50) NOT NULL DEFAULT 'AVAILABLE',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by BIGINT,
    modified_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    modified_by BIGINT,
    CONSTRAINT uq_building_unit UNIQUE (building_id, unit_number)
);
