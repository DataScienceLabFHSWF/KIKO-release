// frontend/src/features/chat/api/ChatApi.ts

import { apiRequest } from "@/api/client";
import type {
  ChatHistoryResponse,
  ChatLlmModel,
  ChatQueryResponse,
  ProcessUploadedDocsResponse,
} from "../types/Chat";
import { DEFAULT_EMBEDDING_MODEL } from "../types/Chat";

export function getChatHistory() {
  return apiRequest<ChatHistoryResponse>("/chatbot/chat/history");
}

export function submitChatQuery(query: string, llmModel: ChatLlmModel) {
  return apiRequest<ChatQueryResponse>("/chatbot/query", {
    method: "POST",
    body: JSON.stringify({
      query,
      embedding_model: DEFAULT_EMBEDDING_MODEL,
      llm_model: llmModel,
    }),
  });
}

export function processUploadedPdfDocuments(files: File[]) {
  const formData = new FormData();

  files.forEach((file) => {
    formData.append("files", file);
  });

  formData.append("embedding_model_name", DEFAULT_EMBEDDING_MODEL);

  return apiRequest<ProcessUploadedDocsResponse>(
    "/document/process_uploaded_docs",
    {
      method: "POST",
      body: formData,
    },
  );
}
