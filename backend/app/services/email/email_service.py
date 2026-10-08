# backend/app/services/email/email_service.py
import logging
from typing import Any
from app.core import get_email_settings
from .brevo_provider import BrevoEmailProvider
from .console_provider import ConsoleEmailProvider
from .email_provider import EmailMessage, EmailProvider
from .template_renderer import EmailTemplateRenderer

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self) -> None:
        self.settings = get_email_settings()
        self.renderer = EmailTemplateRenderer()
        self.provider = self._build_provider()

    def _build_provider(self) -> EmailProvider:
        if self.settings.provider == "console":
            return ConsoleEmailProvider()

        if self.settings.provider == "brevo":
            return BrevoEmailProvider()

        logger.warning(
            "Unsupported EMAIL_PROVIDER=%s. Falling back to console provider.",
            self.settings.provider,
        )
        return ConsoleEmailProvider()

    def _resolve_recipient(
        self,
        *,
        to_email: str,
        to_name: str | None,
        context: dict[str, Any],
    ) -> tuple[str, str | None, dict[str, Any]]:
        """
        Stage safety.

        When EMAIL_REDIRECT_ALL_TO is set outside production, all emails go
        to one test inbox, while the original recipient is kept in the template.
        """

        if (
            self.settings.app_env != "production"
            and self.settings.email_redirect_all_to
        ):
            logger.info(
                "ℹ️ Redirecting email in %s from %s to %s",
                self.settings.app_env,
                to_email,
                self.settings.email_redirect_all_to,
            )

            return (
                self.settings.email_redirect_all_to,
                "KIKO Stage Tester",
                {
                    **context,
                    "original_recipient_email": to_email,
                    "original_recipient_name": to_name,
                },
            )

        return to_email, to_name, context

    async def send_template_email(
        self,
        *,
        to_email: str,
        template_key: str,
        language: str,
        context: dict[str, Any],
        to_name: str | None = None,
    ) -> None:
        if not self.settings.email_sending_enabled:
            logger.warning(
                "⚠️ Email sending is disabled. template=%s to=%s",
                template_key,
                to_email,
            )
            return

        final_to_email, final_to_name, final_context = self._resolve_recipient(
            to_email=to_email,
            to_name=to_name,
            context=context,
        )

        full_context = {
            "app_name": "KIKO Platform",
            "from_name": self.settings.from_name,
            **final_context,
        }

        subject, html_body, text_body = self.renderer.render(
            template_key=template_key,
            language=language,
            context=full_context,
        )

        message = EmailMessage(
            to_email=final_to_email,
            to_name=final_to_name,
            subject=subject,
            html_body=html_body,
            text_body=text_body,
            reply_to=self.settings.reply_to,
            template_key=template_key,
        )

        await self.provider.send(message)
