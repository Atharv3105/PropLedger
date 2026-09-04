-- ======================================================================
-- PropLedger Database Schema: Extensions and Core Types
-- Target: PostgreSQL 16
-- ======================================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "tablefunc";

-- Drop existing types if recreating
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'property_type_enum') THEN
        CREATE TYPE property_type_enum AS ENUM ('RESIDENTIAL', 'COMMERCIAL', 'MIXED');
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'unit_status_enum') THEN
        CREATE TYPE unit_status_enum AS ENUM ('AVAILABLE', 'OCCUPIED', 'RESERVED', 'MAINTENANCE', 'INACTIVE');
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'lease_status_enum') THEN
        CREATE TYPE lease_status_enum AS ENUM ('DRAFT', 'ACTIVE', 'EXPIRING', 'EXPIRED', 'TERMINATED', 'RENEWED');
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'maintenance_status_enum') THEN
        CREATE TYPE maintenance_status_enum AS ENUM ('OPEN', 'ASSIGNED', 'IN_PROGRESS', 'ON_HOLD', 'RESOLVED', 'CLOSED');
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'priority_enum') THEN
        CREATE TYPE priority_enum AS ENUM ('LOW', 'MEDIUM', 'HIGH', 'EMERGENCY');
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'charge_status_enum') THEN
        CREATE TYPE charge_status_enum AS ENUM ('PENDING', 'PARTIALLY_PAID', 'PAID', 'OVERDUE', 'CANCELLED');
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'collection_status_enum') THEN
        CREATE TYPE collection_status_enum AS ENUM ('OPEN', 'IN_REVIEW', 'PAYMENT_PLAN', 'SETTLED', 'WRITTEN_OFF');
    END IF;
END $$;
