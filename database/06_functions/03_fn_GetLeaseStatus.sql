-- ======================================================================
-- Function: fn_GetLeaseStatus
-- Description: Evaluates effective lease status based on contract dates and as-of date
-- PRD Reference: Part J, Module 4
-- ======================================================================

CREATE OR REPLACE FUNCTION fn_GetLeaseStatus(
    p_lease_id BIGINT,
    p_as_of_date DATE DEFAULT CURRENT_DATE
) RETURNS VARCHAR AS $$
DECLARE
    v_start_date DATE;
    v_end_date DATE;
    v_current_status VARCHAR(50);
BEGIN
    SELECT start_date, end_date, status
    INTO v_start_date, v_end_date, v_current_status
    FROM leases
    WHERE lease_id = p_lease_id;

    IF NOT FOUND THEN
        RETURN 'NOT_FOUND';
    END IF;

    IF v_current_status IN ('TERMINATED', 'RENEWED', 'DRAFT') THEN
        RETURN v_current_status;
    END IF;

    IF p_as_of_date < v_start_date THEN
        RETURN 'DRAFT';
    ELSIF p_as_of_date > v_end_date THEN
        RETURN 'EXPIRED';
    ELSIF (v_end_date - p_as_of_date) <= 60 THEN
        RETURN 'EXPIRING';
    ELSE
        RETURN 'ACTIVE';
    END IF;
END;
$$ LANGUAGE plpgsql STABLE;
