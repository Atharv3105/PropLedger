from app.core.database import get_db_cursor

class BillingService:
    @staticmethod
    def generate_monthly_rent(billing_month: int, billing_year: int) -> dict:
        with get_db_cursor(commit=True) as cur:
            cur.execute("""
                SELECT * FROM usp_GenerateMonthlyRent(%s, %s);
            """, (billing_month, billing_year))
            row = cur.fetchone()
            return {
                "billing_month": billing_month,
                "billing_year": billing_year,
                "charges_created": row["charges_created"] if row else 0,
                "total_amount": float(row["total_amount_billed"]) if row and row["total_amount_billed"] else 0.0,
                "message": f"Generated monthly rent charges for {billing_month:02d}/{billing_year}"
            }
