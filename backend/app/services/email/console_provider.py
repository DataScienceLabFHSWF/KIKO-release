# backend/app/services/email/console_provider.py

import logging
from .email_provider import EmailMessage

logger = logging.getLogger(__name__)

class ConsoleEmailProvider:
    """
    Development-only email provider.

    It does not send a real email.
    It logs the rendered email content so we can test the flow safely.
    """

    async def send(self, message: EmailMessage) -> None:
        logger.info(
            "\n"
            "================ KIKO EMAIL DEBUG ================\n"
            "To: %s\n"
            "Name: %s\n"
            "Subject: %s\n"
            "Reply-To: %s\n"
            "---------------- TEXT BODY ----------------\n"
            "%s\n"
            "---------------- HTML BODY ----------------\n"
            "%s\n"
            "==================================================",
            message.to_email,
            message.to_name or "-",
            message.subject,
            message.reply_to or "-",
            message.text_body,
            message.html_body,
        )
