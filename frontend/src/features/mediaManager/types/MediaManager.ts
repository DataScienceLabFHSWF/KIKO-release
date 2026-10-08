// frontend/src/features/mediaManager/types/MediaManager.ts

export type InstructorCourseSummary = {
  course_id: number;
  title: string;
  summary?: string | null;
  question_count?: number;
  quiz_question_count?: number;
  enrolled_count?: number;
  created_at?: string | null;
  updated_at?: string | null;
};

export type CourseImage = {
  course_id: number;
  original_filename: string;
  stored_filename: string;
  url?: string | null;
  content_type?: string | null;
  size_bytes?: number | null;
  uploaded_at?: string | null;
};

export type CourseImageUploadResponse = CourseImage & {
  message: "success";
};
