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
            dsns_to_try = []
            if settings.DATABASE_URL:
                dsns_to_try.append(settings.DATABASE_URL)
            if settings.DATABASE_PUBLIC_URL and settings.DATABASE_PUBLIC_URL not in dsns_to_try:
                dsns_to_try.append(settings.DATABASE_PUBLIC_URL)

            if dsns_to_try:
                last_err = None
                for raw_dsn in dsns_to_try:
                    dsn = raw_dsn
                    if dsn.startswith("postgres://"):
                        dsn = dsn.replace("postgres://", "postgresql://", 1)
                    try:
                        db_pool = pool.ThreadedConnectionPool(
                            minconn=settings.DB_POOL_MIN,
                            maxconn=settings.DB_POOL_MAX,
                            dsn=dsn
                        )
                        logger.info("PostgreSQL ThreadedConnectionPool initialized successfully.")
                        return
                    except Exception as conn_err:
                        masked = raw_dsn.split("@")[-1] if "@" in raw_dsn else "target host"
                        logger.warning(f"Database connection attempt to {masked} failed: {conn_err}")
                        last_err = conn_err
                if last_err:
                    raise last_err
            else:
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
        try:
            if not getattr(db_pool, "closed", False):
                db_pool.closeall()
        except Exception:
            pass
        finally:
            db_pool = None
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
