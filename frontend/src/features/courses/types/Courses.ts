// frontend/src/features/courses/types/Courses.ts

import type { ReactNode } from "react";

export type CourseProgressStatus = "not_started" | "in_progress" | "completed";
export type CourseJson = Record<string, unknown>;

export type LearnerEnrolledCourse = {
  course_id: number;
  title: string;
  summary?: string | null;
  completed?: boolean;
  status?: string | null;
  completion_percent: number | null;
  enrolled_at: string | null;
};

export type LearnerAvailableCourse = {
  course_id: number;
  title: string;
  summary?: string | null;
  instructor_name?: string | null;
  is_enrolled?: boolean;
  reason?: string | null;
};

export type InstructorCourse = {
  course_id: number;
  title: string;
  created_by: number;
  summary?: string | null;
  description?: string | null;
  question_count?: number;
  quiz_question_count?: number;
  created_at?: string | null;
  learner_count?: number;
  document_count?: number;
};

export type CourseCardAction = {
  label: string;
  icon?: ReactNode;
  onClick?: () => void;
  to?: string;
  variant?: "primary" | "secondary" | "ghost" | "danger" | "success";
  disabled?: boolean;
  ariaLabel?: string;
};

export type InstructorCourseDetails = {
  course_id: number;
  title: string;
  created_by: number;
  summary?: string | null;
  quiz?: string | null;
  template_markdown?: string | null;
  course_json?: CourseJson | null;
  questions?: Array<{
    question_id?: number;
    text?: string;
    answer_text?: string;
  }>;
  created_at?: string | null;
  updated_at?: string | null;
};

export type InstructorCourseUpdateRequest = {
  title?: string;
  summary?: string;
  quiz?: string | null;
  template_markdown?: string | null;
  course_json?: CourseJson | null;
  questions?: Array<{
    question_id?: number;
    text: string;
    answer_text: string;
  }>;
};

export type InstructorCourseUpdateResponse = {
  message?: string;
  course_id: number;
  title?: string;
  summary?: string | null;
  quiz?: string | null;
  template_markdown?: string | null;
  course_json?: CourseJson | null;
};
