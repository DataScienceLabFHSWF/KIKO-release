# backend/app/services/security_service.py
# JWT Utilities

import os, logging
from typing import Optional
from fastapi import HTTPException, status, Depends, Header
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from datetime import timedelta, timezone, datetime
from jose import ExpiredSignatureError, JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models import UserModel

logger = logging.getLogger(__name__)

TOKEN_SECRET_KEY = os.getenv("SECRET_KEY")
TOKEN_ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/authentication/authenticate")

def _require_secret_key() -> str:
    if not TOKEN_SECRET_KEY:
        raise RuntimeError("SECRET_KEY environment variable is required.")
    return TOKEN_SECRET_KEY

def datetime_to_token_timestamp(value: datetime | None) -> int:
    """
    Convert password_changed_at to a stable integer timestamp.

    None means password was never changed after registration/reset.
    """
    if value is None:
        return 0

    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)

    return int(value.timestamp())

async def create_access_token(
    data: dict,
    expires_delta: timedelta | None = None,
) -> str:
    """
    Create a JWT access token with expiry.

    Required claims are added here:
    - exp: token expiry
    - iat: issued-at timestamp
    - type: token type
    """
    now = datetime.now(timezone.utc)
    expire = now + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    to_encode = data.copy()
    to_encode.update(
        {
            "exp": expire,
            "iat": now,
            "type": "access",
        }
    )

    return jwt.encode(
        to_encode,
        _require_secret_key(),
        algorithm=TOKEN_ALGORITHM,
    )

async def decode_access_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(
            token,
            _require_secret_key(),
            algorithms=[TOKEN_ALGORITHM],
        )

        if payload.get("type") != "access":
            return None

        return payload

    except ExpiredSignatureError:
        logger.info("JWT access token expired.")
        return None

    except JWTError:
        logger.info("Invalid JWT access token.")
        return None

async def _get_user_from_token_payload(
    payload: dict,
    db: AsyncSession,
) -> UserModel | None:
    user_id = payload.get("sub")

    if user_id is not None:
        try:
            result = await db.execute(
                select(UserModel).where(UserModel.user_id == int(user_id))
            )
            return result.scalar_one_or_none()
        except (TypeError, ValueError):
            return None

    email = payload.get("email")

    if not email:
        return None

    result = await db.execute(
        select(UserModel)
        .where(UserModel.email == email.lower().strip())
    )

    return result.scalar_one_or_none()

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
):
    """
    Validate JWT and return the current user.

    Also invalidates old tokens when password_changed_at is newer than the
    timestamp stored in the token.
    """
    payload = await decode_access_token(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token.",
        )

    db_user = await _get_user_from_token_payload(payload, db)

    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token.",
        )

    token_password_changed_at = int(payload.get("pwd_changed_at") or 0)
    current_password_changed_at = datetime_to_token_timestamp(
        db_user.password_changed_at
    )

    if token_password_changed_at < current_password_changed_at:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired because password was changed.",
        )

    return {
        "user_id": db_user.user_id,
        "email": db_user.email,
        "role": db_user.role,
    }

# 🎯 Role checker
def require_role(allowed_roles: list):
    """Decorator to check if the user has one of the allowed roles.
    This function returns a dependency that checks the user's role against the allowed roles.
    If the user's role is not in the allowed roles, it raises an HTTPException with a HTTP_403_FORBIDDEN status code."""
    
    async def role_checker(user=Depends(get_current_user)):
        """Check if the current user has one of the allowed roles."""
        
        if user["role"] not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied for role: {user['role']}",
            )
        return user
    return role_checker

def get_request_lang(accept_language: Optional[str] = Header(default=None, alias="Accept-Language"),) -> str:
    
    if not accept_language:
        return "en"
    
    first_language = accept_language.split(",")[0].strip().lower()
    
    if first_language.startswith("de"):
        return "de"
    
    return "en"
