// frontend/src/features/knowledgeAssessment/types/KnowledgeAssessment.ts

export type AssessmentQuestion = {
  question_id: number;
  topic: string;
  question: string;
  type: string;
  options?: Array<Record<string, unknown>> | null;
  difficulty?: string | null;
};

export type AssessmentAnswer = {
  question_id: number;
  user_answer: string;
};

export type AssessmentSubmitRequest = {
  answers: AssessmentAnswer[];
};

export type GradedAssessmentAnswer = {
  question_id?: number | null;
  grade: number;
  summary?: string | null;
};

export type RecommendedCourse = {
  course_id?: number;
  title?: string;
  summary?: string | null;
  reason?: string | null;
  [key: string]: unknown;
};

export type AssessmentResult = {
  graded_answers: GradedAssessmentAnswer[];
  knowledge_assessment: string;
  learning_path: string;
  learning_step: string;
  recommended_courses: RecommendedCourse[];
};
