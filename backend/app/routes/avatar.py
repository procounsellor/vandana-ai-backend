import base64
import json
import re
from concurrent.futures import ThreadPoolExecutor
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from openai import OpenAI
from sqlalchemy.orm import Session

from app.config import OPENAI_API_KEY
from app.db import SessionLocal
from app.dependencies import get_current_user_id
from app.models import Conversation, Message
from app.models.message import MessageRole
from app.schemas.message import ChatRequest, MessageResponse
from app.services.chat import chat, build_verse_context, get_conversation_history, get_system_prompt, suggest_scripture
from app.services.embedding import get_embedding
from app.services.search import search_verses, search_verses_by_embedding
from app.services.sarvam import (
    text_to_speech, text_to_speech_stream, speech_to_text,
    _clean_for_tts, _tts_chunk, LANGUAGE_MAP, TTS_SPEAKERS,
)
router = APIRouter(prefix="/avatar", tags=["avatar"])

_openai = OpenAI(api_key=OPENAI_API_KEY)

# Sentence boundary: ., ।, ॥, ?, ! followed by whitespace
_SENTENCE_END = re.compile(r'[.।॥?!]\s+')


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/chat")
def avatar_chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    try:
        conversation, message = chat(
            user_message=request.message,
            db=db,
            user_id=user_id,
            conversation_id=str(request.conversation_id) if request.conversation_id else None,
            language_code=request.language_code,
            scripture_short_name=request.scripture_short_name,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    audio_chunks = text_to_speech(message.content, language_code=request.language_code)

    return {
        "conversation_id": str(conversation.id),
        "message": MessageResponse.model_validate(message),
        "audio_chunks": [base64.b64encode(c).decode("utf-8") for c in audio_chunks],
    }


@router.post("/voice/stream")
async def avatar_voice_stream(
    audio: UploadFile = File(...),
    conversation_id: str = Form(None),
    language_code: str = Form("en"),
    scripture_short_name: str = Form(None),
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """
    Pipelined voice endpoint:
      STT → GPT stream → TTS per sentence (parallel) → SSE audio chunks
    Audio starts playing as soon as the first sentence is synthesised,
    while GPT is still generating the rest of the response.
    """
    audio_bytes = await audio.read()
    try:
        user_text = speech_to_text(audio_bytes, filename=audio.filename, language_code=language_code)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if not user_text:
        raise HTTPException(status_code=400, detail="Could not transcribe audio")

    # Fire embedding call immediately in background — runs while we do DB setup
    with ThreadPoolExecutor(max_workers=1) as embed_pool:
        embed_future = embed_pool.submit(get_embedding, user_text)

        # DB setup runs in parallel with embedding
        if conversation_id:
            conversation = db.query(Conversation).filter_by(id=conversation_id, user_id=user_id).first()
            if not conversation:
                raise HTTPException(status_code=404, detail="Conversation not found")
            if not scripture_short_name:
                scripture_short_name = conversation.scripture_short_name
        else:
            conversation = Conversation(
                user_id=user_id,
                language_code=language_code,
                scripture_short_name=scripture_short_name or "gita",
            )
            db.add(conversation)
            db.flush()

        # Capture history BEFORE adding current user message to avoid duplication
        history = get_conversation_history(conversation)

        user_msg = Message(conversation_id=conversation.id, role=MessageRole.user, content=user_text)
        db.add(user_msg)
        db.flush()

        # Embedding should be ready by now (or very close)
        query_embedding = embed_future.result()

    relevant_verses = search_verses_by_embedding(
        query_embedding, db, top_k=2,
        scripture_short_names=[scripture_short_name or "gita"],
    )
    verse_context = build_verse_context(relevant_verses, language_code=language_code, scripture_short_name=scripture_short_name)
    cited_verse_ids = [str(v.id) for v in relevant_verses]

    from app.services.chat import get_scripture_config
    config = get_scripture_config(scripture_short_name)
    gpt_messages = [
        {"role": "system", "content": get_system_prompt(language_code, scripture_short_name)},
        {"role": "system", "content": f"Relevant passages from the {config['context_label']}:\n\n{verse_context}"},
        *history,
        {"role": "user", "content": user_text},
    ]

    sarvam_lang = LANGUAGE_MAP.get(language_code, "en-IN")
    speaker = TTS_SPEAKERS.get(language_code, "anushka")
    conv_id = str(conversation.id)

    def generate():
        yield f"data: {json.dumps({'type': 'meta', 'transcript': user_text, 'conversation_id': conv_id})}\n\n"

        full_content = []
        buffer = ""
        pending: dict[int, object] = {}
        submitted = 0
        yielded = 0

        def submit_sentence(text: str):
            nonlocal submitted
            clean = _clean_for_tts(text).strip()
            if clean:
                idx = submitted
                submitted += 1
                pending[idx] = tts_pool.submit(_tts_chunk, clean, sarvam_lang, speaker)

        def flush_ready():
            nonlocal yielded
            while yielded in pending and pending[yielded].done():
                wav = pending.pop(yielded).result()
                yielded += 1
                if wav:
                    yield f"data: {json.dumps({'type': 'audio', 'chunk': base64.b64encode(wav).decode('utf-8')})}\n\n"

        with ThreadPoolExecutor(max_workers=6) as tts_pool:
            gpt_stream = _openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=gpt_messages,
                temperature=0.7,
                stream=True,
            )

            for token in gpt_stream:
                delta = token.choices[0].delta.content or ""
                full_content.append(delta)
                buffer += delta

                # Submit TTS for each complete sentence as GPT produces it
                while True:
                    m = _SENTENCE_END.search(buffer)
                    if not m:
                        break
                    submit_sentence(buffer[:m.end()])
                    buffer = buffer[m.end():]

                yield from flush_ready()

            # Flush remaining buffer (last sentence may not end with punctuation)
            if buffer.strip():
                submit_sentence(buffer.strip())

            # Drain remaining TTS futures in order
            for i in range(yielded, submitted):
                if i in pending:
                    wav = pending[i].result()
                    if wav:
                        yield f"data: {json.dumps({'type': 'audio', 'chunk': base64.b64encode(wav).decode('utf-8')})}\n\n"

        # Save full response to DB
        assistant_content = "".join(full_content)
        if not conversation.title:
            conversation.title = user_text[:60] + ("..." if len(user_text) > 60 else "")
        assistant_msg = Message(
            conversation_id=conversation.id,
            role=MessageRole.assistant,
            content=assistant_content,
            cited_verses=cited_verse_ids,
        )
        db.add(assistant_msg)
        db.commit()

        yield f"data: {json.dumps({'type': 'done', 'message': assistant_content})}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


@router.get("/scriptures")
def list_scriptures(db: Session = Depends(get_db)):
    """List all available scriptures."""
    from app.models import Scripture
    from app.services.chat import SCRIPTURE_PROMPTS
    scriptures = db.query(Scripture).all()
    seeded = {s.short_name for s in scriptures}
    return [
        {
            "short_name": key,
            "name": val["name"],
            "available": key in seeded,
        }
        for key, val in SCRIPTURE_PROMPTS.items()
    ]


@router.post("/suggest-scripture")
def suggest_scripture_endpoint(body: dict):
    """Suggest the best scripture for a user's message."""
    message = body.get("message", "")
    if not message:
        return {"scripture_short_name": "gita"}
    suggested = suggest_scripture(message)
    from app.services.chat import SCRIPTURE_PROMPTS
    return {
        "scripture_short_name": suggested,
        "name": SCRIPTURE_PROMPTS[suggested]["name"],
    }
