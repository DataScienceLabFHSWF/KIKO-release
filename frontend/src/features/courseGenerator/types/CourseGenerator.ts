// frontend/src/features/courseGenerator/types/CourseGenerator.ts

export type CourseUploadMessage = "success" | "file_exists" | "markdown_exists";

export type CourseUploadResult = {
  message: CourseUploadMessage;
  detail?: string | null;
  final_summary?: string | null;
  questions?: QuestionAnswerList | null;
  quiz?: string | null;
  generated_markdown?: string | null;
  generated_markdown_file_name?: string | null;
  metadata?: Record<string, unknown> | null;
  template_markdown?: string | null;
  course_json?: CourseJson | null;
  existing_document?: {
    document_id: number;
    file_name: string;
    uploaded_at?: string | null;
  } | null;
};

export type CourseUploadJobStatus =
  | "queued"
  | "processing"
  | "cancelling"
  | "completed"
  | "cancelled"
  | "failed";

export type CourseUploadJobResponse = {
  job_id: string;
  status: CourseUploadJobStatus;
  progress: number;
  message: string;
  cancel_requested: boolean;
  stage_key: string;
  created_at: string;
  updated_at: string;
  result?: CourseUploadResult | null;
  error?: string | null;
};

export type QuestionAnswerItem = {
  id?: string;
  module_id?: string;
  module_title?: string;
  question?: string;
  answer?: string;
  prompt?: string;
  reference_answer?: string;
  text?: string;
  answer_text?: string;
  points?: number;
};

export type QuestionAnswerList = {
  qa_list?: QuestionAnswerItem[];
};

export type CourseMeta = {
  id?: string;
  source_doc?: string;
  title?: string;
  version?: string;
  provider?: string;
  language?: string;
  level?: string;
  tags?: string[];
  estimated_minutes?: number;
  published?: boolean;
  prerequisites?: string[];
};

export type CourseJsonModule = {
  id?: string;
  title?: string;
  content_md?: string;
  content?: string;
  questions?: QuestionAnswerItem[];
  practice_questions?: QuestionAnswerItem[];
  quiz?: Record<string, unknown>;
  further_reading_md?: string;
  further_reading?: unknown;
  misconceptions?: unknown;
  grade?: unknown;
  meta?: Record<string, unknown>;
};

export type CourseJson = {
  schema?: string;
  course?: CourseMeta;
  instructors?: Array<Record<string, unknown>>;
  grading?: Record<string, unknown>;
  resources?: Array<Record<string, unknown>>;
  modules?: CourseJsonModule[];
  final_quiz?: Record<string, unknown>;
};

export type AppConfigForCourseGenerator = {
  default_embedding_model?: string;
  default_llm_model?: string;
  default_reasoning_model?: string;

  course_generator_qa_count_min?: number;
  course_generator_qa_count_default?: number;
  course_generator_qa_count_max?: number;

  course_generator_quiz_question_count_min?: number;
  course_generator_quiz_question_count_default?: number;
  course_generator_quiz_question_count_max?: number;

  course_generator_quiz_option_count_min?: number;
  course_generator_quiz_option_count_default?: number;
  course_generator_quiz_option_count_max?: number;

  course_generator_misconception_count_min?: number;
  course_generator_misconception_count_default?: number;
  course_generator_misconception_count_max?: number;
};

export type AppConfigResponse = {
  app_config?: AppConfigForCourseGenerator;
};

export type AnswerGradingResponse = {
  message: "success";
  grade: number | string | null;
  summary: string;
  misconceptions_considered?: string[];
};

export type CreatedCourseResponse = {
  message: "success";
  course_id: number;
  title: string;
  summary?: string | null;
  quiz?: string | null;
  template_markdown?: string | null;
  course_json?: CourseJson | null;
  questions: Array<{
    question_id?: number | null;
    text: string;
    answer_text: string;
  }>;
  question_count: number;
  has_quiz: boolean;
  has_template_markdown: boolean;
  has_course_json: boolean;
  created_at?: string | null;
  updated_at?: string | null;
};

export type AnswerGradingRequest = {
  question: string;
  reference_answer: string;
  user_answer: string;
  reasoning_model_name?: string;
  misconceptions: string[];
};

export type GeneratedQaReviewItem = {
  question: QuestionAnswerItem;
  moduleId?: string;
  moduleTitle?: string;
  misconceptions: string[];
};
