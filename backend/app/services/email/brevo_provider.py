# backend/app/services/email/brevo_provider.py

import logging
import httpx
from app.core import get_email_settings
from .email_provider import EmailMessage

logger = logging.getLogger(__name__)

class BrevoEmailProvider:
    """
    Brevo transactional email provider.

    Uses Brevo's transactional email API instead of SMTP.
    """

    def __init__(self) -> None:
        self.settings = get_email_settings()

        if not self.settings.brevo_api_key:
            raise RuntimeError(
                "BREVO_API_KEY is required when EMAIL_PROVIDER=brevo."
            )

    async def send(self, message: EmailMessage) -> None:
        payload: dict = {
            "sender": {
                "name": self.settings.from_name,
                "email": self.settings.from_address,
            },
            "to": [
                {
                    "email": message.to_email,
                    "name": message.to_name or message.to_email,
                }
            ],
            "subject": message.subject,
            "htmlContent": message.html_body,
            "textContent": message.text_body,
        }

        if message.reply_to:
            payload["replyTo"] = {
                "email": message.reply_to,
            }

        if message.template_key:
            payload["tags"] = [
                self.settings.app_env,
                message.template_key,
            ]

        headers = {
            "accept": "application/json",
            "api-key": self.settings.brevo_api_key,
            "content-type": "application/json",
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.settings.brevo_api_url,
                    headers=headers,
                    json=payload,
                )

            if response.status_code == 401:
                logger.error(
                    "❌ Brevo authentication failed. "
                    "Check BREVO_API_KEY. Use a Brevo API key, not an SMTP key. "
                    "Response=%s",
                    response.text[:500],
                )
                response.raise_for_status()

            if response.status_code >= 400:
                logger.error(
                    "❌ Brevo email failed. status=%s response=%s",
                    response.status_code,
                    response.text[:500],
                )
                response.raise_for_status()

            response_data = response.json() if response.content else {}

            logger.info(
                "✅ Brevo email sent. to=%s subject=%s message_id=%s",
                message.to_email,
                message.subject,
                response_data.get("messageId"),
            )

        except httpx.HTTPError as exc:
            logger.exception("❌ Brevo email delivery failed.")
            raise RuntimeError("Brevo email delivery failed.") from exc
