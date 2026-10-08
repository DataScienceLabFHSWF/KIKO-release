// frontend/src/features/courseGenerator/api/CourseGeneratorApi.ts

import { apiRequest } from "@/api/client";
import type {
  AnswerGradingRequest,
  AnswerGradingResponse,
  AppConfigResponse,
  CourseUploadJobResponse,
  CourseUploadResult,
  CreatedCourseResponse,
} from "../types/CourseGenerator";

function languageHeader(language: string) {
  return {
    "Accept-Language": language.startsWith("de") ? "de" : "en",
  };
}

export function getCourseGeneratorConfig() {
  return apiRequest<AppConfigResponse>("/app_configurations/app_config");
}

export function uploadCourseDocument(formData: FormData, language: string) {
  return apiRequest<CourseUploadResult>("/course/upload_course_document", {
    method: "POST",
    headers: languageHeader(language),
    body: formData,
  });
}

export function startPdfCourseUploadJob(formData: FormData, language: string) {
  return apiRequest<CourseUploadJobResponse>(
    "/course/upload_course_document_pdf_job",
    {
      method: "POST",
      headers: languageHeader(language),
      body: formData,
    },
  );
}

export function getPdfCourseUploadJob(jobId: string, language: string) {
  return apiRequest<CourseUploadJobResponse>(
    `/course/upload_course_document_pdf_job/${jobId}`,
    {
      headers: languageHeader(language),
    },
  );
}

export function cancelPdfCourseUploadJob(jobId: string, language: string) {
  return apiRequest<CourseUploadJobResponse>(
    `/course/upload_course_document_pdf_job/${jobId}/cancel`,
    {
      method: "POST",
      headers: languageHeader(language),
    },
  );
}

export function gradeGeneratedQuestion(
  payload: AnswerGradingRequest,
  language: string,
) {
  const misconceptions = (payload.misconceptions ?? [])
    .map((item) => item.trim())
    .filter(Boolean);

  const cleanPayload: AnswerGradingRequest = {
    question: payload.question.trim(),
    reference_answer: payload.reference_answer.trim(),
    user_answer: payload.user_answer.trim(),
    ...(payload.reasoning_model_name
      ? { reasoning_model_name: payload.reasoning_model_name }
      : {}),
    misconceptions,
  };

  return apiRequest<AnswerGradingResponse>("/course/answer_grading", {
    method: "POST",
    headers: languageHeader(language),
    body: JSON.stringify(cleanPayload),
  });
}

export function createCourseFromGeneratedContent(
  formData: FormData,
  language: string,
) {
  return apiRequest<CreatedCourseResponse>(
    "/course/create_course_with_summary_and_qas",
    {
      method: "POST",
      headers: languageHeader(language),
      body: formData,
    },
  );
}
