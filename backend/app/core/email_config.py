# backend/app/core/email_config.py

import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

def _get_int_env(name: str, default: int) -> int:
    raw_value = os.getenv(name)

    if raw_value is None:
        return default

    try:
        return int(raw_value)
    except ValueError:
        return default

def _get_bool_env(name: str, default: bool) -> bool:
    raw_value = os.getenv(name)

    if raw_value is None:
        return default

    return raw_value.strip().lower() in {"1", "true", "yes", "on"}

@dataclass(frozen=True)
class EmailSettings:
    app_env: str
    provider: str
    from_name: str
    from_address: str
    reply_to: str | None
    frontend_public_url: str
    password_reset_token_expire_minutes: int
    email_verification_token_expire_minutes: int
    brevo_api_key: str | None
    brevo_api_url: str
    email_redirect_all_to: str | None
    email_sending_enabled: bool
    welcome_email_enabled: bool

def get_email_settings() -> EmailSettings:
    return EmailSettings(
        app_env= os.getenv("APP_ENV", "development").strip().lower(),

        provider= os.getenv("EMAIL_PROVIDER", "console").strip().lower(),

        from_name= os.getenv("EMAIL_FROM_NAME", "KIKO Platform").strip(),

        from_address= os.getenv(
            "EMAIL_FROM_ADDRESS",
            "no-reply@kiko.local",
        ).strip(),

        reply_to= os.getenv("EMAIL_REPLY_TO") or None,

        frontend_public_url= os.getenv(
            "FRONTEND_PUBLIC_URL",
            "http://localhost:8003",
        ).rstrip("/"),

        password_reset_token_expire_minutes=_get_int_env(
            "PASSWORD_RESET_TOKEN_EXPIRE_MINUTES",
            30,
        ),

        email_verification_token_expire_minutes=_get_int_env(
            "EMAIL_VERIFICATION_TOKEN_EXPIRE_MINUTES",
            1440,
        ),

        brevo_api_key= os.getenv("BREVO_API_KEY") or None,

        brevo_api_url= os.getenv(
            "BREVO_API_URL",
            "https://api.brevo.com/v3/smtp/email",
        ).strip(),

        # Stage safety: redirect all stage emails to one test inbox.
        email_redirect_all_to= os.getenv("EMAIL_REDIRECT_ALL_TO") or None,

        # Emergency switch.
        email_sending_enabled=_get_bool_env("EMAIL_SENDING_ENABLED", True),

        welcome_email_enabled=_get_bool_env("WELCOME_EMAIL_ENABLED", True),

    )
