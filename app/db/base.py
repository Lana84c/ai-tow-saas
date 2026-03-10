from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


# Import models so they are registered with Base.metadata
from app.db.models.dispatch_job import DispatchJob  # noqa: E402,F401
from app.db.models.driver import Driver  # noqa: E402,F401
from app.db.models.service_request import ServiceRequest  # noqa: E402,F401