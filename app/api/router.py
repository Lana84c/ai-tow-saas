from fastapi import APIRouter

from app.api.v1.endpoints import (
    admin,
    auth,
    dispatch,
    public_chat,
    service_requests,
    tenants,
)

api_router = APIRouter()

# Auth
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["Auth"],
)

# Public customer chat
api_router.include_router(
    public_chat.router,
    prefix="/chat",
    tags=["Customer Chat"],
)

# Service requests
api_router.include_router(
    service_requests.router,
    prefix="/requests",
    tags=["Service Requests"],
)

# Dispatch system
api_router.include_router(
    dispatch.router,
    prefix="/dispatch",
    tags=["Dispatch"],
)

# Tenants (towing companies)
api_router.include_router(
    tenants.router,
    prefix="/tenants",
    tags=["Tenants"],
)

# Admin
api_router.include_router(
    admin.router,
    prefix="/admin",
    tags=["Admin"],
)