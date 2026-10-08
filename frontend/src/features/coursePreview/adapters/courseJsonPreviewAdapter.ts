// frontend/src/features/coursePreview/adapters/courseJsonPreviewAdapter.ts

import type {
  CoursePreviewCourse,
  CoursePreviewModule,
  CoursePreviewPracticeQuestion,
  CoursePreviewQuiz,
  CoursePreviewQuizChoice,
  CoursePreviewQuizQuestion,
  CoursePreviewResource,
} from "../types/CoursePreview";

type UnknownRecord = Record<string, unknown>;

type CourseJsonPreviewOptions = {
  courseId?: number;
  fallbackTitle?: string;
  fallbackOverview?: string;
  progressPercent?: number;
  isEnrolled?: boolean;
};

function asRecord(value: unknown): UnknownRecord {
  return value && typeof value === "object" && !Array.isArray(value)
    ? (value as UnknownRecord)
    : {};
}

function asArray(value: unknown): unknown[] {
  return Array.isArray(value) ? value : [];
}

function asString(value: unknown, fallback = ""): string {
  return typeof value === "string" && value.trim() ? value.trim() : fallback;
}

function asStringArray(value: unknown): string[] {
  return asArray(value)
    .map((item) => String(item).trim())
    .filter(Boolean);
}

function asNumber(value: unknown, fallback = 0): number {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : fallback;
}

function pickString(
  source: UnknownRecord,
  keys: string[],
  fallback = "",
): string {
  for (const key of keys) {
    const value = source[key];

    if (typeof value === "string" && value.trim()) {
      return value.trim();
    }
  }

  return fallback;
}

function minutesToDuration(value: unknown): string {
  const minutes = asNumber(value, 60);

  if (minutes < 60) return `${minutes} min`;

  const hours = minutes / 60;
  return Number.isInteger(hours) ? `${hours}h` : `${hours.toFixed(1)}h`;
}

function normalizeResources(value: unknown): CoursePreviewResource[] {
  return asArray(value).map((item, index) => {
    if (typeof item === "string") {
      return {
        title: item,
        url: item.startsWith("http") ? item : undefined,
      };
    }

    const record = asRecord(item);

    return {
      title: pickString(
        record,
        ["title", "name", "label"],
        `Resource ${index + 1}`,
      ),
      type: pickString(record, ["type", "kind"], ""),
      url: pickString(record, ["url", "link", "href"], ""),
    };
  });
}

function markdownLinksToResources(value: unknown): CoursePreviewResource[] {
  const markdown = asString(value);

  if (!markdown) return [];

  const resources: CoursePreviewResource[] = [];
  const regex = /\[([^\]]+)\]\(([^)]+)\)/g;

  let match: RegExpExecArray | null;

  while ((match = regex.exec(markdown)) !== null) {
    resources.push({
      title: match[1],
      url: match[2],
      type: match[2].toLowerCase().includes(".pdf") ? "pdf" : "link",
    });
  }

  return resources;
}

function normalizePracticeQuestions(
  value: unknown,
): CoursePreviewPracticeQuestion[] {
  return asArray(value).map((item, index) => {
    const record = asRecord(item);

    return {
      id: pickString(record, ["id", "question_id"], `practice-${index + 1}`),
      prompt: pickString(
        record,
        ["prompt", "question", "text"],
        `Question ${index + 1}`,
      ),
      referenceAnswer: pickString(
        record,
        ["reference_answer", "referenceAnswer", "answer", "answer_text"],
        "",
      ),
      points: asNumber(record.points, 1),
    };
  });
}

function normalizeQuizChoices(value: unknown): CoursePreviewQuizChoice[] {
  return asArray(value).map((item, index) => {
    if (typeof item === "string") {
      return {
        id: item,
        text: item,
      };
    }

    const record = asRecord(item);

    return {
      id: pickString(record, ["id", "choice_id", "key"], `choice-${index + 1}`),
      text: pickString(
        record,
        ["text", "label", "answer", "title"],
        `Option ${index + 1}`,
      ),
      correct: Boolean(record.correct),
    };
  });
}

function normalizeQuizQuestions(value: unknown): CoursePreviewQuizQuestion[] {
  return asArray(value).map((item, index) => {
    const record = asRecord(item);

    return {
      id: pickString(
        record,
        ["id", "item_id", "question_id"],
        `quiz-${index + 1}`,
      ),
      text: pickString(
        record,
        ["prompt", "question", "text", "title"],
        `Question ${index + 1}`,
      ),
      type: pickString(record, ["type"], ""),
      points: asNumber(record.points, 1),
      choices: normalizeQuizChoices(record.choices ?? record.options),
      correctAnswer: record.answer ?? record.correct_answer,
    };
  });
}

function normalizeQuiz(
  value: unknown,
  fallbackId: string,
  fallbackTitle: string,
): CoursePreviewQuiz | null {
  const record = asRecord(value);
  const meta = asRecord(record.meta);

  const questions = normalizeQuizQuestions(
    record.items ?? record.questions ?? record.quiz_items,
  );

  if (questions.length === 0) return null;

  return {
    id: pickString(
      meta,
      ["id", "assessment_id"],
      pickString(record, ["id"], fallbackId),
    ),
    title: pickString(
      meta,
      ["title", "name"],
      pickString(record, ["title"], fallbackTitle),
    ),
    passPercent: asNumber(meta.pass_percent ?? record.pass_percent, 70),
    questions,
  };
}

function normalizeMisconceptions(value: unknown): string[] {
  return asArray(value)
    .map((item) => {
      if (typeof item === "string") return item.trim();

      const record = asRecord(item);
      const misconception = pickString(
        record,
        ["misconception", "title", "text"],
        "",
      );
      const correction = pickString(record, ["correction", "explanation"], "");

      if (misconception && correction) {
        return `${misconception} — ${correction}`;
      }

      return misconception || correction;
    })
    .filter(Boolean);
}

function normalizeModules(value: unknown): CoursePreviewModule[] {
  return asArray(value).map((item, index) => {
    const record = asRecord(item);
    const id = pickString(
      record,
      ["id", "module_id", "key"],
      `module-${index + 1}`,
    );
    const title = pickString(
      record,
      ["title", "name", "module_title"],
      `Module ${index + 1}`,
    );

    return {
      id,
      title,
      content: pickString(
        record,
        ["content_md", "content", "markdown", "body", "text"],
        "",
      ),
      practiceQuestions: normalizePracticeQuestions(
        record.questions ?? record.practice_questions,
      ),
      quiz: normalizeQuiz(record.quiz, `${id}-quiz`, `${title} quiz`),
      furtherReading: [
        ...normalizeResources(
          record.further_reading ?? record.furtherReading ?? record.resources,
        ),
        ...markdownLinksToResources(record.further_reading_md),
      ],
      misconceptions: normalizeMisconceptions(record.misconceptions),
      meta: asRecord(record.meta),
    };
  });
}

export function createCoursePreviewFromCourseJson(
  value: unknown,
  options: CourseJsonPreviewOptions = {},
): CoursePreviewCourse {
  const courseJson = asRecord(value);
  const course = asRecord(courseJson.course);
  const grading = asRecord(courseJson.grading);
  const gradingPolicy = asRecord(grading.policy);

  const modules = normalizeModules(courseJson.modules);

  return {
    courseId: options.courseId,
    title: pickString(
      course,
      ["title"],
      options.fallbackTitle ?? "Untitled course",
    ),
    provider: pickString(
      course,
      ["provider", "institution"],
      "KIKO Auto-Generated",
    ),
    difficulty: pickString(course, ["level", "difficulty"], "Beginner"),
    language: pickString(course, ["language"], "English"),
    duration: minutesToDuration(course.estimated_minutes),
    progressPercent: Math.max(0, Math.min(100, options.progressPercent ?? 0)),
    overview: asString(
      courseJson.overview_md,
      options.fallbackOverview ||
        asString(modules[0]?.content, "No overview available yet."),
    ),
    modules,
    resources: normalizeResources(courseJson.resources),
    finalQuiz: normalizeQuiz(
      courseJson.final_quiz,
      "final-quiz",
      "Final assessment",
    ),
    tags: asStringArray(course.tags),
    prerequisites: asStringArray(course.prerequisites),
    instructors: asArray(courseJson.instructors).map((item, index) => {
      const record = asRecord(item);

      return {
        name: pickString(
          record,
          ["name", "full_name"],
          `Instructor ${index + 1}`,
        ),
        bio: pickString(record, ["bio", "description"], ""),
      };
    }),
    gradingNotes: asStringArray(gradingPolicy.notes),
    isEnrolled: options.isEnrolled,
  };
}
