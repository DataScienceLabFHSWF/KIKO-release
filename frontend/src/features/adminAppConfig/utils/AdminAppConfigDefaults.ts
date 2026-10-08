// frontend/src/features/adminAppConfig/utils/adminAppConfigDefaults.ts

import type {
  ConfigValidationError,
  EditableAppConfig,
  FullAppConfig,
} from "../types/AdminAppConfig";

export function pickEditableAppConfig(
  config: FullAppConfig,
): EditableAppConfig {
  return {
    default_embedding_model: config.default_embedding_model ?? "",
    default_llm_model: config.default_llm_model ?? "",
    default_reasoning_model: config.default_reasoning_model ?? "",

    course_generator_qa_count_min: config.course_generator_qa_count_min ?? 1,
    course_generator_qa_count_default:
      config.course_generator_qa_count_default ?? 5,
    course_generator_qa_count_max: config.course_generator_qa_count_max ?? 10,

    course_generator_quiz_question_count_min:
      config.course_generator_quiz_question_count_min ?? 1,
    course_generator_quiz_question_count_default:
      config.course_generator_quiz_question_count_default ?? 3,
    course_generator_quiz_question_count_max:
      config.course_generator_quiz_question_count_max ?? 4,

    course_generator_quiz_option_count_min:
      config.course_generator_quiz_option_count_min ?? 2,
    course_generator_quiz_option_count_default:
      config.course_generator_quiz_option_count_default ?? 3,
    course_generator_quiz_option_count_max:
      config.course_generator_quiz_option_count_max ?? 4,

    course_generator_misconception_count_min:
      config.course_generator_misconception_count_min ?? 1,
    course_generator_misconception_count_default:
      config.course_generator_misconception_count_default ?? 2,
    course_generator_misconception_count_max:
      config.course_generator_misconception_count_max ?? 4,

    enable_vlm: Boolean(config.enable_vlm),
    preferred_vlm_model: config.preferred_vlm_model ?? "",

    use_advanced_ocr: Boolean(config.use_advanced_ocr),
    preferred_ocr_engine: config.preferred_ocr_engine ?? "trocr",
    ocr_preprocessing: Boolean(config.ocr_preprocessing),
    ocr_skew_correction: Boolean(config.ocr_skew_correction),
    ocr_noise_reduction: Boolean(config.ocr_noise_reduction),
    ocr_language: config.ocr_language ?? "auto",

    enable_multilingual: Boolean(config.enable_multilingual),
    language_detection: Boolean(config.language_detection),
    default_language: config.default_language ?? "deu",
  };
}

function validateRange(
  errors: ConfigValidationError[],
  min: number,
  value: number,
  max: number,
  label: string,
) {
  if (min < 1) {
    errors.push({
      field: "general",
      message: `${label}: minimum must be at least 1.`,
    });
  }

  if (value < min || value > max) {
    errors.push({
      field: "general",
      message: `${label}: default value must be between minimum and maximum.`,
    });
  }

  if (min > max) {
    errors.push({
      field: "general",
      message: `${label}: minimum cannot be greater than maximum.`,
    });
  }
}

export function validateEditableAppConfig(
  config: EditableAppConfig,
): ConfigValidationError[] {
  const errors: ConfigValidationError[] = [];

  if (!config.default_embedding_model.trim()) {
    errors.push({
      field: "default_embedding_model",
      message: "Default embedding model is required.",
    });
  }

  if (!config.default_llm_model.trim()) {
    errors.push({
      field: "default_llm_model",
      message: "Default LLM model is required.",
    });
  }

  if (!config.default_reasoning_model.trim()) {
    errors.push({
      field: "default_reasoning_model",
      message: "Default reasoning model is required.",
    });
  }

  validateRange(
    errors,
    config.course_generator_qa_count_min,
    config.course_generator_qa_count_default,
    config.course_generator_qa_count_max,
    "Q&A pairs",
  );

  validateRange(
    errors,
    config.course_generator_quiz_question_count_min,
    config.course_generator_quiz_question_count_default,
    config.course_generator_quiz_question_count_max,
    "Quiz questions",
  );

  validateRange(
    errors,
    config.course_generator_quiz_option_count_min,
    config.course_generator_quiz_option_count_default,
    config.course_generator_quiz_option_count_max,
    "Quiz options",
  );

  validateRange(
    errors,
    config.course_generator_misconception_count_min,
    config.course_generator_misconception_count_default,
    config.course_generator_misconception_count_max,
    "Misconceptions",
  );

  if (config.enable_vlm && !config.preferred_vlm_model.trim()) {
    errors.push({
      field: "preferred_vlm_model",
      message: "Preferred VLM model is required when VLM is enabled.",
    });
  }

  if (config.use_advanced_ocr && !config.preferred_ocr_engine.trim()) {
    errors.push({
      field: "preferred_ocr_engine",
      message: "Preferred OCR engine is required when advanced OCR is enabled.",
    });
  }

  if (!config.ocr_language.trim()) {
    errors.push({
      field: "ocr_language",
      message: "OCR language is required.",
    });
  }

  if (!config.default_language.trim()) {
    errors.push({
      field: "default_language",
      message: "Default language is required.",
    });
  }

  return errors;
}
