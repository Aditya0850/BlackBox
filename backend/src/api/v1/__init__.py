"""API v1 router with all endpoints."""
from fastapi import APIRouter

from .cases import router as cases_router
from .evidence import router as evidence_router

api_router = APIRouter()

# Include sub-routers
api_router.include_router(cases_router, prefix="/cases", tags=["cases"])
api_router.include_router(evidence_router, prefix="/evidence", tags=["evidence"])