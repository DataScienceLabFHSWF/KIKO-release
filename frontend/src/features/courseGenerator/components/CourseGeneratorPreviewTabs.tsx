// frontend/src/features/courseGenerator/components/CourseGeneratorPreviewTabs.tsx

import {
  AlertTriangle,
  BookOpen,
  BookOpenCheck,
  CheckCircle2,
  Clipboard,
  Code2,
  FileQuestion,
  GraduationCap,
  Layers3,
  ListChecks,
  Settings,
  Square,
} from "lucide-react";
import { useMemo, useState, useEffect } from "react";
import { useTranslation } from "node_modules/react-i18next";
import { Button } from "@/components";
import {
  CoursePreview,
  createCoursePreviewFromCourseJson,
  type CoursePreviewModuleTabKey,
  type CoursePreviewSectionKey,
} from "@/features/coursePreview";
import { GeneratedQaReviewTable } from "./GeneratedQaReviewTable";
import type {
  CourseJson,
  CourseJsonModule,
  CourseUploadResult,
  GeneratedQaReviewItem,
  QuestionAnswerItem,
} from "../types/CourseGenerator";
import {
  extractQuestions,
  getCourseSummary,
  getCourseTitle,
  getQuestionText,
  updateModuleAt,
  yamlParse,
  yamlStringify,
} from "../utils/CourseGeneratorUtils";

type PreviewTab =
  | "preview"
  | "course"
  | "modules"
  | "finalQuiz"
  | "qa"
  | "resources"
  | "raw";

type LearnerSection =
  | "overview"
  | "courseInfo"
  | "module"
  | "finalQuiz"
  | "grades"
  | "resources";

type ModuleSubTab =
  | "content"
  | "practice"
  | "quiz"
  | "furtherReading"
  | "misconceptions"
  | "meta";

type CourseGeneratorPreviewTabsProps = {
  result: CourseUploadResult;
  editedCourseJson: CourseJson | null;
  defaultReasoningModel: string;
  language: string;
  onCourseJsonChange: (value: CourseJson | null) => void;
  mode?: "preview" | "edit";
  showEditorTabs?: boolean;
};

type QuizChoice = {
  id?: string;
  text?: string;
  label?: string;
  correct?: boolean;
};

type QuizItem = {
  id?: string;
  type?: string;
  prompt?: string;
  question?: string;
  text?: string;
  points?: number;
  answer?: unknown;
  correct_answer?: unknown;
  choices?: QuizChoice[];
};

type QuizLike = {
  meta?: {
    id?: string;
    title?: string;
    points_total?: number;
    pass_percent?: number;
  };
  items?: QuizItem[];
};

type MisconceptionLike =
  | string
  | {
      misconception?: string;
      correction?: string;
      text?: string;
      title?: string;
      explanation?: string;
    };

const tabs: Array<{
  key: PreviewTab;
  labelKey: string;
  icon: React.ReactNode;
}> = [
  { key: "preview", labelKey: "tabs.preview", icon: <BookOpen size={16} /> },
  { key: "course", labelKey: "tabs.course", icon: <Settings size={16} /> },
  { key: "modules", labelKey: "tabs.modules", icon: <Layers3 size={16} /> },
  {
    key: "finalQuiz",
    labelKey: "tabs.finalQuiz",
    icon: <GraduationCap size={16} />,
  },
  { key: "qa", labelKey: "tabs.qa", icon: <FileQuestion size={16} /> },
  {
    key: "resources",
    labelKey: "tabs.resources",
    icon: <ListChecks size={16} />,
  },
  { key: "raw", labelKey: "tabs.raw", icon: <Code2 size={16} /> },
];

function getQuizData(value: unknown): QuizLike {
  if (!value || typeof value !== "object") {
    return {};
  }

  return value as QuizLike;
}

function getQuizTitle(quiz: QuizLike, fallback: string) {
  return quiz.meta?.title || fallback;
}

function getQuizPassPercent(quiz: QuizLike) {
  return quiz.meta?.pass_percent ?? 70;
}

function getQuizItems(quiz: QuizLike) {
  return Array.isArray(quiz.items) ? quiz.items : [];
}

function getQuizPrompt(item: QuizItem) {
  return item.prompt ?? item.question ?? item.text ?? "Untitled question";
}

function getCorrectAnswerText(item: QuizItem) {
  if (item.type === "true_false") {
    return String(item.answer ?? item.correct_answer ?? "—");
  }

  const correctChoice = item.choices?.find((choice) => choice.correct);
  return (
    correctChoice?.text ?? correctChoice?.label ?? String(item.answer ?? "—")
  );
}

function getResourceTitle(resource: Record<string, unknown>, index: number) {
  return String(resource.title ?? resource.name ?? `Resource ${index + 1}`);
}

function getResourceType(resource: Record<string, unknown>) {
  return String(resource.type ?? "resource");
}

function getResourceUrl(resource: Record<string, unknown>) {
  const url = resource.url ?? resource.link ?? resource.href;
  return typeof url === "string" ? url : "";
}

function ReadOnlyField({
  label,
  value,
}: {
  label: string;
  value?: string | number | null;
}) {
  return (
    <label className="course-generator-readonly-field">
      <span>{label}</span>
      <input value={value ?? "—"} readOnly aria-readonly="true" />
    </label>
  );
}

function EditableField({
  label,
  value,
  onChange,
  type = "text",
}: {
  label: string;
  value: string | number;
  type?: "text" | "number";
  onChange: (value: string) => void;
}) {
  return (
    <label className="course-generator-editable-field">
      <span>{label}</span>
      <input
        type={type}
        value={value}
        onChange={(event) => onChange(event.currentTarget.value)}
      />
    </label>
  );
}

function EditableTextarea({
  label,
  value,
  minHeight = 180,
  onChange,
}: {
  label: string;
  value: string;
  minHeight?: number;
  onChange: (value: string) => void;
}) {
  return (
    <label className="course-generator-editable-textarea">
      <span>{label}</span>
      <textarea
        value={value}
        style={{ minHeight }}
        onChange={(event) => onChange(event.currentTarget.value)}
      />
    </label>
  );
}

function YamlEditor<T>({
  label,
  value,
  minHeight = 220,
  onValidChange,
}: {
  label: string;
  value: T;
  minHeight?: number;
  onValidChange: (value: T) => void;
}) {
  const [text, setText] = useState(yamlStringify(value));
  const [error, setError] = useState<string | null>(null);
  const { t } = useTranslation("courseGenerator");

  function handleChange(nextText: string) {
    setText(nextText);

    try {
      const parsed = yamlParse<T>(nextText);
      onValidChange(parsed);
      setError(null);
    } catch (parseError) {
      setError(
        parseError instanceof Error
          ? parseError.message
          : t("editor.invalidYaml"),
      );
    }
  }

  return (
    <label className="course-generator-yaml-editor">
      <span>{label}</span>
      <textarea
        value={text}
        style={{ minHeight }}
        spellCheck={false}
        onChange={(event) => handleChange(event.currentTarget.value)}
      />
      {error && (
        <small className="course-generator-yaml-editor__error">{error}</small>
      )}
    </label>
  );
}

function getMisconceptionText(item: MisconceptionLike) {
  if (typeof item === "string") {
    return item.trim();
  }

  return String(item.misconception ?? item.text ?? item.title ?? "").trim();
}

function getMisconceptionCorrection(item: MisconceptionLike) {
  if (typeof item === "string") {
    return "";
  }

  return String(item.correction ?? item.explanation ?? "").trim();
}

function normalizeQuestionText(value: string): string {
  return value.trim().toLowerCase().replace(/\s+/g, " ");
}

function normalizeModuleMisconceptions(value: unknown): string[] {
  if (value === null || value === undefined) {
    return [];
  }

  const items = Array.isArray(value) ? value : [value];

  return items
    .map((item) => {
      if (typeof item === "string") {
        return item.trim();
      }

      if (item && typeof item === "object") {
        return getMisconceptionText(item as MisconceptionLike);
      }

      return "";
    })
    .filter(Boolean);
}

function getModuleQuestions(module: CourseJsonModule): QuestionAnswerItem[] {
  if (Array.isArray(module.questions) && module.questions.length > 0) {
    return module.questions;
  }

  if (Array.isArray(module.practice_questions)) {
    return module.practice_questions;
  }

  return [];
}

export function CourseGeneratorPreviewTabs({
  result,
  editedCourseJson,
  defaultReasoningModel,
  language,
  onCourseJsonChange,
  mode = "edit",
  showEditorTabs = true,
}: CourseGeneratorPreviewTabsProps) {
  const { t } = useTranslation("courseGenerator");
  const [activeTab, setActiveTab] = useState<PreviewTab>("preview");
  const [learnerSection, setLearnerSection] =
    useState<LearnerSection>("overview");
  const [activeModuleIndex, setActiveModuleIndex] = useState(0);
  const [moduleSubTab, setModuleSubTab] = useState<ModuleSubTab>("content");
  const [copied, setCopied] = useState(false);
  const [previewSection, setPreviewSection] =
    useState<CoursePreviewSectionKey>("overview");
  const courseJson = editedCourseJson ?? result.course_json ?? {};
  const course = courseJson.course ?? {};
  const modules = courseJson.modules ?? [];
  const resources = (courseJson.resources ?? []) as Array<
    Record<string, unknown>
  >;
  const instructors = courseJson.instructors ?? [];
  const grading = courseJson.grading ?? {};
  const questions = useMemo(
    () => extractQuestions(result.questions, courseJson),
    [result.questions, courseJson],
  );
  const activeModule = modules[activeModuleIndex];
  const activeModuleQuiz = getQuizData(activeModule?.quiz);
  const finalQuiz = getQuizData(courseJson.final_quiz);
  const visibleTabs =
    mode === "preview"
      ? tabs.filter((tab) => tab.key === "preview")
      : showEditorTabs
        ? tabs
        : tabs.filter((tab) => tab.key === "preview");

  const rawJson = useMemo(
    () => JSON.stringify(courseJson, null, 2),
    [courseJson],
  );

  const previewCourse = useMemo(
    () =>
      createCoursePreviewFromCourseJson(courseJson, {
        fallbackTitle: getCourseTitle(courseJson),
        fallbackOverview: getCourseSummary(result, courseJson),
        progressPercent: 0,
        isEnrolled: true,
      }),
    [courseJson, result],
  );

  const qaReviewItems = useMemo<GeneratedQaReviewItem[]>(() => {
    type ModuleContext = {
      moduleId?: string;
      moduleTitle?: string;
      misconceptions: string[];
    };

    const contextByQuestionId = new Map<string, ModuleContext>();
    const contextByQuestionText = new Map<string, ModuleContext>();

    modules.forEach((module, moduleIndex) => {
      const moduleId = String(module.id ?? `module-${moduleIndex + 1}`);
      const moduleTitle = module.title ?? `Module ${moduleIndex + 1}`;

      const misconceptions = normalizeModuleMisconceptions(
        module.misconceptions,
      );

      const context: ModuleContext = {
        moduleId,
        moduleTitle,
        misconceptions,
      };

      const moduleQuestions = getModuleQuestions(module);

      moduleQuestions.forEach((question) => {
        /*
         * Best match:
         * use question ID when the generated course has one.
         */
        const questionId =
          typeof question.id === "string" ? question.id.trim() : "";

        if (questionId) {
          contextByQuestionId.set(questionId, context);
        }

        /*
         * Fallback:
         * match normalized question text.
         *
         * This supports generated data where the flattened Q&A list
         * does not preserve module_id.
         */
        const questionText = normalizeQuestionText(getQuestionText(question));

        if (questionText && !contextByQuestionText.has(questionText)) {
          contextByQuestionText.set(questionText, context);
        }
      });
    });

    return questions.map((question) => {
      const questionId =
        typeof question.id === "string" ? question.id.trim() : "";

      const questionText = normalizeQuestionText(getQuestionText(question));

      /*
       * Prefer explicit module_id when the backend/generator
       * provides it.
       */
      let context: ModuleContext | undefined;

      if (question.module_id) {
        const moduleIndex = modules.findIndex(
          (module, index) =>
            String(module.id ?? `module-${index + 1}`) ===
            String(question.module_id),
        );

        if (moduleIndex >= 0) {
          const module = modules[moduleIndex];

          context = {
            moduleId: String(module.id ?? `module-${moduleIndex + 1}`),
            moduleTitle: module.title ?? `Module ${moduleIndex + 1}`,
            misconceptions: normalizeModuleMisconceptions(
              module.misconceptions,
            ),
          };
        }
      }

      /*
       * Second choice: question ID.
       */
      if (!context && questionId) {
        context = contextByQuestionId.get(questionId);
      }

      /*
       * Last fallback: question text.
       */
      if (!context && questionText) {
        context = contextByQuestionText.get(questionText);
      }

      return {
        question,
        moduleId: context?.moduleId,
        moduleTitle: context?.moduleTitle,
        misconceptions: context?.misconceptions ?? [],
      };
    });
  }, [questions, modules]);

  const previewModuleTab: CoursePreviewModuleTabKey =
    moduleSubTab === "furtherReading"
      ? "further-reading"
      : (moduleSubTab as CoursePreviewModuleTabKey);

  function handlePreviewSectionChange(nextSection: CoursePreviewSectionKey) {
    setPreviewSection(nextSection);

    if (!nextSection.startsWith("module:")) return;

    const moduleId = nextSection.replace("module:", "");
    const index = modules.findIndex(
      (module, moduleIndex) =>
        String(module.id ?? `module-${moduleIndex + 1}`) === moduleId,
    );

    if (index >= 0) {
      setActiveModuleIndex(index);
      setModuleSubTab("content");
    }
  }

  function handlePreviewModuleTabChange(nextTab: CoursePreviewModuleTabKey) {
    setModuleSubTab(nextTab === "further-reading" ? "furtherReading" : nextTab);
  }

  function updateCourse(next: Partial<NonNullable<CourseJson["course"]>>) {
    onCourseJsonChange({
      ...courseJson,
      course: {
        ...courseJson.course,
        ...next,
      },
    });
  }

  function updateActiveModule(
    updater: (module: CourseJsonModule) => CourseJsonModule,
  ) {
    onCourseJsonChange(updateModuleAt(courseJson, activeModuleIndex, updater));
  }

  async function copyRawJson() {
    await navigator.clipboard.writeText(rawJson);
    setCopied(true);
    window.setTimeout(() => setCopied(false), 1800);
  }

  useEffect(() => {
    if (mode === "preview") {
      setActiveTab("preview");
    }
  }, [mode]);

  return (
    <section className="course-generator-preview">
      <nav
        className="course-generator-tabs"
        aria-label="Generated course editor sections"
      >
        {visibleTabs.map((tab) => (
          <Button
            key={tab.key}
            type="button"
            variant="plain"
            className={activeTab === tab.key ? "is-active" : ""}
            onClick={() => setActiveTab(tab.key)}
          >
            {tab.icon}
            {t(tab.labelKey)}
          </Button>
        ))}
      </nav>

      {activeTab === "preview" && (
        <CoursePreview
          course={previewCourse}
          activeSection={previewSection}
          activeModuleTab={previewModuleTab}
          onSectionChange={handlePreviewSectionChange}
          onModuleTabChange={handlePreviewModuleTabChange}
        />
      )}

      {activeTab === "course" && (
        <div className="course-generator-editor-panel">
          <div className="course-generator-editor-grid course-generator-editor-grid--three">
            <EditableField
              label={t("editor.courseTitle")}
              value={course.title ?? ""}
              onChange={(value) => updateCourse({ title: value })}
            />

            <ReadOnlyField
              label={t("editor.provider")}
              value={course.provider}
            />
            <ReadOnlyField
              label={t("editor.language")}
              value={course.language}
            />

            <EditableField
              label={t("editor.level")}
              value={course.level ?? ""}
              onChange={(value) => updateCourse({ level: value })}
            />

            <ReadOnlyField label={t("editor.courseId")} value={course.id} />

            <EditableField
              label={t("editor.estimatedMinutes")}
              type="number"
              value={course.estimated_minutes ?? 60}
              onChange={(value) =>
                updateCourse({ estimated_minutes: Number(value) || 60 })
              }
            />
          </div>

          <EditableField
            label={t("editor.tagsCommaSeparated")}
            value={(course.tags ?? []).join(", ")}
            onChange={(value) =>
              updateCourse({
                tags: value
                  .split(",")
                  .map((item) => item.trim())
                  .filter(Boolean),
              })
            }
          />

          <EditableTextarea
            label={t("editor.prerequisitesOnePerLine")}
            value={(course.prerequisites ?? []).join("\n")}
            minHeight={90}
            onChange={(value) =>
              updateCourse({
                prerequisites: value
                  .split("\n")
                  .map((item) => item.trim())
                  .filter(Boolean),
              })
            }
          />

          <EditableTextarea
            label={t("editor.courseOverviewMarkdown")}
            value={getCourseSummary(result, courseJson)}
            minHeight={220}
            onChange={(value) => {
              if (!modules[0]) return;

              onCourseJsonChange(
                updateModuleAt(courseJson, 0, (module) => ({
                  ...module,
                  content_md: value,
                })),
              );
            }}
          />
        </div>
      )}

      {activeTab === "modules" && (
        <div className="course-generator-editor-panel">
          {modules.length === 0 ? (
            <p className="course-generator-empty">
              {t("editor.noModulesGenerated")}
            </p>
          ) : (
            <>
              <label className="course-generator-editable-field">
                <span>{t("editor.selectModule")}</span>
                <select
                  value={activeModuleIndex}
                  onChange={(event) =>
                    setActiveModuleIndex(Number(event.currentTarget.value))
                  }
                >
                  {modules.map((module, index) => (
                    <option key={module.id ?? index} value={index}>
                      Module {index + 1}: {module.title || "Untitled module"}
                    </option>
                  ))}
                </select>
              </label>

              {activeModule && (
                <>
                  <EditableField
                    label={t("editor.moduleTitle")}
                    value={activeModule.title ?? ""}
                    onChange={(value) =>
                      updateActiveModule((module) => ({
                        ...module,
                        title: value,
                      }))
                    }
                  />

                  <EditableTextarea
                    label={t("editor.contentMarkdown")}
                    value={
                      activeModule.content_md ?? activeModule.content ?? ""
                    }
                    minHeight={260}
                    onChange={(value) =>
                      updateActiveModule((module) => ({
                        ...module,
                        content_md: value,
                      }))
                    }
                  />

                  <YamlEditor
                    label={t("editor.practiceQuestionsYaml")}
                    value={
                      activeModule.questions ??
                      activeModule.practice_questions ??
                      []
                    }
                    minHeight={240}
                    onValidChange={(value) =>
                      updateActiveModule((module) => ({
                        ...module,
                        questions: Array.isArray(value) ? value : [],
                      }))
                    }
                  />

                  <YamlEditor
                    label={t("editor.quizYaml")}
                    value={activeModule.quiz ?? {}}
                    minHeight={260}
                    onValidChange={(value) =>
                      updateActiveModule((module) => ({
                        ...module,
                        quiz:
                          value && typeof value === "object"
                            ? (value as Record<string, unknown>)
                            : {},
                      }))
                    }
                  />

                  <EditableTextarea
                    label={t("editor.furtherReadingMarkdown")}
                    value={
                      activeModule.further_reading_md ??
                      yamlStringify(activeModule.further_reading ?? [])
                    }
                    minHeight={150}
                    onChange={(value) =>
                      updateActiveModule((module) => ({
                        ...module,
                        further_reading_md: value,
                      }))
                    }
                  />

                  <YamlEditor
                    label={t("editor.misconceptionsYaml")}
                    value={activeModule.misconceptions ?? []}
                    minHeight={180}
                    onValidChange={(value) =>
                      updateActiveModule((module) => ({
                        ...module,
                        misconceptions: value,
                      }))
                    }
                  />
                </>
              )}
            </>
          )}
        </div>
      )}

      {activeTab === "finalQuiz" && (
        <div className="course-generator-editor-panel">
          <YamlEditor
            label={t("editor.finalQuizYaml")}
            value={courseJson.final_quiz ?? {}}
            minHeight={520}
            onValidChange={(value) =>
              onCourseJsonChange({
                ...courseJson,
                final_quiz:
                  value && typeof value === "object"
                    ? (value as Record<string, unknown>)
                    : {},
              })
            }
          />
        </div>
      )}

      {activeTab === "qa" && (
        <GeneratedQaReviewTable
          items={qaReviewItems}
          defaultReasoningModel={defaultReasoningModel}
          language={language}
        />
      )}

      {activeTab === "resources" && (
        <div className="course-generator-editor-panel">
          <YamlEditor
            label={t("editor.instructorsYaml")}
            value={instructors}
            minHeight={160}
            onValidChange={(value) =>
              onCourseJsonChange({
                ...courseJson,
                instructors: Array.isArray(value) ? value : [],
              })
            }
          />

          <YamlEditor
            label={t("editor.resourcesYaml")}
            value={resources}
            minHeight={220}
            onValidChange={(value) =>
              onCourseJsonChange({
                ...courseJson,
                resources: Array.isArray(value) ? value : [],
              })
            }
          />

          <YamlEditor
            label={t("editor.gradingYaml")}
            value={grading}
            minHeight={240}
            onValidChange={(value) =>
              onCourseJsonChange({
                ...courseJson,
                grading:
                  value && typeof value === "object"
                    ? (value as Record<string, unknown>)
                    : {},
              })
            }
          />
        </div>
      )}

      {activeTab === "raw" && (
        <div className="course-generator-raw-json">
          <div className="course-generator-raw-json__header">
            <h3>{t("raw.title")}</h3>

            <Button
              type="button"
              variant="ghost"
              className="course-generator-action-button"
              onClick={() => void copyRawJson()}
            >
              <Clipboard size={16} />
              {copied ? t("raw.copied") : t("raw.copy")}
            </Button>
          </div>

          <pre>{rawJson}</pre>
        </div>
      )}
    </section>
  );
}
