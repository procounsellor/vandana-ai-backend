from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db import SessionLocal
from app.services.auth import verify_google_token, get_or_create_user, create_jwt

router = APIRouter(prefix="/auth", tags=["auth"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class GoogleAuthRequest(BaseModel):
    id_token: str


@router.post("/google")
def google_login(body: GoogleAuthRequest, db: Session = Depends(get_db)):
    """Exchange a Google ID token for our app JWT."""
    try:
        payload = verify_google_token(body.id_token)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

    user = get_or_create_user(db, payload)
    token = create_jwt(str(user.id))

    return {
        "token": token,
        "user": {
            "id": str(user.id),
            "name": user.name,
            "email": user.email,
            "picture": user.picture,
        },
    }
