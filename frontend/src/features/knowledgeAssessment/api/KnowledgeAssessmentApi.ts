// frontend/src/features/knowledgeAssessment/api/KnowledgeAssessmentApi.ts

import { apiRequest } from "@/api/client";
import type {
  AssessmentQuestion,
  AssessmentResult,
  AssessmentSubmitRequest,
} from "../types/KnowledgeAssessment";

export function getAssessmentQuiz() {
  return apiRequest<AssessmentQuestion[]>(
    "/knowledge_assessment/assessment_quiz",
  );
}

export function submitAssessmentQuiz(
  payload: AssessmentSubmitRequest,
  language: string,
) {
  console.log(
    "Submitting assessment quiz with payload:",
    payload,
    "and language:",
    language,
  );
  return apiRequest<AssessmentResult>(
    "/knowledge_assessment/assessment_submit",
    {
      method: "POST",
      headers: {
        "Accept-Language": language,
      },
      body: JSON.stringify(payload),
    },
  );
}
