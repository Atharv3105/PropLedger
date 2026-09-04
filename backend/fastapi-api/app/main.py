from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
import psycopg2
import logging

from app.core.config import settings
from app.core.database import init_db_pool, close_db_pool
from app.core.exceptions import (
    AppException,
    app_exception_handler,
    validation_exception_handler,
    db_exception_handler,
    general_exception_handler
)
from app.core.logging import RequestLoggingMiddleware
from app.api.v1.router import api_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("propledger")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting PropLedger API Backend...")
    try:
        init_db_pool()
    except Exception as e:
        logger.warning(f"Database connection pool initialization deferred (will retry on incoming requests): {e}")
    yield
    # Shutdown
    logger.info("Shutting down PropLedger API Backend...")
    close_db_pool()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="PropLedger Enterprise Property Management & Analytics Platform API",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request Logging Middleware
app.add_middleware(RequestLoggingMiddleware)

# RFC 7807 Problem Details Exception Handlers
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(psycopg2.Error, db_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Mount API V1 Router
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/", tags=["Root"])
def root():
    return {
        "title": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health",
        "status": "online"
    }

@app.get("/health", tags=["Root"])
def health():
    return {"status": "ok", "version": settings.VERSION}

if __name__ == "__main__":
    import os, uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=False)
