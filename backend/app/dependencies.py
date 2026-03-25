from fastapi import Header
from sqlalchemy.orm import Session

from app.models.user import User
from app.services.auth import decode_jwt

GUEST_USER_ID = "00000000-0000-0000-0000-000000000001"


def get_current_user_id(authorization: str = Header(default=None)) -> str:
    """
    Extract user_id from Bearer token.
    Returns GUEST_USER_ID if no token or invalid token.
    """
    if authorization and authorization.startswith("Bearer "):
        token = authorization.removeprefix("Bearer ")
        user_id = decode_jwt(token)
        if user_id:
            return user_id
    return GUEST_USER_ID
