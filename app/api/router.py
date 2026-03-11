from fastapi import APIRouter

from app.api.v1.endpoints import (
    admin,
    auth,
    dispatch,
    driver,
    public_chat,
    service_requests,
    tenants,
)

api_router = APIRouter()

api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["Auth"],
)

api_router.include_router(
    public_chat.router,
    prefix="/chat",
    tags=["Customer Chat"],
)

api_router.include_router(
    service_requests.router,
    prefix="/requests",
    tags=["Service Requests"],
)

api_router.include_router(
    dispatch.router,
    prefix="/dispatch",
    tags=["Dispatch"],
)

api_router.include_router(
    driver.router,
    prefix="/driver",
    tags=["Driver"],
)

api_router.include_router(
    tenants.router,
    prefix="/tenants",
    tags=["Tenants"],
)

api_router.include_router(
    admin.router,
    prefix="/admin",
    tags=["Admin"],
)