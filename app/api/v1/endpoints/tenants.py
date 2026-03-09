from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def tenants_root():
    return {"message": "Tenants endpoint working"}