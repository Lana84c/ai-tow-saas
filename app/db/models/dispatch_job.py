from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class DispatchJob(Base):
    __tablename__ = "dispatch_jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    tenant_id: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)

    service_request_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("service_requests.id"),
        nullable=False,
        index=True,
    )

    driver_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("drivers.id"),
        nullable=True,
        index=True,
    )

    status: Mapped[str] = mapped_column(String(50), nullable=False, default="assigned")
    estimated_distance_miles: Mapped[float | None] = mapped_column(Float, nullable=True)
    estimated_eta_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )