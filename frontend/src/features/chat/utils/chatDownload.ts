// frontend/src/features/chat/utils/chatDownload.ts

import type { ChatSourceDocument } from "../types/Chat";

function sanitizeFileName(value: string) {
  return value
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9-_]+/gi, "-")
    .replace(/^-+|-+$/g, "")
    .slice(0, 80);
}

function downloadTextFile(fileName: string, content: string, mimeType: string) {
  const blob = new Blob([content], { type: mimeType });
  const url = URL.createObjectURL(blob);

  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = fileName;
  anchor.click();

  URL.revokeObjectURL(url);
}

export function downloadAssistantMessageAsMarkdown(content: string) {
  const timestamp = new Date().toISOString().replace(/[:.]/g, "-");
  downloadTextFile(
    `kiko-chat-response-${timestamp}.md`,
    content,
    "text/markdown;charset=utf-8",
  );
}

export function downloadSourceSnippetAsMarkdown(source: ChatSourceDocument) {
  const title =
    source.source ?? source.title ?? source.module_title ?? "kiko-source";

  const fileName = `${sanitizeFileName(title) || "kiko-source"}.md`;

  const content = [
    `# ${title}`,
    "",
    source.module_title ? `**Module:** ${source.module_title}` : null,
    source.document_id ? `**Document ID:** ${source.document_id}` : null,
    "",
    "## Retrieved content",
    "",
    source.retrieved_chunks ?? "",
  ]
    .filter(Boolean)
    .join("\n");

  downloadTextFile(fileName, content, "text/markdown;charset=utf-8");
}
