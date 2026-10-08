// frontend/src/features/courses/components/InstructorCourseAccordion.tsx

import { useEffect, useMemo, useState } from "react";
import {
  ChevronDown,
  Eye,
  Pencil,
  RotateCcw,
  Save,
  Trash2,
} from "lucide-react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useTranslation } from "node_modules/react-i18next";

import { Button, ErrorState, LoadingState } from "@/components";
import { CourseGeneratorPreviewTabs } from "@/features/courseGenerator/components/CourseGeneratorPreviewTabs";
import {
  CoursePreview,
  createCoursePreviewFromCourseJson,
} from "@/features/coursePreview";

import {
  courseQueryKeys,
  getInstructorCourseDetails,
  updateInstructorCourse,
} from "../api/CoursesApi";
import type {
  InstructorCourse,
  InstructorCourseDetails,
  InstructorCourseUpdateRequest,
} from "../types/Courses";

import "./InstructorCourseAccordion.css";

type ViewMode = "preview" | "edit";
type CourseJson = Record<string, unknown>;

type InstructorCourseAccordionProps = {
  course: InstructorCourse;
  isDeleting?: boolean;
  onDelete: (course: InstructorCourse) => void;
};

function getCourseJson(details: InstructorCourseDetails): CourseJson {
  return details.course_json ?? {};
}

function getCourseTitleFromJson(courseJson: CourseJson, fallback: string) {
  const course = courseJson.course;

  if (course && typeof course === "object" && "title" in course) {
    const title = String(
      (course as Record<string, unknown>).title ?? "",
    ).trim();

    if (title) return title;
  }

  return fallback;
}

function getCourseSummaryFromJson(
  courseJson: CourseJson,
  fallback?: string | null,
) {
  const overview = courseJson.overview_md;

  if (typeof overview === "string" && overview.trim()) {
    return overview.trim();
  }

  const modules = courseJson.modules;

  if (Array.isArray(modules)) {
    const firstModule = modules[0];

    if (firstModule && typeof firstModule === "object") {
      const moduleRecord = firstModule as Record<string, unknown>;
      const content =
        moduleRecord.content_md ?? moduleRecord.content ?? moduleRecord.summary;

      if (typeof content === "string" && content.trim()) {
        return content.trim();
      }
    }
  }

  return fallback ?? "";
}

function buildPreviewResult(details: InstructorCourseDetails) {
  return {
    message: "success",
    course_id: details.course_id,
    title: details.title,
    summary: details.summary ?? "",
    questions: details.questions ?? [],
    course_json: getCourseJson(details),
    has_course_json: Boolean(details.course_json),
  };
}

function buildUpdatePayload(
  details: InstructorCourseDetails,
  editableCourseJson: CourseJson,
): InstructorCourseUpdateRequest {
  return {
    title: getCourseTitleFromJson(editableCourseJson, details.title),
    summary: getCourseSummaryFromJson(editableCourseJson, details.summary),
    quiz: details.quiz ?? null,
    template_markdown: details.template_markdown ?? null,
    course_json: editableCourseJson,
    questions: details.questions?.map((question) => ({
      question_id: question.question_id,
      text: question.text ?? "",
      answer_text: question.answer_text ?? "",
    })),
  };
}

export function InstructorCourseAccordion({
  course,
  isDeleting = false,
  onDelete,
}: InstructorCourseAccordionProps) {
  const queryClient = useQueryClient();
  const { t, i18n } = useTranslation("courses");

  const language = i18n.language.startsWith("de") ? "de" : "en";

  const [isOpen, setIsOpen] = useState(false);
  const [mode, setMode] = useState<ViewMode>("preview");
  const [editedCourseJson, setEditedCourseJson] = useState<CourseJson | null>(
    null,
  );

  const detailsQuery = useQuery({
    queryKey: courseQueryKeys.instructorDetails(course.course_id),
    queryFn: () => getInstructorCourseDetails(course.course_id),
    enabled: isOpen,
  });

  const details = detailsQuery.data;

  useEffect(() => {
    if (!details) return;
    setEditedCourseJson(getCourseJson(details));
  }, [details]);

  const hasUnsavedChanges = useMemo(() => {
    if (!details || !editedCourseJson) return false;

    return (
      JSON.stringify(getCourseJson(details)) !==
      JSON.stringify(editedCourseJson)
    );
  }, [details, editedCourseJson]);

  const previewCourse = useMemo(() => {
    if (!details || !editedCourseJson) return null;

    return createCoursePreviewFromCourseJson(editedCourseJson, {
      courseId: details.course_id,
      fallbackTitle: details.title,
      fallbackOverview: details.summary ?? "",
      progressPercent: 0,
      isEnrolled: true,
    });
  }, [details, editedCourseJson]);

  const updateMutation = useMutation({
    mutationFn: (payload: InstructorCourseUpdateRequest) =>
      updateInstructorCourse(course.course_id, payload),
    onSuccess: async () => {
      await queryClient.invalidateQueries({
        queryKey: courseQueryKeys.instructor,
      });

      await queryClient.invalidateQueries({
        queryKey: courseQueryKeys.instructorDetails(course.course_id),
      });

      setMode("preview");
    },
  });

  function openInMode(nextMode: ViewMode) {
    setIsOpen(true);
    setMode(nextMode);
  }

  function handleReset() {
    if (!details) return;
    setEditedCourseJson(getCourseJson(details));
  }

  function handleSave() {
    if (!details || !editedCourseJson) return;
    updateMutation.mutate(buildUpdatePayload(details, editedCourseJson));
  }

  return (
    <article className="instructor-course-accordion">
      <header className="instructor-course-accordion__summary">
        <Button
          type="button"
          variant="plain"
          className="instructor-course-accordion__toggle"
          onClick={() => setIsOpen((current) => !current)}
          aria-expanded={isOpen}
        >
          <ChevronDown
            size={18}
            strokeWidth={2.3}
            className={isOpen ? "is-open" : undefined}
            aria-hidden="true"
          />

          <span>
            {t("course")} #{course.course_id}: {course.title}
          </span>
        </Button>

        <div className="instructor-course-accordion__actions">
          <Button
            type="button"
            variant={isOpen && mode === "preview" ? "primary" : "ghost"}
            onClick={() => openInMode("preview")}
          >
            <Eye size={16} strokeWidth={2.3} />
            {t("actions.preview")}
          </Button>

          <Button
            type="button"
            variant={isOpen && mode === "edit" ? "primary" : "ghost"}
            onClick={() => openInMode("edit")}
          >
            <Pencil size={16} strokeWidth={2.3} />
            {t("actions.edit")}
          </Button>

          <Button
            type="button"
            variant="danger"
            isLoading={isDeleting}
            onClick={() => onDelete(course)}
          >
            <Trash2 size={16} strokeWidth={2.3} />
            {t("actions.delete")}
          </Button>
        </div>
      </header>

      {isOpen && (
        <div className="instructor-course-accordion__body">
          {detailsQuery.isLoading && (
            <LoadingState description="Loading course details..." />
          )}

          {detailsQuery.isError && (
            <ErrorState
              title="Could not load course"
              description={
                detailsQuery.error instanceof Error
                  ? detailsQuery.error.message
                  : "Unexpected error while loading the course."
              }
              actionLabel="Retry"
              onAction={() => void detailsQuery.refetch()}
            />
          )}

          {details && editedCourseJson && (
            <>
              {mode === "edit" && (
                <div className="instructor-course-accordion__edit-toolbar">
                  <Button
                    type="button"
                    variant="ghost"
                    onClick={handleReset}
                    disabled={!hasUnsavedChanges || updateMutation.isPending}
                  >
                    <RotateCcw size={16} strokeWidth={2.3} />
                    {t("actions.resetChanges")}
                  </Button>

                  <Button
                    type="button"
                    onClick={handleSave}
                    isLoading={updateMutation.isPending}
                    disabled={!hasUnsavedChanges}
                  >
                    <Save size={16} strokeWidth={2.3} />
                    {t("actions.saveChanges")}
                  </Button>
                </div>
              )}

              {updateMutation.isError && (
                <p className="instructor-course-accordion__error" role="alert">
                  {updateMutation.error instanceof Error
                    ? updateMutation.error.message
                    : "Could not save course changes."}
                </p>
              )}

              {mode === "preview" && previewCourse && (
                <CoursePreview course={previewCourse} />
              )}

              {mode === "edit" && (
                <CourseGeneratorPreviewTabs
                  result={buildPreviewResult(details)}
                  editedCourseJson={editedCourseJson}
                  defaultReasoningModel=""
                  language={language}
                  mode="edit"
                  showEditorTabs
                  onCourseJsonChange={setEditedCourseJson}
                />
              )}
            </>
          )}
        </div>
      )}
    </article>
  );
}
