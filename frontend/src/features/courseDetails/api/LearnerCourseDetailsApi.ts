// frontend/src/features/courseDetails/api/LearnerCourseDetailsApi.ts

import { apiRequest } from "@/api/client";
import type {
  LearnerCourseDetailsResponse,
  LearnerProgressUpdateRequest,
  LearnerQuizSubmitResponse,
  LearnerSubmitQuizRequest,
  PracticeAnswerEvaluationRequest,
  PracticeAnswerEvaluationResponse,
  SubmitModuleQuizRequest,
} from "../types/LearnerCourseDetails";

export function getLearnerCourseDetails(courseId: number) {
  return apiRequest<LearnerCourseDetailsResponse>(
    `/learner/courses/${courseId}`,
  );
}

export function enrollInLearnerCourse(courseId: number) {
  return apiRequest<void>(`/learner/courses/${courseId}/enroll`, {
    method: "POST",
  });
}

export function unenrollFromLearnerCourse(courseId: number) {
  return apiRequest<void>(`/learner/courses/${courseId}/enrollment`, {
    method: "DELETE",
  });
}

export function saveLearnerCourseProgress(
  courseId: number,
  payload: LearnerProgressUpdateRequest,
) {
  return apiRequest<void | { message: string }>(
    `/learner/courses/${courseId}/progress`,
    {
      method: "PUT",
      body: JSON.stringify(payload),
    },
  );
}

export function submitModuleQuizAttempt(
  courseId: number,
  moduleId: string,
  payload: SubmitModuleQuizRequest,
) {
  const cleanPayload: SubmitModuleQuizRequest = {
    assessment_id: payload.assessment_id,
    answers: payload.answers,
    ...(payload.reasoning_model_name
      ? { reasoning_model_name: payload.reasoning_model_name }
      : {}),
  };
  console.log("Submitting module quiz attempt:", {
    courseId,
    moduleId,
    payload: cleanPayload,
  });
  return apiRequest<LearnerQuizSubmitResponse>(
    `/learner/courses/${courseId}/module-quizzes/${moduleId}/submit`,
    {
      method: "POST",
      body: JSON.stringify(cleanPayload),
    },
  );
}

export function submitFinalQuizAttempt(
  courseId: number,
  payload: SubmitModuleQuizRequest,
) {
  const cleanPayload: SubmitModuleQuizRequest = {
    assessment_id: payload.assessment_id,
    answers: payload.answers,
    ...(payload.reasoning_model_name
      ? { reasoning_model_name: payload.reasoning_model_name }
      : {}),
  };

  return apiRequest<LearnerQuizSubmitResponse>(
    `/learner/courses/${courseId}/final-quiz/submit`,
    {
      method: "POST",
      body: JSON.stringify(cleanPayload),
    },
  );
}

export function evaluatePracticeAnswer(
  payload: PracticeAnswerEvaluationRequest,
) {
  const misconceptions = (payload.misconceptions ?? [])
    .map((item) => item.trim())
    .filter(Boolean);
  const cleanPayload = {
    question: payload.question,
    reference_answer: payload.reference_answer,
    user_answer: payload.user_answer,
    ...(payload.reasoning_model_name
      ? { reasoning_model_name: payload.reasoning_model_name }
      : {}),
    ...(misconceptions.length > 0 ? { misconceptions } : {}),
  };

  return apiRequest<PracticeAnswerEvaluationResponse>(
    "/course/answer_grading",
    {
      method: "POST",
      body: JSON.stringify(cleanPayload),
    },
  );
}
