from app.core.database import get_db_cursor
from typing import List, Optional

class FinanceService:
    @staticmethod
    def list_expenses(property_id: Optional[int] = None, limit: int = 50, offset: int = 0) -> List[dict]:
        with get_db_cursor() as cur:
            query = """
                SELECT 
                    e.expense_id, e.property_id, p.name AS property_name,
                    v.company_name AS vendor_name, e.category, e.amount,
                    e.expense_date, e.description
                FROM expenses e
                JOIN properties p ON e.property_id = p.property_id
                LEFT JOIN vendors v ON e.vendor_id = v.vendor_id
            """
            params = []
            if property_id:
                query += " WHERE e.property_id = %s"
                params.append(property_id)
            
            query += " ORDER BY e.expense_date DESC LIMIT %s OFFSET %s;"
            params.extend([limit, offset])
            cur.execute(query, tuple(params))
            return cur.fetchall()

    @staticmethod
    def get_financial_summaries(property_id: Optional[int] = None) -> List[dict]:
        with get_db_cursor() as cur:
            query = """
                SELECT 
                    property_id, property_code, property_name, property_type,
                    city, owner_name, total_billed_rent, total_collected_rent,
                    total_late_fees_collected, total_operating_revenue,
                    total_operating_expenses, net_operating_income, collection_percentage
                FROM vw_PropertyFinancialSummary
            """
            params = []
            if property_id:
                query += " WHERE property_id = %s"
                params.append(property_id)
            
            query += " ORDER BY property_id ASC;"
            cur.execute(query, tuple(params))
            return cur.fetchall()
