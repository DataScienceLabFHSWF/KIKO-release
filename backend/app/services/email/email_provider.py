# backend/app/services/email/email_provider.py

from dataclasses import dataclass
from typing import Protocol

@dataclass(frozen=True)
class EmailMessage:
    to_email: str
    subject: str
    html_body: str
    text_body: str
    to_name: str | None = None
    reply_to: str | None = None
    template_key: str | None = None

class EmailProvider(Protocol):
    async def send(self, message: EmailMessage) -> None:
        """Send an email message."""
