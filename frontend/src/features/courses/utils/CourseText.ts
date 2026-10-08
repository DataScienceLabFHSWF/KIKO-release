// frontend/src/features/courses/utils/CourseText.ts

export function stripMarkdownFormatting(value?: string | null) {
  if (!value) return "";

  return value
    .replace(/^#+\s+/gm, "")
    .replace(/^>\s+/gm, "")
    .replace(/\*\*(.+?)\*\*/g, "$1")
    .replace(/\*(.+?)\*/g, "$1")
    .replace(/\[([^\]]+)\]\([^)]+\)/g, "$1")
    .trim();
}

export function shortenText(value?: string | null, maxLength = 260) {
  const plain = stripMarkdownFormatting(value);

  if (plain.length <= maxLength) return plain;

  return `${plain.slice(0, maxLength).trim()}…`;
}

export function safePercent(value: unknown) {
  const numeric = Number(value);

  if (!Number.isFinite(numeric)) return 0;

  return Math.max(0, Math.min(100, Math.round(numeric)));
}
