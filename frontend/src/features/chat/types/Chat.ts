// frontend/src/features/chat/types/Chat.ts

export const DEFAULT_EMBEDDING_MODEL = "nomic-embed-text:v1.5";

export type ChatRole = "user" | "assistant" | "system";

export const CHAT_LLM_OPTIONS = [
  "llama3.3:70b",
  "nemotron:70b",
  "Apertus-8B-Instruct-2509",
  // "Soofi-S-Instruct-Preview",
] as const;

export type ChatLlmModel = (typeof CHAT_LLM_OPTIONS)[number];

export type ChatSourceDocument = {
  source?: string | null;
  content_hash?: string | null;
  file_path?: string | null;
  document_type?: string | null;
  document_id?: number | null;
  module_id?: string | null;
  module_title?: string | null;
  chunk_index_within_module?: number | null;
  total_chunks_within_module?: number | null;
  title?: string | null;
  retrieved_chunks?: string | null;
};

export type ChatQueryRequest = {
  query: string;
  embedding_model: string;
  llm_model: string;
};

export type ChatQueryResponse = {
  data: {
    answer: string;
    source_docs?: ChatSourceDocument[];
  };
};

export type ChatMessage = {
  id: string;
  role: ChatRole;
  content: string;
  sources?: ChatSourceDocument[];
  timestamp?: string | null;
};

export type ProcessUploadedDocsResponse = {
  message: "success";
  summary?: {
    processed: number;
    skipped_existing: number;
    failed: number;
    elapsed_sec: number;
  };
  files?: Array<{
    file_name?: string | null;
    status: string;
    message?: string | null;
  }>;
};

export type ChatHistoryMessageResponse = {
  role: ChatRole;
  content: string;
  sources?: ChatSourceDocument[];
  timestamp?: string | null;
};

export type ChatHistoryResponse = {
  messages: ChatHistoryMessageResponse[];
};
