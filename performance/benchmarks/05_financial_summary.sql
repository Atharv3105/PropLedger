-- Query 5: Multi-Year Property Financial Performance Summary (Revenue vs Expenses)
-- Requirements: PL-136
-- Multi-year aggregation of operating inflows and expense outlays by category
WITH revenue_summary AS (
    SELECT 
        p.property_id,
        EXTRACT(YEAR FROM rc.due_date)::integer AS fiscal_year,
        SUM(rc.amount_paid) AS total_revenue,
        COUNT(DISTINCT rc.lease_id) AS active_lease_count
    FROM rent_charges rc
    JOIN leases l ON l.lease_id = rc.lease_id
    JOIN units u ON u.unit_id = l.unit_id
    JOIN buildings b ON b.building_id = u.building_id
    JOIN properties p ON p.property_id = b.property_id
    WHERE rc.due_date BETWEEN '2023-01-01' AND '2025-12-31'
    GROUP BY p.property_id, EXTRACT(YEAR FROM rc.due_date)
),
expense_summary AS (
    SELECT 
        e.property_id,
        EXTRACT(YEAR FROM e.expense_date)::integer AS fiscal_year,
        SUM(e.amount) AS total_expenses,
        SUM(CASE WHEN e.category = 'Utilities' THEN e.amount ELSE 0 END) AS utility_expenses,
        SUM(CASE WHEN e.category = 'Repairs' THEN e.amount ELSE 0 END) AS repair_expenses,
        SUM(CASE WHEN e.category = 'Management Fee' THEN e.amount ELSE 0 END) AS management_fees,
        SUM(CASE WHEN e.category = 'Insurance' THEN e.amount ELSE 0 END) AS insurance_expenses
    FROM expenses e
    WHERE e.expense_date BETWEEN '2023-01-01' AND '2025-12-31'
    GROUP BY e.property_id, EXTRACT(YEAR FROM e.expense_date)
)
SELECT 
    p.property_id,
    p.name AS property_name,
    p.property_type,
    r.fiscal_year,
    COALESCE(r.total_revenue, 0.00) AS total_revenue,
    COALESCE(e.total_expenses, 0.00) AS total_expenses,
    COALESCE(r.total_revenue, 0.00) - COALESCE(e.total_expenses, 0.00) AS net_operating_income,
    ROUND(
        (COALESCE(r.total_revenue, 0.00) - COALESCE(e.total_expenses, 0.00)) / 
        NULLIF(COALESCE(r.total_revenue, 0.00), 0) * 100, 2
    ) AS noi_margin_pct,
    COALESCE(e.utility_expenses, 0.00) AS utility_expenses,
    COALESCE(e.repair_expenses, 0.00) AS repair_expenses,
    COALESCE(e.management_fees, 0.00) AS management_fees
FROM properties p
JOIN revenue_summary r ON r.property_id = p.property_id
LEFT JOIN expense_summary e ON e.property_id = p.property_id AND e.fiscal_year = r.fiscal_year
ORDER BY r.fiscal_year DESC, net_operating_income DESC;
