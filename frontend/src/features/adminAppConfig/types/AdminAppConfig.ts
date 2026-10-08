// frontend/src/features/adminAppConfig/types/AdminAppConfig.ts

export type RuntimeEnvironment = {
  python_version: string;
  platform: string;
};

export type CudaInfo = {
  enabled: boolean;
  version?: string | null;
  device?: string | null;
  memory_gb?: number | null;
};

export type TorchInfo = {
  is_available: boolean;
  cuda: CudaInfo;
  torch_version?: string | null;
};

export type FeatureFlags = {
  is_advanced_models_available: boolean;
  is_surya_available: boolean;
  is_cv2_available: boolean;
};

export type FullAppConfig = {
  app_title: string;
  chunk_size: number;
  chunk_overlap: number;

  default_embedding_model: string;
  default_llm_model: string;
  default_reasoning_model: string;

  course_generator_qa_count_min: number;
  course_generator_qa_count_default: number;
  course_generator_qa_count_max: number;

  course_generator_quiz_question_count_min: number;
  course_generator_quiz_question_count_default: number;
  course_generator_quiz_question_count_max: number;

  course_generator_quiz_option_count_min: number;
  course_generator_quiz_option_count_default: number;
  course_generator_quiz_option_count_max: number;

  course_generator_misconception_count_min: number;
  course_generator_misconception_count_default: number;
  course_generator_misconception_count_max: number;

  enable_vlm: boolean;
  preferred_vlm_model: string;

  use_advanced_ocr: boolean;
  preferred_ocr_engine: string;
  ocr_preprocessing: boolean;
  ocr_skew_correction: boolean;
  ocr_noise_reduction: boolean;
  ocr_language: string;

  enable_multilingual: boolean;
  language_detection: boolean;
  default_language: string;

  [key: string]: unknown;
};

export type AppConfigResponse = {
  message?: "success";
  environment: RuntimeEnvironment;
  modules: {
    torch: TorchInfo;
  };
  flags: FeatureFlags;
  app_config: FullAppConfig;
};

export type EditableAppConfig = Pick<
  FullAppConfig,
  | "default_embedding_model"
  | "default_llm_model"
  | "default_reasoning_model"
  | "course_generator_qa_count_min"
  | "course_generator_qa_count_default"
  | "course_generator_qa_count_max"
  | "course_generator_quiz_question_count_min"
  | "course_generator_quiz_question_count_default"
  | "course_generator_quiz_question_count_max"
  | "course_generator_quiz_option_count_min"
  | "course_generator_quiz_option_count_default"
  | "course_generator_quiz_option_count_max"
  | "course_generator_misconception_count_min"
  | "course_generator_misconception_count_default"
  | "course_generator_misconception_count_max"
  | "enable_vlm"
  | "preferred_vlm_model"
  | "use_advanced_ocr"
  | "preferred_ocr_engine"
  | "ocr_preprocessing"
  | "ocr_skew_correction"
  | "ocr_noise_reduction"
  | "ocr_language"
  | "enable_multilingual"
  | "language_detection"
  | "default_language"
>;

export type AppConfigUpdateRequest = {
  app_config: EditableAppConfig;
};

export type ConfigValidationError = {
  field: keyof EditableAppConfig | "general";
  message: string;
};
