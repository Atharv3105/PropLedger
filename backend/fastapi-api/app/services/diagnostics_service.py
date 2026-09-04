from app.core.database import ping_database, get_db_cursor
from datetime import datetime, timezone

class DiagnosticsService:
    @staticmethod
    def get_system_health() -> dict:
        db_info = ping_database()
        return {
            "status": "HEALTHY",
            "environment": "production-ready",
            "database": db_info,
            "pool": {
                "engine": "PostgreSQL 16",
                "pool_type": "ThreadedConnectionPool",
                "status": "operational"
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    @staticmethod
    def get_recent_incidents() -> dict:
        with get_db_cursor() as cur:
            # Query audit log errors or collection severe cases as operational health indicators
            cur.execute("""
                SELECT 
                    case_id, lease_id, overdue_amount, days_overdue, status, opened_date
                FROM collection_cases
                ORDER BY opened_date DESC
                LIMIT 10;
            """)
            cases = cur.fetchall()
            return {
                "incident_count": len(cases),
                "recent_incidents": cases
            }
