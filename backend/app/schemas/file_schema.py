# backend/app/schemas/file_schema.py
from typing import Any
from pydantic import BaseModel, Field

class MarkdownPreviewResponse(BaseModel):
    """
    Schema for markdown preview response.
    This schema is used to return the rendered markdown content along with any relevant metadata, such as 
    the original markdown text, a summary, quiz information, and extracted questions. It allows the frontend to
    display a preview of the markdown content, including any generated quizzes or questions, 
    before it is finalized and saved.
    """
    file_name: str
    content: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    summary: str | None = None
    quiz: dict[str, Any] | None = None
    quiz_yaml: str | None = None
    questions: list[dict[str, Any]] = Field(default_factory=list)
    raw_markdown: str
