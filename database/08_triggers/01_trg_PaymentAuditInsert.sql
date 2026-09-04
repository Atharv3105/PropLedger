-- ======================================================================
-- Trigger: trg_PaymentAuditInsert
-- Description: Automatically creates an immutable audit record whenever a payment is inserted
-- PRD Reference: Part J, Part L
-- ======================================================================

CREATE OR REPLACE FUNCTION fn_trg_PaymentAudit()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO payment_audit (payment_id, lease_id, action, payment_amount, recorded_by, recorded_at, client_ip, audit_notes)
    VALUES (
        NEW.payment_id,
        NEW.lease_id,
        'RECORDED',
        NEW.amount,
        NEW.recorded_by,
        CURRENT_TIMESTAMP,
        '127.0.0.1',
        'Auto-audited payment transaction ref: ' || COALESCE(NEW.reference_number, 'N/A')
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_PaymentAuditInsert ON payments;
CREATE TRIGGER trg_PaymentAuditInsert
AFTER INSERT ON payments
FOR EACH ROW
EXECUTE FUNCTION fn_trg_PaymentAudit();
