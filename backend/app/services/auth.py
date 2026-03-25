import requests
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app.config import GOOGLE_CLIENT_ID, JWT_SECRET, JWT_ALGORITHM
from app.models.user import User


GOOGLE_TOKEN_INFO_URL = "https://oauth2.googleapis.com/tokeninfo"


def verify_google_token(id_token: str) -> dict:
    """Verify Google ID token and return the payload."""
    resp = requests.get(GOOGLE_TOKEN_INFO_URL, params={"id_token": id_token}, timeout=10)
    if not resp.ok:
        raise ValueError("Invalid Google token")
    payload = resp.json()
    if GOOGLE_CLIENT_ID and payload.get("aud") != GOOGLE_CLIENT_ID:
        raise ValueError("Token audience mismatch")
    return payload


def get_or_create_user(db: Session, google_payload: dict) -> User:
    """Find existing user by google_id or email, or create a new one."""
    google_id = google_payload.get("sub")
    email = google_payload.get("email")

    user = db.query(User).filter_by(google_id=google_id).first()
    if not user and email:
        user = db.query(User).filter_by(email=email).first()

    if user:
        # Update profile fields if changed
        user.google_id = google_id
        user.name = user.name or google_payload.get("name")
        user.picture = google_payload.get("picture")
        db.commit()
        db.refresh(user)
    else:
        user = User(
            google_id=google_id,
            email=email,
            name=google_payload.get("name"),
            picture=google_payload.get("picture"),
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    return user


def create_jwt(user_id: str) -> str:
    """Create a non-expiring JWT for the given user_id."""
    return jwt.encode({"sub": user_id}, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_jwt(token: str) -> str | None:
    """Decode JWT and return user_id, or None if invalid."""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload.get("sub")
    except JWTError:
        return None
