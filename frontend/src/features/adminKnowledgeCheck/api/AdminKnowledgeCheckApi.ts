// frontend/src/features/adminKnowledgeCheck/api/adminKnowledgeCheckApi.ts

import { apiRequest } from "@/api/client";
import type {
  AdminKnowledgeQuestion,
  KnowledgeCheckConfig,
  KnowledgeCheckConfigResponse,
  KnowledgeCheckConfigUpdateRequest,
} from "../types/AdminKnowledgeCheck";

const DEFAULT_CONFIG: KnowledgeCheckConfig = {
  enabled: true,
  size: 5,
  question_ids: [],
};

export const adminKnowledgeCheckQueryKeys = {
  all: ["admin-knowledge-check"] as const,
  questions: ["admin-knowledge-check", "questions"] as const,
  config: ["admin-knowledge-check", "config"] as const,
};

function normalizeConfig(
  response: KnowledgeCheckConfigResponse | null | undefined,
): KnowledgeCheckConfig {
  const config = response?.config ?? {};

  return {
    enabled:
      typeof config.enabled === "boolean"
        ? config.enabled
        : DEFAULT_CONFIG.enabled,
    size:
      typeof config.size === "number" && Number.isFinite(config.size)
        ? Math.max(1, Math.floor(config.size))
        : DEFAULT_CONFIG.size,
    question_ids: Array.isArray(config.question_ids)
      ? config.question_ids
          .map((id) => Number(id))
          .filter((id) => Number.isInteger(id) && id > 0)
      : DEFAULT_CONFIG.question_ids,
  };
}

export async function listAdminKnowledgeQuestions(): Promise<
  AdminKnowledgeQuestion[]
> {
  return apiRequest<AdminKnowledgeQuestion[]>(
    "/knowledge_assessment/questions",
  );
}

export async function getAdminKnowledgeConfig(): Promise<KnowledgeCheckConfig> {
  const response = await apiRequest<KnowledgeCheckConfigResponse>(
    "/knowledge_assessment/config",
  );

  return normalizeConfig(response);
}

export async function updateAdminKnowledgeConfig(
  config: KnowledgeCheckConfig,
): Promise<void> {
  const payload: KnowledgeCheckConfigUpdateRequest = {
    config,
  };

  await apiRequest<void>("/knowledge_assessment/config", {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}

export async function deleteAdminKnowledgeQuestion(
  questionId: number,
): Promise<void> {
  await apiRequest<void>(`/knowledge_assessment/questions/${questionId}`, {
    method: "DELETE",
  });
}
