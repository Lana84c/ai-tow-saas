from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_roles
from app.db.models.driver import Driver
from app.db.models.user import User

router = APIRouter()


@router.get("/drivers/map")
def get_driver_map(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("tenant_admin", "dispatcher")),
):
    tenant_id = getattr(request.state, "tenant_id", None)

    query = db.query(Driver)

    if tenant_id:
        query = query.filter(Driver.tenant_id == tenant_id)

    drivers = query.all()

    result = []

    for d in drivers:
        if d.current_latitude and d.current_longitude:
            result.append(
                {
                    "driver_id": d.id,
                    "name": d.name,
                    "truck_number": d.truck_number,
                    "latitude": d.current_latitude,
                    "longitude": d.current_longitude,
                    "available": d.is_available,
                }
            )

    return result