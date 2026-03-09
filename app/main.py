from fastapi import FastAPI

from app.api.router import api_router
from app.core.config import settings
from app.db.base import Base
from app.db.session import engine
from app.middleware.tenant_context import TenantMiddleware

app = FastAPI(
    title="AI Tow Dispatch SaaS",
    version="1.0.0",
    debug=settings.DEBUG,
    description="AI-powered towing dispatch platform",
)

app.add_middleware(TenantMiddleware)

app.include_router(api_router, prefix="/api")


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


@app.get("/health")
def health():
    return {"status": "healthy"}