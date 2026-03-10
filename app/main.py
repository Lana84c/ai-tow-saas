from fastapi import FastAPI

from app.api.router import api_router
from app.core.config import settings
from app.middleware.tenant_context import TenantMiddleware


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    description="AI-powered towing dispatch platform",
)

# Tenant middleware
app.add_middleware(TenantMiddleware)

# API routes
app.include_router(api_router, prefix="/api")


@app.get("/")
def root():
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }