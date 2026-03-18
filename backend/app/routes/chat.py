from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.db import SessionLocal
from app.schemas.message import ChatRequest, ChatResponse, MessageResponse
from app.services.chat import chat, chat_stream

router = APIRouter(prefix="/chat", tags=["chat"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("", response_model=ChatResponse)
def send_message(request: ChatRequest, db: Session = Depends(get_db)):
    # TODO: Replace hardcoded user_id with authenticated user once auth is built
    TEMP_USER_ID = "00000000-0000-0000-0000-000000000001"

    try:
        conversation, message = chat(
            user_message=request.message,
            db=db,
            user_id=TEMP_USER_ID,
            conversation_id=str(request.conversation_id) if request.conversation_id else None,
            language_code=request.language_code,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return ChatResponse(
        conversation_id=conversation.id,
        message=MessageResponse.model_validate(message),
    )


@router.post("/stream")
def send_message_stream(request: ChatRequest, db: Session = Depends(get_db)):
    # TODO: Replace hardcoded user_id with authenticated user once auth is built
    TEMP_USER_ID = "00000000-0000-0000-0000-000000000001"

    try:
        generator = chat_stream(
            user_message=request.message,
            db=db,
            user_id=TEMP_USER_ID,
            conversation_id=str(request.conversation_id) if request.conversation_id else None,
            language_code=request.language_code,
        )
        return StreamingResponse(generator, media_type="text/event-stream")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
