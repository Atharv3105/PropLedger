from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth, properties, units, tenants, leases,
    payments, billing, collections, maintenance,
    finance, reports, diagnostics
)

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(properties.router)
api_router.include_router(units.router)
api_router.include_router(tenants.router)
api_router.include_router(leases.router)
api_router.include_router(payments.router)
api_router.include_router(billing.router)
api_router.include_router(collections.router)
api_router.include_router(maintenance.router)
api_router.include_router(finance.router)
api_router.include_router(reports.router)
api_router.include_router(diagnostics.router)
