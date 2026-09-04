-- ======================================================================
-- Procedure: usp_ReopenMaintenanceRequest
-- Description: Reopens a closed maintenance ticket with audit justification (Rule BR-08)
-- PRD Reference: Part W (BR-08), Part I (Module 7)
-- ======================================================================

CREATE OR REPLACE FUNCTION usp_ReopenMaintenanceRequest(
    p_request_id BIGINT,
    p_reason TEXT,
    p_user_id BIGINT
) RETURNS JSONB AS $$
DECLARE
    v_current_status VARCHAR(50);
BEGIN
    SELECT status INTO v_current_status
    FROM maintenance_requests
    WHERE request_id = p_request_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Maintenance request ID % does not exist', p_request_id;
    END IF;

    IF v_current_status != 'CLOSED' THEN
        RETURN jsonb_build_object(
            'status', 'NOT_MODIFIED',
            'request_id', p_request_id,
            'current_status', v_current_status,
            'message', 'Request is not closed; cannot reopen'
        );
    END IF;

    -- Update request status to OPEN and append reopen reason
    UPDATE maintenance_requests
    SET status = 'OPEN',
        closed_date = NULL,
        resolution_notes = COALESCE(resolution_notes, '') || ' | REOPENED on ' || CURRENT_DATE::TEXT || ': ' || p_reason,
        modified_at = CURRENT_TIMESTAMP,
        modified_by = p_user_id
    WHERE request_id = p_request_id;

    -- Log transition in status_history
    INSERT INTO status_history (entity_type, entity_id, old_status, new_status, changed_by, changed_at, reason)
    VALUES ('MAINTENANCE_REQUEST', p_request_id, 'CLOSED', 'OPEN', p_user_id, CURRENT_TIMESTAMP, p_reason);

    RETURN jsonb_build_object(
        'status', 'SUCCESS',
        'request_id', p_request_id,
        'new_status', 'OPEN',
        'reason', p_reason
    );
END;
$$ LANGUAGE plpgsql;
