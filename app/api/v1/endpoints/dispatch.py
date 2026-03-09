from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def dispatch_root():
    return {"message": "Dispatch endpoint working"}