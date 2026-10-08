// frontend/src/features/courseDetails/types/LearnerCourseDetails.ts

export type LearnerCourseProgressResponse = {
  current_nav?: string | null;
  current_module_id?: string | null;
  progress_percent?: number;
  practice_answers?: Record<string, unknown> | null;
  updated_at?: string | null;
};

export type LearnerCourseSummaryResponse = {
  course_id: number;
  title: string;
  summary?: string | null;
  created_at?: string | null;
};

export type LearnerCourseEnrollmentResponse = {
  is_enrolled: boolean;
  enrolled?: boolean;
  status?: string;
  completion_percent?: number;
  completed?: boolean;
};

export type LearnerProgressSnapshotResponse = {
  current_nav?: string | null;
  current_module_id?: string | null;
  completion_percent?: number;
  module_status?: Record<string, unknown>;
  final_status?: Record<string, unknown>;
  practice_answers?: Record<string, unknown>;
  course_completion?: Record<string, unknown>;
};

export type LearnerAttemptSummariesResponse = {
  module_quizzes?: Record<string, unknown>;
  final_quiz?: Record<string, unknown>;
  course_completion?: Record<string, unknown>;
};

export type LearnerCourseDetailsResponse = {
  course: LearnerCourseSummaryResponse;
  enrollment: LearnerCourseEnrollmentResponse;
  course_json?: Record<string, unknown> | null;
  template_markdown?: string | null;
  progress_snapshot?: LearnerProgressSnapshotResponse | null;
  attempt_summaries?: LearnerAttemptSummariesResponse | null;
  latest_attempts?: PersistedQuizAttempts | null;
};

export type LearnerQuizAnswerItem = {
  item_id: string;
  selected_choice_ids?: string[];
  selected_value?: string | string[] | boolean | number | null;
};

export type LearnerSubmitQuizRequest = {
  assessment_id: string;
  reasoning_model_name?: string | null;
  answers: LearnerQuizAnswerItem[];
};

export type LearnerGradedAnswerResponse = {
  item_id?: string | null;
  question_id?: string | number | null;
  grade?: number | null;
  is_correct?: boolean | null;
  feedback?: string | null;
  correct_answer?: unknown;
};

export type LearnerProgressUpdateRequest = {
  current_nav?: string | null;
  current_module_id?: string | null;
  practice_answers?: Record<string, unknown> | null;
};

export type CourseChoice = {
  id: string;
  text: string;
};

export type CoursePracticeQuestion = {
  id: string;
  prompt: string;
  referenceAnswer: string;
  points: number;
};

export type PracticeAnswers = Record<string, string>;

export type PracticeEvaluation = {
  message?: string;
  grade?: number | string | null;
  summary?: string;
  misconceptions_considered?: string[];
};

export type NormalizedCourseModule = {
  id: string;
  title: string;
  content: string;
  practiceText?: string;
  practiceQuestions: CoursePracticeQuestion[];
  quiz?: NormalizedCourseQuiz | null;
  furtherReading: Array<{
    title: string;
    type?: string;
    url?: string;
  }>;
  misconceptions: string[];
};

export type NormalizedCourseResource = {
  title: string;
  type?: string;
  url?: string;
};

export type NormalizedCourseDetails = {
  courseId: number;
  title: string;
  summary: string;
  overview: string;
  difficulty: string;
  language: string;
  duration: string;
  provider: string;
  modules: NormalizedCourseModule[];
  resources: NormalizedCourseResource[];
  finalQuiz?: NormalizedCourseQuiz | null;
  skills: string[];
  prerequisites: string[];
  instructors: Array<{
    name: string;
    bio?: string;
  }>;
  grading: {
    passPercent: number;
    assessmentWeights: Record<string, unknown>;
    requiredModules: string[];
    requiredAssessments: string[];
    notes: string[];
  };
  progressPercent: number;
  isEnrolled: boolean;
  finalAssessmentStatus: NormalizedFinalAssessmentStatus;
  latestAttempts: PersistedQuizAttempts;
};

export type CourseModuleTabKey =
  | "content"
  | "practice"
  | "quiz"
  | "further-reading"
  | "misconceptions";

export type PracticeAnswerEvaluationRequest = {
  question: string;
  reference_answer: string;
  user_answer: string;
  reasoning_model_name?: string;
  misconceptions?: string[];
};

export type PracticeAnswerEvaluationResponse = {
  message?: string;
  grade?: number | string | null;
  summary?: string;
  misconceptions_considered?: string[];
};

export type SubmitModuleQuizRequest = {
  assessment_id: string;
  reasoning_model_name?: string;
  answers: LearnerQuizAnswerItem[];
};

export type CourseQuestionType =
  | "single_select"
  | "multi_select"
  | "true_false";

export type CourseQuizQuestion = {
  item_id: string;
  text: string;
  type: CourseQuestionType;
  choices: CourseChoice[];
  points?: number;
};

export type NormalizedCourseQuiz = {
  assessment_id: string;
  title: string;
  pass_threshold?: number;
  questions: CourseQuizQuestion[];
};

export type QuizAnswerValue = string | string[];

export type QuizAnswers = Record<string, QuizAnswerValue>;

export type LearnerQuizFeedbackItem = {
  item_id?: string | null;
  prompt?: string | null;
  question?: string | null;
  type?: string | null;
  awarded_points?: number | null;
  max_points?: number | null;
  awarded?: number | null;
  max?: number | null;
  correct?: boolean | null;
  summary?: string | null;
  grade?: number | string | null;
  feedback?: string | null;
};

export type LearnerQuizResult = {
  assessment_type: string;
  assessment_id: string;
  module_id?: string | null;
  score?: number | null;
  total_points?: number | null;
  percent?: number | null;
  passed?: boolean | null;
  pass_percent?: number | null;
  german_grade?: number | string | null;
  feedback?: LearnerQuizFeedbackItem[];
};

export type LearnerQuizSubmitResponse = {
  message?: string;
  course_id?: number;
  assessment_id?: string;
  module_id?: string | null;
  score?: number | null;
  max_score?: number | null;
  percent?: number | null;
  passed?: boolean | null;
  pass_percent?: number | null;
  german_grade?: number | string | null;
  graded_answers?: LearnerQuizFeedbackItem[];

  result?: {
    assessment_type?: string;
    assessment_id?: string;
    module_id?: string | null;
    score?: number | null;
    total_points?: number | null;
    percent?: number | null;
    passed?: boolean | null;
    pass_percent?: number | null;
    german_grade?: number | string | null;
    feedback?: LearnerQuizFeedbackItem[];
  };
};

export type NormalizedFinalAssessmentStatus = {
  isEligible: boolean;
  requiredModules: string[];
  missingRequiredModules: string[];
  completed: boolean;
  weightedPercent?: number | null;
  germanGrade?: number | string | null;
};

export type PersistedQuizAttempt = {
  attempt_id?: number;
  assessment_type?: "module_quiz" | "final_quiz";
  assessment_id: string;
  module_id?: string | null;
  submitted_answers: LearnerQuizAnswerItem[];
  score?: number | null;
  max_score?: number | null;
  percent?: number | null;
  passed?: boolean | null;
  german_grade?: number | string | null;
  graded_answers?: LearnerQuizFeedbackItem[];
  submitted_at?: string | null;
};

export type PersistedQuizAttempts = {
  module_quizzes: Record<string, PersistedQuizAttempt>;
  final_quiz: PersistedQuizAttempt | null;
};
