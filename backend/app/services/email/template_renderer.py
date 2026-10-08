# backend/app/services/email/template_renderer.py

from pathlib import Path
from typing import Any
from jinja2 import Environment, FileSystemLoader, select_autoescape

class EmailTemplateRenderer:
    def __init__(self) -> None:
        template_root = (
            Path(__file__).resolve().parents[2]
            / "core"
            / "email_templates"
        )

        self.env = Environment(
            loader=FileSystemLoader(str(template_root)),
            autoescape=select_autoescape(["html", "xml"]),
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def _safe_language(self, language: str | None) -> str:
        if language and language.lower().startswith("de"):
            return "de"

        return "en"

    def render(
        self,
        template_key: str,
        language: str | None,
        context: dict[str, Any],
    ) -> tuple[str, str, str]:
        safe_language = self._safe_language(language)

        subject_template = self.env.get_template(
            f"{safe_language}/{template_key}.subject.txt"
        )
        html_template = self.env.get_template(
            f"{safe_language}/{template_key}.html"
        )
        text_template = self.env.get_template(
            f"{safe_language}/{template_key}.txt"
        )

        subject = subject_template.render(**context).strip()
        html_body = html_template.render(**context).strip()
        text_body = text_template.render(**context).strip()

        return subject, html_body, text_body
