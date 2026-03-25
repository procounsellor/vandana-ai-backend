from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.db import SessionLocal
from app.dependencies import get_current_user_id, GUEST_USER_ID
from app.models import Conversation, Message

router = APIRouter(prefix="/conversations", tags=["conversations"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("")
def list_conversations(
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Return the user's conversations, newest first."""
    if user_id == GUEST_USER_ID:
        return []

    convs = (
        db.query(Conversation)
        .filter_by(user_id=user_id)
        .order_by(Conversation.updated_at.desc())
        .limit(50)
        .all()
    )
    return [
        {
            "id": str(c.id),
            "title": c.title or "Untitled",
            "language_code": c.language_code,
            "updated_at": c.updated_at.isoformat(),
        }
        for c in convs
    ]


@router.get("/{conversation_id}")
def get_conversation(
    conversation_id: str,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Return a conversation with all its messages."""
    conv = (
        db.query(Conversation)
        .options(joinedload(Conversation.messages))
        .filter_by(id=conversation_id, user_id=user_id)
        .first()
    )
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    return {
        "id": str(conv.id),
        "title": conv.title or "Untitled",
        "language_code": conv.language_code,
        "updated_at": conv.updated_at.isoformat(),
        "messages": [
            {
                "id": str(m.id),
                "role": m.role.value,
                "content": m.content,
                "created_at": m.created_at.isoformat(),
            }
            for m in conv.messages
        ],
    }


@router.delete("/{conversation_id}")
def delete_conversation(
    conversation_id: str,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Delete a conversation and all its messages."""
    conv = db.query(Conversation).filter_by(id=conversation_id, user_id=user_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    db.delete(conv)
    db.commit()
    return {"ok": True}
