import time
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request

logger = logging.getLogger("propledger.api")

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        client_host = request.client.host if request.client else "unknown"
        path = request.url.path
        method = request.method
        
        response = await call_next(request)
        duration_ms = round((time.time() - start_time) * 1000, 2)
        
        logger.info(f"{method} {path} | Status: {response.status_code} | Duration: {duration_ms}ms | IP: {client_host}")
        response.headers["X-Response-Time-Ms"] = str(duration_ms)
        return response
