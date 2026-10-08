// frontend/src/features/adminKnowledgeCheck/types/AdminKnowledgeCheck.ts

export type AdminKnowledgeQuestion = {
  question_id: number;
  topic: string;
  question: string;
  type: string;
  options?: Array<Record<string, unknown>> | null;
  difficulty?: string | null;
  correct_answer?: unknown;
  explanation?: string | null;
  is_active?: boolean | null;
  created_at?: string | null;
  updated_at?: string | null;
};

export type KnowledgeCheckConfig = {
  enabled: boolean;
  size: number;
  question_ids: number[];
};

export type KnowledgeCheckConfigResponse = {
  config?: Partial<KnowledgeCheckConfig> | null;
};

export type KnowledgeCheckConfigUpdateRequest = {
  config: KnowledgeCheckConfig;
};
