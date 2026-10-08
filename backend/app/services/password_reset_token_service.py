# backend/app/services/password_reset_token_service.py

import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import PasswordResetTokenModel, UserModel

def generate_raw_password_reset_token() -> str:
    return secrets.token_urlsafe(48)

def hash_password_reset_token(raw_token: str) -> str:
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()

async def create_password_reset_token(
    *,
    user_id: int,
    db: AsyncSession,
    expires_minutes: int,
    requested_ip: str | None = None,
    user_agent: str | None = None,
) -> str:
    now = datetime.now(timezone.utc)

    # Invalidate older active tokens for this user.
    await db.execute(
        update(PasswordResetTokenModel)
        .where(
            PasswordResetTokenModel.user_id == user_id,
            PasswordResetTokenModel.used_at.is_(None),
        )
        .values(used_at=now)
    )

    raw_token = generate_raw_password_reset_token()
    token_hash = hash_password_reset_token(raw_token)

    reset_token = PasswordResetTokenModel(
        user_id=user_id,
        token_hash=token_hash,
        expires_at=now + timedelta(minutes=expires_minutes),
        requested_ip=requested_ip,
        user_agent=user_agent[:512] if user_agent else None,
    )

    db.add(reset_token)
    await db.commit()

    return raw_token

async def get_valid_password_reset_token(
    *,
    raw_token: str,
    db: AsyncSession,
) -> PasswordResetTokenModel:
    token_hash = hash_password_reset_token(raw_token)
    now = datetime.now(timezone.utc)

    result = await db.execute(
        select(PasswordResetTokenModel).where(
            PasswordResetTokenModel.token_hash == token_hash,
            PasswordResetTokenModel.used_at.is_(None),
            PasswordResetTokenModel.expires_at > now,
        )
    )

    reset_token = result.scalar_one_or_none()

    if not reset_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="❌ Invalid or expired password reset link.",
        )

    return reset_token

async def get_user_based_token_id(db: AsyncSession, user_id: int) -> UserModel | None:
    result = await db.execute(
        select(UserModel)
        .where(UserModel.user_id == user_id)
    )

    return result.scalar_one_or_none()
