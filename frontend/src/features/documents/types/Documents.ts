// frontend/src/features/documents/types/Documents.ts

export type DocumentCardAction = "preview" | "download" | "delete";

export type DocumentItem = {
  document_id: number;
  file_name: string;
  content_hash: string;
  storage_path?: string | null;
  status?: string | null;
  uploaded_at: string;
  processing_stats?: Record<string, unknown> | null;
};

export type MarkdownPreviewResponse = {
  title?: string | null;
  summary?: string | null;
  markdown?: string | null;
  content?: string | null;
  modules?: unknown;
  questions?: unknown;
  quiz?: unknown;
  [key: string]: unknown;
};

export type DocumentPreview =
  | {
      type: "image";
      title: string;
      objectUrl: string;
    }
  | {
      type: "markdown";
      title: string;
      content: string;
    };
