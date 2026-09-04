from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder
import psycopg2
import logging

logger = logging.getLogger(__name__)

class AppException(Exception):
    def __init__(
        self,
        status_code: int,
        title: str,
        detail: str,
        error_type: str = "about:blank",
        error_code: str = "APP_ERROR"
    ):
        self.status_code = status_code
        self.title = title
        self.detail = detail
        self.error_type = error_type
        self.error_code = error_code
        super().__init__(detail)

class NotFoundError(AppException):
    def __init__(self, detail: str = "Requested resource not found"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            title="Resource Not Found",
            detail=detail,
            error_code="RESOURCE_NOT_FOUND"
        )

class UnauthorizedError(AppException):
    def __init__(self, detail: str = "Authentication credentials required"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            title="Unauthorized",
            detail=detail,
            error_code="UNAUTHORIZED"
        )

class ForbiddenError(AppException):
    def __init__(self, detail: str = "Action forbidden for current role"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            title="Forbidden",
            detail=detail,
            error_code="FORBIDDEN_ACTION"
        )

class BusinessRuleViolationError(AppException):
    def __init__(self, detail: str, rule_id: str = "BR_VIOLATION"):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            title="Business Rule Violation",
            detail=detail,
            error_code=rule_id
        )

class ConflictError(AppException):
    def __init__(self, detail: str = "Resource conflict"):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            title="Conflict",
            detail=detail,
            error_code="CONFLICT"
        )

async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "type": exc.error_type,
            "title": exc.title,
            "status": exc.status_code,
            "detail": exc.detail,
            "instance": request.url.path,
            "code": exc.error_code
        },
        headers={"Content-Type": "application/problem+json"}
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    safe_errors = jsonable_encoder(errors)
    details = "; ".join([f"{e.get('loc', [])[-1] if e.get('loc') else 'field'}: {e.get('msg', '')}" for e in safe_errors])
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "type": "https://propledger.com/errors/validation-error",
            "title": "Validation Error",
            "status": 422,
            "detail": details,
            "instance": request.url.path,
            "code": "REQUEST_VALIDATION_FAILED",
            "errors": safe_errors
        },
        headers={"Content-Type": "application/problem+json"}
    )

async def db_exception_handler(request: Request, exc: psycopg2.Error):
    logger.error(f"Database error on {request.url.path}: {exc}")
    err_msg = str(exc).strip().split("\n")[0]
    if "P0001" in getattr(exc, "pgcode", "") or "BR-" in err_msg or "Cannot" in err_msg or "violates" in err_msg or "Rule Check Failed" in err_msg:
        detail = err_msg
        status_code = 422
        title = "Database Constraint or Business Rule Violation"
    else:
        detail = "A database integrity or transaction constraint error occurred."
        status_code = 400
        title = "Database Error"

    return JSONResponse(
        status_code=status_code,
        content={
            "type": "https://propledger.com/errors/db-error",
            "title": title,
            "status": status_code,
            "detail": detail,
            "instance": request.url.path,
            "code": getattr(exc, "pgcode", "DB_ERROR")
        },
        headers={"Content-Type": "application/problem+json"}
    )

async def general_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unhandled exception on {request.url.path}: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "type": "https://propledger.com/errors/internal-server-error",
            "title": "Internal Server Error",
            "status": 500,
            "detail": "An unexpected server error occurred. Please contact support.",
            "instance": request.url.path,
            "code": "INTERNAL_SERVER_ERROR"
        },
        headers={"Content-Type": "application/problem+json"}
    )
