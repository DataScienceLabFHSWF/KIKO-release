// frontend/src/features/documents/api/DocumentsApi.ts

import { apiBlob, apiRequest } from "@/api/client";
import type { DocumentItem, MarkdownPreviewResponse } from "../types/Documents";

export const documentQueryKeys = {
  myDocuments: ["documents", "mine"] as const,
};

export function listMyDocuments() {
  return apiRequest<DocumentItem[]>("/document/my_docs");
}

export function deleteDocument(documentId: number) {
  return apiRequest<void>(`/document/delete_doc/${documentId}`, {
    method: "DELETE",
  });
}

export function deleteAllDocuments() {
  return apiRequest<void>("/document/delete_all_doc", {
    method: "DELETE",
  });
}

export function downloadDocument(contentHash: string) {
  return apiBlob(`/files/${contentHash}/download`);
}

export function previewPdfDocument(contentHash: string) {
  return apiBlob(
    `/files/${contentHash}/preview.png?page_from=1&page_to=3&scale=1.4`,
  );
}

export function previewMarkdownDocument(contentHash: string) {
  return apiRequest<MarkdownPreviewResponse>(`/files/${contentHash}/markdown`);
}
