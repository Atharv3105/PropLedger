-- Query 2: Tenant & Lease Payment History Ledger with Cumulative Running Balance
-- Requirements: PL-133
-- Calculates chronological payment flow and running cumulative paid balance
SELECT 
    p.payment_id,
    p.lease_id,
    l.unit_id,
    p.payment_date,
    p.amount AS payment_amount,
    p.payment_method,
    p.reference_number,
    SUM(p.amount) OVER (
        PARTITION BY p.lease_id 
        ORDER BY p.payment_date ASC, p.payment_id ASC
    ) AS cumulative_amount_paid,
    COUNT(p.payment_id) OVER (
        PARTITION BY p.lease_id
    ) AS total_payments_count,
    AVG(p.amount) OVER (
        PARTITION BY p.lease_id
    ) AS average_payment_amount
FROM payments p
JOIN leases l ON l.lease_id = p.lease_id
WHERE p.payment_date >= '2023-01-01'
ORDER BY p.lease_id, p.payment_date ASC, p.payment_id ASC;
