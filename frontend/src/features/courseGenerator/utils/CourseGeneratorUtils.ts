// frontend/src/features/courseGenerator/utils/CourseGeneratorUtils.ts

import YAML from "yaml";
import type {
  CourseJson,
  CourseJsonModule,
  CourseUploadResult,
  QuestionAnswerItem,
  QuestionAnswerList,
} from "../types/CourseGenerator";

export function asString(value: unknown, fallback = "") {
  return typeof value === "string" ? value : fallback;
}

export function asNumber(value: unknown, fallback: number) {
  const numberValue = Number(value);
  return Number.isFinite(numberValue) ? numberValue : fallback;
}

export function clampNumber(value: number, min: number, max: number) {
  return Math.min(Math.max(value, min), max);
}

export function isPdfFile(file: File | null) {
  return Boolean(file?.name.toLowerCase().endsWith(".pdf"));
}

export function isMarkdownFile(file: File | null) {
  const name = file?.name.toLowerCase() ?? "";
  return name.endsWith(".md") || name.endsWith(".markdown");
}

export function getCourseTitle(courseJson?: CourseJson | null) {
  return courseJson?.course?.title?.trim() || "Generated Course";
}

export function getCourseSummary(
  result: CourseUploadResult,
  courseJson?: CourseJson | null,
) {
  if (result.final_summary?.trim()) {
    return result.final_summary.trim();
  }

  const firstModule = courseJson?.modules?.[0];
  return firstModule?.content_md?.trim() || firstModule?.content?.trim() || "";
}

export function getQuestionText(item: QuestionAnswerItem) {
  return item.question ?? item.prompt ?? item.text ?? "";
}

export function getAnswerText(item: QuestionAnswerItem) {
  return item.answer ?? item.reference_answer ?? item.answer_text ?? "";
}

export function extractQuestions(
  resultQuestions?: QuestionAnswerList | null,
  courseJson?: CourseJson | null,
): QuestionAnswerItem[] {
  const fromResult = resultQuestions?.qa_list;

  if (Array.isArray(fromResult) && fromResult.length > 0) {
    return fromResult;
  }

  return (
    courseJson?.modules?.flatMap((module) => {
      const moduleQuestions =
        module.questions ?? module.practice_questions ?? [];
      return Array.isArray(moduleQuestions) ? moduleQuestions : [];
    }) ?? []
  );
}

export function yamlStringify(value: unknown) {
  try {
    return YAML.stringify(value ?? null).trim();
  } catch {
    return "";
  }
}

export function yamlParse<T>(value: string): T {
  return YAML.parse(value) as T;
}

export function updateModuleAt(
  courseJson: CourseJson,
  moduleIndex: number,
  updater: (module: CourseJsonModule) => CourseJsonModule,
): CourseJson {
  const modules = [...(courseJson.modules ?? [])];
  const currentModule = modules[moduleIndex];

  if (!currentModule) {
    return courseJson;
  }

  modules[moduleIndex] = updater(currentModule);

  return {
    ...courseJson,
    modules,
  };
}

export function buildSaveCourseFormData(params: {
  result: CourseUploadResult;
  editedCourseJson: CourseJson | null;
  title: string;
}) {
  const { result, editedCourseJson, title } = params;

  const courseJson = editedCourseJson ?? result.course_json ?? {};
  const questions = extractQuestions(result.questions, courseJson).map(
    (item) => ({
      text: getQuestionText(item),
      answer_text: getAnswerText(item),
    }),
  );

  const formData = new FormData();

  formData.set("title", title.trim() || getCourseTitle(courseJson));
  formData.set("summary", getCourseSummary(result, courseJson));
  formData.set("questions", JSON.stringify(questions));
  formData.set(
    "quiz",
    result.quiz ?? yamlStringify(courseJson.final_quiz ?? {}),
  );
  formData.set("template_markdown", result.template_markdown ?? "");
  formData.set("course_json", JSON.stringify(courseJson));

  return formData;
}

export function buildUploadFormData(params: {
  file: File;
  embeddingModel: string;
  llmModel: string;
  qaCount: number;
  quizQuestionCount: number;
  quizOptionCount: number;
  misconceptionCount: number;
  replaceExisting?: boolean;
}) {
  const formData = new FormData();

  formData.set("file", params.file);
  formData.set("embedding_model_name", params.embeddingModel);
  formData.set("llm_model_name", params.llmModel);
  formData.set("qa_count", String(params.qaCount));
  formData.set("quiz_question_count", String(params.quizQuestionCount));
  formData.set("quiz_option_count", String(params.quizOptionCount));
  formData.set("misconception_count", String(params.misconceptionCount));

  if (params.replaceExisting !== undefined) {
    formData.set("replace_existing", String(params.replaceExisting));
  }

  return formData;
}
