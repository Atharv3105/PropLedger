-- ======================================================================
-- Trigger: trg_PreventWorkOrderOnClosedMaintenance
-- Description: Enforces Business Rule BR-08 (No work orders on closed requests without reopening)
-- PRD Reference: Part W (BR-08)
-- ======================================================================

CREATE OR REPLACE FUNCTION fn_trg_PreventWorkOrderOnClosed()
RETURNS TRIGGER AS $$
DECLARE
    v_req_status VARCHAR(50);
BEGIN
    SELECT status INTO v_req_status
    FROM maintenance_requests
    WHERE request_id = NEW.request_id;

    IF v_req_status = 'CLOSED' THEN
        RAISE EXCEPTION 'Rule BR-08 Violation: Cannot attach a work order to a closed maintenance request (ID %). Reopen the request first.', NEW.request_id;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_PreventWorkOrderOnClosedMaintenance ON work_orders;
CREATE TRIGGER trg_PreventWorkOrderOnClosedMaintenance
BEFORE INSERT ON work_orders
FOR EACH ROW
EXECUTE FUNCTION fn_trg_PreventWorkOrderOnClosed();
