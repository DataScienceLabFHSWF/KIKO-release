// frontend/src/features/courses/pages/MyCoursesPage.tsx

import {
  BookOpen,
  CheckCircle2,
  Eye,
  GraduationCap,
  Plus,
  Sparkles,
  UserMinus,
  UserPlus,
  XCircle,
} from "lucide-react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useTranslation } from "node_modules/react-i18next";
import { useState } from "react";
import { useAuth } from "@/app/providers/AuthProvider";
import { usePageMeta } from "@/app/hooks/usePageMeta";
import {
  ConfirmDialog,
  EmptyState,
  ErrorState,
  LoadingState,
  PageHeader,
  ButtonLink,
} from "@/components";

import {
  deleteInstructorCourse,
  dismissRecommendedCourse,
  enrollInCourse,
  getInstructorCourses,
  getLearnerAvailableCourses,
  getLearnerEnrolledCourses,
  getLearnerRecommendedCourses,
  unenrollFromCourse,
  courseQueryKeys,
} from "../api/CoursesApi";
import { CourseCard } from "../components/CourseCard";
import { CourseSection } from "../components/CourseSection";
import { InstructorCourseAccordion } from "../components/InstructorCourseAccordion";
import type {
  InstructorCourse,
  LearnerAvailableCourse,
  LearnerEnrolledCourse,
} from "../types/Courses";
import "./MyCoursesPage.css";

type ConfirmState =
  | { type: "enroll"; course: LearnerAvailableCourse }
  | { type: "unenroll"; course: LearnerEnrolledCourse }
  | { type: "dismiss"; course: LearnerAvailableCourse }
  | { type: "delete"; course: InstructorCourse }
  | null;

function normalizeList<T>(value: unknown): T[] {
  return Array.isArray(value) ? value : [];
}

function getCourseStatusLabel(
  t: (key: string) => string,
  course: LearnerEnrolledCourse,
) {
  if (course.completed) return t("status.completed");
  if (course.status === "eligible_for_final_quiz") {
    return t("status.eligibleFinalQuiz");
  }
  return t("status.inProgress");
}

export function MyCoursesPage() {
  const { t } = useTranslation("courses");
  const { user } = useAuth();
  const queryClient = useQueryClient();

  const [confirmState, setConfirmState] = useState<ConfirmState>(null);

  const isLearner = user?.role === "Learner";
  const isInstructor = user?.role === "Instructor";

  usePageMeta({
    title: t("metaTitle"),
  });

  const enrolledQuery = useQuery({
    queryKey: courseQueryKeys.learnerEnrolled,
    queryFn: getLearnerEnrolledCourses,
    enabled: isLearner,
  });

  const recommendedQuery = useQuery({
    queryKey: courseQueryKeys.learnerRecommended,
    queryFn: getLearnerRecommendedCourses,
    enabled: isLearner,
  });

  const availableQuery = useQuery({
    queryKey: courseQueryKeys.learnerAvailable,
    queryFn: getLearnerAvailableCourses,
    enabled: isLearner,
  });

  const instructorQuery = useQuery({
    queryKey: courseQueryKeys.instructor,
    queryFn: getInstructorCourses,
    enabled: isInstructor,
  });

  const enrollMutation = useMutation({
    mutationFn: enrollInCourse,
    onSuccess: async () => {
      setConfirmState(null);
      await queryClient.invalidateQueries({
        queryKey: courseQueryKeys.learner,
      });
    },
  });

  const unenrollMutation = useMutation({
    mutationFn: unenrollFromCourse,
    onSuccess: async () => {
      setConfirmState(null);
      await queryClient.invalidateQueries({
        queryKey: courseQueryKeys.learner,
      });
    },
  });

  const dismissMutation = useMutation({
    mutationFn: dismissRecommendedCourse,
    onSuccess: async () => {
      setConfirmState(null);
      await queryClient.invalidateQueries({
        queryKey: courseQueryKeys.learnerRecommended,
      });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: deleteInstructorCourse,
    onSuccess: async () => {
      setConfirmState(null);
      await queryClient.invalidateQueries({
        queryKey: courseQueryKeys.instructor,
      });
    },
  });

  const isLoading =
    enrolledQuery.isLoading ||
    recommendedQuery.isLoading ||
    availableQuery.isLoading ||
    instructorQuery.isLoading;

  const error =
    enrolledQuery.error ||
    recommendedQuery.error ||
    availableQuery.error ||
    instructorQuery.error;

  if (isLoading) {
    return <LoadingState description={t("messages.loading")} />;
  }

  if (error) {
    return (
      <ErrorState
        title={t("messages.errorTitle")}
        description={
          error instanceof Error
            ? error.message
            : t("messages.errorDescription")
        }
        actionLabel={t("actions.retry")}
        onAction={() => {
          void enrolledQuery.refetch();
          void recommendedQuery.refetch();
          void availableQuery.refetch();
          void instructorQuery.refetch();
        }}
      />
    );
  }

  const enrolledCourses = normalizeList<LearnerEnrolledCourse>(
    enrolledQuery.data,
  );

  const recommendedCourses = normalizeList<LearnerAvailableCourse>(
    recommendedQuery.data,
  );

  const availableCourses = normalizeList<LearnerAvailableCourse>(
    availableQuery.data,
  );

  const coursesToRecommend =
    recommendedCourses.length > 0 ? recommendedCourses : availableCourses;

  const instructorCourses = normalizeList<InstructorCourse>(
    instructorQuery.data,
  );

  return (
    <section className="my-courses-page">
      <PageHeader
        icon={<BookOpen size={30} strokeWidth={2.3} />}
        title={t("title")}
        subtitle={isInstructor ? t("subtitleInstructor") : t("subtitleLearner")}
        action={
          isInstructor ? (
            <ButtonLink
              to="/course-generator"
              variant="primary"
              className="my-courses-page__create"
            >
              <Plus size={17} strokeWidth={2.4} aria-hidden="true" />
              <span>{t("actions.createCourse")}</span>
            </ButtonLink>
          ) : null
        }
      />

      {isLearner && (
        <>
          <CourseSection
            icon={<GraduationCap size={24} strokeWidth={2.2} />}
            title={t("sections.enrolled")}
            description={t("sections.enrolledDescription")}
          >
            {enrolledCourses.length === 0 ? (
              <EmptyState
                title={t("empty.noEnrolledTitle")}
                description={t("empty.noEnrolledDescription")}
              />
            ) : (
              enrolledCourses.map((course) => (
                <CourseCard
                  key={course.course_id}
                  title={course.title}
                  summary={course.summary}
                  courseId={course.course_id}
                  progressPercent={course.completion_percent ?? 0}
                  statusLabel={getCourseStatusLabel(t, course)}
                  actions={[
                    {
                      label: t("actions.view"),
                      to: `/courses/${course.course_id}`,
                      icon: (
                        <Eye size={16} strokeWidth={2.3} aria-hidden="true" />
                      ),
                      variant: "primary",
                    },
                    course.completed
                      ? {
                          label: t("status.completed"),
                          icon: (
                            <CheckCircle2
                              size={16}
                              strokeWidth={2.3}
                              aria-hidden="true"
                            />
                          ),
                          disabled: true,
                          variant: "success",
                        }
                      : {
                          label: t("actions.unenroll"),
                          icon: (
                            <UserMinus
                              size={16}
                              strokeWidth={2.3}
                              aria-hidden="true"
                            />
                          ),
                          variant: "danger",
                          disabled:
                            unenrollMutation.isPending &&
                            confirmState?.type === "unenroll" &&
                            confirmState.course.course_id === course.course_id,
                          onClick: () =>
                            setConfirmState({ type: "unenroll", course }),
                        },
                  ]}
                />
              ))
            )}
          </CourseSection>

          <CourseSection
            icon={<Sparkles size={24} strokeWidth={2.2} />}
            title={t("sections.recommended")}
            description={
              recommendedCourses.length > 0
                ? t("sections.recommendedDescriptionPersonalized")
                : t("sections.recommendedDescriptionFallback")
            }
          >
            {coursesToRecommend.length === 0 ? (
              <EmptyState
                title={t("empty.noRecommendedTitle")}
                description={t("empty.noRecommendedDescription")}
              />
            ) : (
              coursesToRecommend.map((course) => {
                const isRecommendation = recommendedCourses.length > 0;

                return (
                  <CourseCard
                    key={course.course_id}
                    title={course.title}
                    summary={course.summary}
                    courseId={course.course_id}
                    reason={isRecommendation ? course.reason : undefined}
                    actions={[
                      {
                        label: t("actions.view"),
                        to: `/courses/${course.course_id}`,
                        icon: (
                          <Eye size={16} strokeWidth={2.3} aria-hidden="true" />
                        ),
                        variant: "primary",
                      },
                      {
                        label: t("actions.enroll"),
                        icon: (
                          <UserPlus
                            size={16}
                            strokeWidth={2.3}
                            aria-hidden="true"
                          />
                        ),
                        variant: "primary",
                        disabled:
                          enrollMutation.isPending &&
                          confirmState?.type === "enroll" &&
                          confirmState.course.course_id === course.course_id,
                        onClick: () =>
                          setConfirmState({ type: "enroll", course }),
                      },
                      ...(isRecommendation
                        ? [
                            {
                              label: t("actions.dismiss"),
                              icon: (
                                <XCircle
                                  size={16}
                                  strokeWidth={2.3}
                                  aria-hidden="true"
                                />
                              ),
                              variant: "secondary" as const,
                              disabled:
                                dismissMutation.isPending &&
                                confirmState?.type === "dismiss" &&
                                confirmState.course.course_id ===
                                  course.course_id,
                              onClick: () =>
                                setConfirmState({ type: "dismiss", course }),
                            },
                          ]
                        : []),
                    ]}
                  />
                );
              })
            )}
          </CourseSection>
        </>
      )}

      {isInstructor && (
        <CourseSection
          icon={<BookOpen size={28} strokeWidth={2.1} />}
          title={t("sections.instructorCourses")}
          description={t("sections.instructorCoursesDescription")}
        >
          {instructorQuery.isLoading && (
            <LoadingState description={t("status.loading")} />
          )}

          {instructorQuery.isError && (
            <ErrorState
              title={t("errors.loadTitle")}
              description={
                instructorQuery.error instanceof Error
                  ? instructorQuery.error.message
                  : t("errors.loadDescription")
              }
              actionLabel={t("actions.retry")}
              onAction={() => void instructorQuery.refetch()}
            />
          )}

          {!instructorQuery.isLoading &&
            !instructorQuery.isError &&
            normalizeList<InstructorCourse>(instructorQuery.data).length ===
              0 && (
              <EmptyState
                title={t("empty.instructorTitle")}
                description={t("empty.instructorDescription")}
              />
            )}

          <div className="my-courses-page__instructor-list">
            {normalizeList<InstructorCourse>(instructorQuery.data).map(
              (course) => (
                <InstructorCourseAccordion
                  key={course.course_id}
                  course={course}
                  isDeleting={
                    deleteMutation.isPending &&
                    confirmState?.type === "delete" &&
                    confirmState.course.course_id === course.course_id
                  }
                  onDelete={(selectedCourse) =>
                    setConfirmState({ type: "delete", course: selectedCourse })
                  }
                />
              ),
            )}
          </div>
        </CourseSection>
      )}

      <ConfirmDialog
        isOpen={confirmState?.type === "enroll"}
        title={t("confirm.enrollTitle")}
        description={t("confirm.enrollDescription", {
          title:
            confirmState?.type === "enroll" ? confirmState.course.title : "",
        })}
        confirmLabel={t("confirm.yesEnroll")}
        cancelLabel={t("confirm.cancel")}
        workingLabel={t("confirm.working")}
        isConfirming={enrollMutation.isPending}
        onCancel={() => setConfirmState(null)}
        onConfirm={() => {
          if (confirmState?.type === "enroll") {
            enrollMutation.mutate(confirmState.course.course_id);
          }
        }}
      />

      <ConfirmDialog
        isOpen={confirmState?.type === "unenroll"}
        title={t("confirm.unenrollTitle")}
        description={t("confirm.unenrollDescription", {
          title:
            confirmState?.type === "unenroll" ? confirmState.course.title : "",
        })}
        confirmLabel={t("confirm.yesUnenroll")}
        cancelLabel={t("confirm.cancel")}
        workingLabel={t("confirm.working")}
        isConfirming={unenrollMutation.isPending}
        onCancel={() => setConfirmState(null)}
        onConfirm={() => {
          if (confirmState?.type === "unenroll") {
            unenrollMutation.mutate(confirmState.course.course_id);
          }
        }}
      />

      <ConfirmDialog
        isOpen={confirmState?.type === "dismiss"}
        title={t("confirm.dismissTitle")}
        description={t("confirm.dismissDescription", {
          title:
            confirmState?.type === "dismiss" ? confirmState.course.title : "",
        })}
        confirmLabel={t("confirm.yesDismiss")}
        cancelLabel={t("confirm.cancel")}
        workingLabel={t("confirm.working")}
        isConfirming={dismissMutation.isPending}
        onCancel={() => setConfirmState(null)}
        onConfirm={() => {
          if (confirmState?.type === "dismiss") {
            dismissMutation.mutate(confirmState.course.course_id);
          }
        }}
      />

      <ConfirmDialog
        isOpen={confirmState?.type === "delete"}
        title={t("confirm.deleteTitle")}
        description={t("confirm.deleteDescription", {
          title:
            confirmState?.type === "delete" ? confirmState.course.title : "",
        })}
        confirmLabel={t("confirm.yesDelete")}
        cancelLabel={t("confirm.cancel")}
        workingLabel={t("confirm.working")}
        isConfirming={deleteMutation.isPending}
        onCancel={() => setConfirmState(null)}
        onConfirm={() => {
          if (confirmState?.type === "delete") {
            deleteMutation.mutate(confirmState.course.course_id);
          }
        }}
      />
    </section>
  );
}
