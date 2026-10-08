# backend/app/services/email_verification_token_service.py

import hashlib, secrets
from datetime import datetime, timedelta, timezone
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import EmailVerificationTokenModel

def generate_raw_email_verification_token() -> str:
    return secrets.token_urlsafe(48)

def hash_email_verification_token(raw_token: str) -> str:
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()

async def create_email_verification_token(
    *,
    user_id: int,
    db: AsyncSession,
    expires_minutes: int,
    requested_ip: str | None = None,
    user_agent: str | None = None,
) -> str:
    now = datetime.now(timezone.utc)

    await db.execute(
        update(EmailVerificationTokenModel)
        .where(
            EmailVerificationTokenModel.user_id == user_id,
            EmailVerificationTokenModel.used_at.is_(None),
        )
        .values(used_at=now)
    )

    raw_token = generate_raw_email_verification_token()

    token = EmailVerificationTokenModel(
        user_id=user_id,
        token_hash=hash_email_verification_token(raw_token),
        expires_at=now + timedelta(minutes=expires_minutes),
        requested_ip=requested_ip,
        user_agent=user_agent,
    )

    db.add(token)
    await db.commit()

    return raw_token

async def get_valid_email_verification_token(
    *,
    raw_token: str,
    db: AsyncSession,
) -> EmailVerificationTokenModel | None:
    token_hash = hash_email_verification_token(raw_token)
    now = datetime.now(timezone.utc)

    result = await db.execute(
        select(EmailVerificationTokenModel)
        .where(
            EmailVerificationTokenModel.token_hash == token_hash,
            EmailVerificationTokenModel.used_at.is_(None),
            EmailVerificationTokenModel.expires_at > now,
        )
    )

    return result.scalar_one_or_none()
