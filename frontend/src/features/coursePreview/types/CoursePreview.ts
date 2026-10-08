// frontend/src/features/coursePreview/types/CoursePreview.ts

import type { ReactNode } from "react";

export type CoursePreviewSectionKey =
  | "overview"
  | "course-info"
  | `module:${string}`
  | "final-quiz"
  | "grades"
  | "resources";

export type CoursePreviewModuleTabKey =
  | "content"
  | "practice"
  | "quiz"
  | "further-reading"
  | "misconceptions"
  | "meta";

export type CoursePreviewResource = {
  title: string;
  type?: string;
  url?: string;
};

export type CoursePreviewInstructor = {
  name: string;
  bio?: string;
};

export type CoursePreviewPracticeQuestion = {
  id: string;
  prompt: string;
  referenceAnswer?: string;
  points?: number;
};

export type CoursePreviewQuizChoice = {
  id: string;
  text: string;
  correct?: boolean;
};

export type CoursePreviewQuizQuestion = {
  id: string;
  text: string;
  type?: string;
  points?: number;
  choices?: CoursePreviewQuizChoice[];
  correctAnswer?: unknown;
};

export type CoursePreviewQuiz = {
  id: string;
  title: string;
  passPercent?: number;
  questions: CoursePreviewQuizQuestion[];
};

export type CoursePreviewModule = {
  id: string;
  title: string;
  content: string;
  practiceQuestions: CoursePreviewPracticeQuestion[];
  quiz?: CoursePreviewQuiz | null;
  furtherReading: CoursePreviewResource[];
  misconceptions: string[];
  meta?: Record<string, unknown>;
};

export type CoursePreviewCourse = {
  courseId?: number;
  title: string;
  provider: string;
  difficulty: string;
  language: string;
  duration: string;
  progressPercent: number;
  overview: string;
  modules: CoursePreviewModule[];
  resources: CoursePreviewResource[];
  finalQuiz?: CoursePreviewQuiz | null;
  tags: string[];
  prerequisites: string[];
  instructors: CoursePreviewInstructor[];
  gradingNotes: string[];
  isEnrolled?: boolean;
};

export type CoursePreviewTab = {
  key: string;
  label: string;
  icon?: ReactNode;
  disabled?: boolean;
};
