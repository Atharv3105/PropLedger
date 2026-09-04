import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

db_pool = None

def init_db_pool():
    global db_pool
    if db_pool is None:
        try:
            db_pool = pool.ThreadedConnectionPool(
                minconn=settings.DB_POOL_MIN,
                maxconn=settings.DB_POOL_MAX,
                host=settings.DB_HOST,
                port=settings.DB_PORT,
                user=settings.DB_USER,
                password=settings.DB_PASSWORD,
                dbname=settings.DB_NAME
            )
            logger.info("PostgreSQL ThreadedConnectionPool initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize database connection pool: {e}")
            raise e

def close_db_pool():
    global db_pool
    if db_pool is not None:
        db_pool.closeall()
        logger.info("PostgreSQL connection pool closed.")

@contextmanager
def get_db_connection():
    global db_pool
    if db_pool is None:
        init_db_pool()
    conn = db_pool.getconn()
    try:
        yield conn
    finally:
        db_pool.putconn(conn)

@contextmanager
def get_db_cursor(commit: bool = False):
    with get_db_connection() as conn:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        try:
            yield cursor
            if commit:
                conn.commit()
        except Exception as e:
            if commit:
                conn.rollback()
            raise e
        finally:
            cursor.close()

def ping_database() -> dict:
    with get_db_cursor() as cur:
        cur.execute("SELECT version();")
        version_row = cur.fetchone()
        cur.execute("SELECT COUNT(*) AS table_count FROM information_schema.tables WHERE table_schema = 'public';")
        tables_row = cur.fetchone()
        return {
            "status": "connected",
            "version": version_row["version"] if version_row else "unknown",
            "table_count": tables_row["table_count"] if tables_row else 0
        }
