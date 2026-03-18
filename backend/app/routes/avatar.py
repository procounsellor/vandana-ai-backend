import base64
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import requests as req

from app.db import SessionLocal
from app.schemas.message import ChatRequest, MessageResponse
from app.services.chat import chat
from app.services.sarvam import text_to_speech, speech_to_text
from app.services.simli import generate_avatar_video

router = APIRouter(prefix="/avatar", tags=["avatar"])

TEMP_USER_ID = "00000000-0000-0000-0000-000000000001"


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/proxy-video")
def proxy_video(url: str):
    """Proxy Simli video to avoid CORS issues in the browser."""
    response = req.get(url, stream=True, timeout=30)
    if not response.ok:
        raise HTTPException(status_code=response.status_code, detail="Video not found")
    return StreamingResponse(
        response.iter_content(chunk_size=8192),
        media_type="video/mp4",
        headers={"Cache-Control": "no-cache"},
    )


def try_generate_avatar(audio_bytes: bytes) -> dict:
    """Generate avatar video, returning empty dict if Simli fails (rate limit, etc.)."""
    try:
        return generate_avatar_video(audio_bytes)
    except Exception as e:
        print(f"Simli avatar skipped: {e}")
        return {}


@router.post("/chat")
def avatar_chat(request: ChatRequest, db: Session = Depends(get_db)):
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

    audio_chunks = text_to_speech(message.content, language_code=request.language_code)
    video_urls = try_generate_avatar(audio_chunks[0])

    return {
        "conversation_id": str(conversation.id),
        "message": MessageResponse.model_validate(message),
        "audio_chunks": [base64.b64encode(c).decode("utf-8") for c in audio_chunks],
        "video": {
            "mp4_url": video_urls.get("mp4_url"),
            "hls_url": video_urls.get("hls_url"),
        },
    }


@router.post("/voice")
async def avatar_voice_chat(
    audio: UploadFile = File(...),
    conversation_id: str = Form(None),
    language_code: str = Form("en"),
    db: Session = Depends(get_db),
):
    # Transcribe user voice
    audio_bytes = await audio.read()
    try:
        user_text = speech_to_text(audio_bytes, filename=audio.filename, language_code=language_code)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if not user_text:
        raise HTTPException(status_code=400, detail="Could not transcribe audio")

    try:
        conversation, message = chat(
            user_message=user_text,
            db=db,
            user_id=TEMP_USER_ID,
            conversation_id=conversation_id,
            language_code=language_code,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    audio_chunks = text_to_speech(message.content, language_code=language_code)
    video_urls = try_generate_avatar(audio_chunks[0])

    return {
        "conversation_id": str(conversation.id),
        "transcript": user_text,
        "message": MessageResponse.model_validate(message),
        "audio_chunks": [base64.b64encode(c).decode("utf-8") for c in audio_chunks],
        "video": {
            "mp4_url": video_urls.get("mp4_url"),
            "hls_url": video_urls.get("hls_url"),
        },
    }
