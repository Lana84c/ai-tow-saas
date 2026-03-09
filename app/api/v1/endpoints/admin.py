from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def admin_root():
    return {"message": "Admin endpoint working"}