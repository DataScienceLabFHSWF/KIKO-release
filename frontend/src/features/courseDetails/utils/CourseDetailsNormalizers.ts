// frontend/src/features/courseDetails/utils/CourseDetailsNormalizers.ts

import type {
  CourseQuizQuestion,
  LearnerCourseDetailsResponse,
  NormalizedCourseDetails,
  NormalizedCourseModule,
  NormalizedCourseQuiz,
  NormalizedCourseResource,
  CourseQuestionType,
  NormalizedFinalAssessmentStatus,
  PersistedQuizAttempt,
  LearnerQuizAnswerItem,
  QuizAnswerValue,
  QuizAnswers,
  LearnerQuizSubmitResponse,
  PersistedQuizAttempts,
} from "../types/LearnerCourseDetails";

function asRecord(value: unknown): Record<string, unknown> {
  return value && typeof value === "object" && !Array.isArray(value)
    ? (value as Record<string, unknown>)
    : {};
}

function asArray(value: unknown): unknown[] {
  return Array.isArray(value) ? value : [];
}

function asString(value: unknown, fallback = ""): string {
  return typeof value === "string" && value.trim() ? value : fallback;
}

function asNumber(value: unknown, fallback = 0): number {
  const numberValue = Number(value);
  return Number.isFinite(numberValue) ? numberValue : fallback;
}

function asStringArray(value: unknown): string[] {
  if (!Array.isArray(value)) {
    return [];
  }

  return value
    .filter((item): item is string => typeof item === "string")
    .map((item) => item.trim())
    .filter(Boolean);
}

function asOptionalNumber(value: unknown): number | null {
  if (typeof value === "number" && Number.isFinite(value)) {
    return value;
  }

  if (typeof value === "string") {
    const parsed = Number(value);

    if (Number.isFinite(parsed)) {
      return parsed;
    }
  }

  return null;
}

function clampPercent(value: unknown) {
  return Math.max(0, Math.min(100, Math.round(asNumber(value, 0))));
}

function pickString(
  source: Record<string, unknown>,
  keys: string[],
  fallback = "",
): string {
  for (const key of keys) {
    const value = source[key];

    if (typeof value === "string" && value.trim()) {
      return value;
    }
  }

  return fallback;
}

function estimatedMinutesToDuration(value: unknown): string {
  const minutes = asNumber(value, 0);

  if (!minutes) return "1h";
  if (minutes < 60) return `${minutes} min`;

  const hours = minutes / 60;

  return Number.isInteger(hours) ? `${hours}h` : `${hours.toFixed(1)}h`;
}

function normalizeResources(value: unknown): NormalizedCourseResource[] {
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

function markdownLinksToResources(value: unknown): NormalizedCourseResource[] {
  const markdown = asString(value);

  if (!markdown) return [];

  const resources: NormalizedCourseResource[] = [];
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

function normalizeQuestionType(value: unknown): CourseQuestionType {
  const raw = typeof value === "string" ? value.toLowerCase() : "";

  if (raw === "multi_select" || raw === "multiple_choice_multi") {
    return "multi_select";
  }

  if (raw === "true_false" || raw === "boolean") {
    return "true_false";
  }

  return "single_select";
}

function normalizeChoices(value: unknown, questionType: CourseQuestionType) {
  const rawChoices = asArray(value);

  if (rawChoices.length > 0) {
    return rawChoices.map((item, index) => {
      if (typeof item === "string") {
        return {
          id: item,
          text: item,
        };
      }

      const record = asRecord(item);

      return {
        id: pickString(
          record,
          ["id", "choice_id", "key", "value"],
          `choice_${index + 1}`,
        ),
        text: pickString(
          record,
          ["text", "label", "answer", "title"],
          `Option ${index + 1}`,
        ),
      };
    });
  }

  if (questionType === "true_false") {
    return [
      { id: "true", text: "True" },
      { id: "false", text: "False" },
    ];
  }

  return [];
}

function normalizeQuestions(value: unknown): CourseQuizQuestion[] {
  return asArray(value).map((item, index) => {
    const record = asRecord(item);
    const type = normalizeQuestionType(record.type);

    return {
      item_id: pickString(
        record,
        ["item_id", "id", "question_id", "key"],
        `q${index + 1}`,
      ),
      text: pickString(
        record,
        ["question", "text", "prompt", "title"],
        `Question ${index + 1}`,
      ),
      type,
      points: asNumber(record.points, 1),
      choices: normalizeChoices(
        record.choices ?? record.options ?? record.answers,
        type,
      ),
    };
  });
}

function normalizeQuiz(
  value: unknown,
  fallbackAssessmentId: string,
  fallbackTitle: string,
): NormalizedCourseQuiz | null {
  const record = asRecord(value);
  const meta = asRecord(record.meta);

  const questions = normalizeQuestions(
    record.questions ?? record.items ?? record.quiz_items,
  );

  if (questions.length === 0) return null;

  return {
    assessment_id: pickString(
      meta,
      ["id", "assessment_id", "quiz_id"],
      pickString(
        record,
        ["id", "assessment_id", "quiz_id"],
        fallbackAssessmentId,
      ),
    ),
    title: pickString(
      meta,
      ["title", "name"],
      pickString(record, ["title", "name"], fallbackTitle),
    ),
    pass_threshold: asNumber(
      meta.pass_percent ??
        meta.pass_threshold ??
        record.pass_percent ??
        record.pass_threshold,
      70,
    ),
    questions,
  };
}

function normalizePracticeQuestions(value: unknown) {
  return asArray(value).map((item, index) => {
    const record = asRecord(item);

    return {
      id: pickString(record, ["id", "question_id"], `practice_${index + 1}`),
      prompt: pickString(record, ["prompt", "question", "text"], ""),
      referenceAnswer: pickString(
        record,
        ["reference_answer", "referenceAnswer"],
        "",
      ),
      points: asNumber(record.points, 1),
    };
  });
}

function normalizeMisconceptions(value: unknown): string[] {
  return asArray(value).map((item) => {
    if (typeof item === "string") return item;

    const record = asRecord(item);
    const misconception = pickString(record, ["misconception"], "");
    const correction = pickString(record, ["correction"], "");

    if (misconception && correction) {
      return `${misconception} — ${correction}`;
    }

    return misconception || correction;
  });
}

function normalizeModules(value: unknown): NormalizedCourseModule[] {
  return asArray(value).map((item, index) => {
    const record = asRecord(item);

    const id = pickString(record, ["module_id", "id", "key"], `m${index + 1}`);

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
      practiceQuestions: normalizePracticeQuestions(record.questions),
      practiceText: "",
      quiz: normalizeQuiz(record.quiz, `${id}-quiz`, `${title} quiz`),
      furtherReading: [
        ...normalizeResources(
          record.further_reading ?? record.furtherReading ?? record.resources,
        ),
        ...markdownLinksToResources(record.further_reading_md),
      ],
      misconceptions: normalizeMisconceptions(record.misconceptions),
    };
  });
}

function normalizeQuizAnswerValue(
  item: LearnerQuizAnswerItem,
): QuizAnswerValue {
  const selectedIds = Array.isArray(item.selected_choice_ids)
    ? item.selected_choice_ids.map(String).filter(Boolean)
    : [];

  if (selectedIds.length > 1) {
    return selectedIds;
  }

  if (selectedIds.length === 1) {
    return selectedIds[0];
  }

  if (Array.isArray(item.selected_value)) {
    return item.selected_value.map(String).filter(Boolean);
  }

  if (
    item.selected_value !== null &&
    item.selected_value !== undefined &&
    String(item.selected_value).trim() !== ""
  ) {
    return String(item.selected_value);
  }

  return "";
}

export function quizAttemptToAnswers(
  attempt?: PersistedQuizAttempt | null,
): QuizAnswers {
  if (!attempt?.submitted_answers?.length) {
    return {};
  }

  return Object.fromEntries(
    attempt.submitted_answers.map((item) => [
      item.item_id,
      normalizeQuizAnswerValue(item),
    ]),
  );
}

export function quizAttemptToResult(
  attempt?: PersistedQuizAttempt | null,
): LearnerQuizSubmitResponse | null {
  if (!attempt) {
    return null;
  }

  return {
    message: "loaded",
    assessment_id: attempt.assessment_id,
    module_id: attempt.module_id ?? null,
    score: attempt.score ?? null,
    max_score: attempt.max_score ?? null,
    percent: attempt.percent ?? null,
    passed: attempt.passed ?? null,
    german_grade: attempt.german_grade ?? null,
    graded_answers: attempt.graded_answers ?? [],
  };
}

function normalizeFinalAssessmentStatus(
  raw: unknown,
  moduleStatusRaw: unknown,
): NormalizedFinalAssessmentStatus {
  const record = asRecord(raw);
  const moduleStatus = asRecord(moduleStatusRaw);

  const requiredModules = asStringArray(record.required_modules);

  const explicitMissingModules = asStringArray(record.missing_required_modules);

  const derivedMissingModules =
    explicitMissingModules.length > 0
      ? explicitMissingModules
      : requiredModules.filter((moduleId) => {
          const status = asRecord(moduleStatus[moduleId]);
          return !Boolean(status.quiz_passed);
        });

  const isEligible =
    typeof record.eligible_for_final_quiz === "boolean"
      ? record.eligible_for_final_quiz
      : derivedMissingModules.length === 0;

  return {
    isEligible,
    requiredModules,
    missingRequiredModules: derivedMissingModules,
    completed: Boolean(record.completed),
    weightedPercent: asOptionalNumber(record.weighted_percent),
    germanGrade:
      typeof record.german_grade === "string" ||
      typeof record.german_grade === "number"
        ? record.german_grade
        : null,
  };
}

export function normalizeCourseDetails(
  response: LearnerCourseDetailsResponse,
): NormalizedCourseDetails {
  const courseJson = asRecord(response.course_json);
  const courseMeta = asRecord(courseJson.course);
  const grading = asRecord(courseJson.grading);
  const gradingPolicy = asRecord(grading.policy);
  const gradingCompletion = asRecord(gradingPolicy.completion);

  const modules = normalizeModules(courseJson.modules);

  const progressPercent = clampPercent(
    response.progress_snapshot?.completion_percent ??
      response.enrollment?.completion_percent,
  );

  const courseCompletion = asRecord(
    response.progress_snapshot?.course_completion,
  );

  const latestAttemptsRecord = asRecord(response.latest_attempts);
  const moduleAttempts = asRecord(latestAttemptsRecord.module_quizzes);

  const latestAttempts: PersistedQuizAttempts = {
    module_quizzes: Object.fromEntries(
      Object.entries(moduleAttempts).map(([moduleId, value]) => [
        moduleId,
        value as PersistedQuizAttempt,
      ]),
    ),
    final_quiz:
      latestAttemptsRecord.final_quiz &&
      typeof latestAttemptsRecord.final_quiz === "object"
        ? (latestAttemptsRecord.final_quiz as PersistedQuizAttempt)
        : null,
  };

  return {
    courseId: response.course.course_id,
    title: response.course.title,
    summary: asString(response.course.summary),
    overview: pickString(
      courseJson,
      ["overview_md"],
      asString(response.course.summary),
    ),
    difficulty: pickString(courseMeta, ["level", "difficulty"], "Beginner"),
    language: pickString(courseMeta, ["language"], "English"),
    duration: estimatedMinutesToDuration(courseMeta.estimated_minutes),
    provider: pickString(courseMeta, ["provider", "institution"], "KIKO"),
    modules,
    resources: normalizeResources(courseJson.resources),
    finalQuiz: normalizeQuiz(
      courseJson.final_quiz,
      "final-quiz",
      "Final assessment",
    ),
    skills: asArray(courseMeta.tags ?? courseJson.tags).map((item) =>
      String(item),
    ),
    prerequisites: asArray(courseMeta.prerequisites).map((item) =>
      String(item),
    ),
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
    grading: {
      passPercent: asNumber(grading.pass_percent, 70),
      assessmentWeights: asRecord(grading.assessment_weights),
      requiredModules: asArray(gradingCompletion.required_modules).map((item) =>
        String(item),
      ),
      requiredAssessments: asArray(gradingCompletion.required_assessments).map(
        (item) => String(item),
      ),
      notes: asArray(asRecord(gradingPolicy).notes).map((item) => String(item)),
    },
    progressPercent,
    isEnrolled: Boolean(response.enrollment?.is_enrolled),
    finalAssessmentStatus: normalizeFinalAssessmentStatus(
      courseCompletion,
      response.progress_snapshot?.module_status,
    ),
    latestAttempts,
  };
}
