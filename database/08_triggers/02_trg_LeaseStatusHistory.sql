-- ======================================================================
-- Trigger: trg_LeaseStatusHistory
-- Description: Automatically logs historical status changes on leases
-- PRD Reference: Part J, Part L
-- ======================================================================

CREATE OR REPLACE FUNCTION fn_trg_LeaseStatusHistory()
RETURNS TRIGGER AS $$
BEGIN
    IF (OLD.status IS DISTINCT FROM NEW.status) THEN
        INSERT INTO status_history (entity_type, entity_id, old_status, new_status, changed_by, changed_at, reason)
        VALUES (
            'LEASE',
            NEW.lease_id,
            OLD.status,
            NEW.status,
            COALESCE(NEW.modified_by, NEW.created_by),
            CURRENT_TIMESTAMP,
            'Automated lease transition from ' || OLD.status || ' to ' || NEW.status
        );
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_LeaseStatusHistory ON leases;
CREATE TRIGGER trg_LeaseStatusHistory
AFTER UPDATE OF status ON leases
FOR EACH ROW
EXECUTE FUNCTION fn_trg_LeaseStatusHistory();
