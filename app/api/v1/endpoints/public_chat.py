from fastapi import APIRouter

from app.schemas.chat import ChatRequest, ChatResponse
from app.services.ai.ai_dispatcher import handle_customer_message

router = APIRouter()


@router.post("/", response_model=ChatResponse)
def customer_chat(payload: ChatRequest) -> ChatResponse:
    return handle_customer_message(payload.message)