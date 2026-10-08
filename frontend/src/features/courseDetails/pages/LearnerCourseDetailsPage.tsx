// frontend/src/features/courseDetails/pages/LearnerCourseDetailsPage.tsx

import { useEffect, useMemo, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ArrowLeft, UserMinus } from "lucide-react";
import {
  Button,
  ButtonLink,
  ConfirmDialog,
  ErrorState,
  LoadingState,
  MarkdownView,
} from "@/components";
import { usePageMeta } from "@/app/hooks/usePageMeta";
import { useTranslation } from "node_modules/react-i18next";
import {
  CoursePreview,
  createCoursePreviewFromLearnerCourse,
  type CoursePreviewModuleTabKey,
  type CoursePreviewSectionKey,
} from "@/features/coursePreview";
import {
  enrollInLearnerCourse,
  getLearnerCourseDetails,
  saveLearnerCourseProgress,
  submitFinalQuizAttempt,
  submitModuleQuizAttempt,
  unenrollFromLearnerCourse,
} from "../api/LearnerCourseDetailsApi";
import { LockedCourseNotice } from "../components/LockedCourseNotice";
import { CourseModuleSection } from "../components/CourseModuleSection";
import { FinalAssessmentSection } from "../components/FinalAssessmentSection";
import { CourseGradesSection } from "../components/CourseGradesSection";
import type {
  LearnerQuizSubmitResponse,
  NormalizedCourseModule,
  NormalizedCourseQuiz,
  CourseModuleTabKey,
  QuizAnswers,
} from "../types/LearnerCourseDetails";
import {
  normalizeCourseDetails,
  quizAttemptToAnswers,
  quizAttemptToResult,
} from "../utils/CourseDetailsNormalizers";
import { buildLearnerQuizAnswerItems } from "../utils/QuizPayload";
import "./LearnerCourseDetailsPage.css";

function getModuleFromNav(
  navKey: string,
  modules: NormalizedCourseModule[],
): NormalizedCourseModule | null {
  if (!navKey.startsWith("module:")) return null;
  const moduleId = navKey.replace("module:", "");
  return modules.find((module) => module.id === moduleId) ?? null;
}

function renderTextBlock(value: string, courseId?: number) {
  if (!value) {
    return (
      <p className="course-details-page__muted">No content available yet.</p>
    );
  }

  return <MarkdownView content={value} courseId={courseId} />;
}

function toPreviewModuleTab(
  tab: CourseModuleTabKey,
): CoursePreviewModuleTabKey {
  return tab === "further-reading" ? "further-reading" : tab;
}

function toCourseModuleTab(tab: CoursePreviewModuleTabKey): CourseModuleTabKey {
  return tab === "further-reading" ? "further-reading" : tab;
}

export function LearnerCourseDetailsPage() {
  const { t } = useTranslation("courseDetails");
  const params = useParams();
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const courseId = Number(params.courseId);

  const [activeNav, setActiveNav] =
    useState<CoursePreviewSectionKey>("overview");
  const [confirmUnenroll, setConfirmUnenroll] = useState(false);
  const [moduleQuizResults, setModuleQuizResults] = useState<
    Record<string, LearnerQuizSubmitResponse>
  >({});

  const [finalQuizResult, setFinalQuizResult] =
    useState<LearnerQuizSubmitResponse | null>(null);

  const [activeModuleTab, setActiveModuleTab] =
    useState<CourseModuleTabKey>("content");

  const courseQuery = useQuery({
    queryKey: ["learner-course-details", courseId],
    queryFn: () => getLearnerCourseDetails(courseId),
    enabled: Number.isFinite(courseId),
  });

  console.log("Course query data:", courseQuery);

  const course = useMemo(() => {
    return courseQuery.data ? normalizeCourseDetails(courseQuery.data) : null;
  }, [courseQuery.data]);

  const activeModule = useMemo(() => {
    return course ? getModuleFromNav(activeNav, course.modules) : null;
  }, [activeNav, course]);

  const previewCourse = useMemo(() => {
    return course ? createCoursePreviewFromLearnerCourse(course) : null;
  }, [course]);

  const moduleAttempt =
    course && activeModule
      ? course.latestAttempts.module_quizzes[activeModule.id]
      : undefined;

  usePageMeta({
    title: course?.title ?? t("meta.defaultTitle"),
  });

  useEffect(() => {
    const savedNav = courseQuery.data?.progress_snapshot?.current_nav;

    if (savedNav) {
      setActiveNav(savedNav);
    }
  }, [courseQuery.data?.course.course_id]);

  useEffect(() => {
    if (!activeModule) return;

    setActiveModuleTab("content");
  }, [activeModule?.id]);

  const enrollMutation = useMutation({
    mutationFn: () => enrollInLearnerCourse(courseId),
    onSuccess: async () => {
      await queryClient.invalidateQueries({
        queryKey: ["learner-course-details", courseId],
      });
      await queryClient.invalidateQueries({
        queryKey: ["courses", "learner"],
      });
    },
  });

  const unenrollMutation = useMutation({
    mutationFn: () => unenrollFromLearnerCourse(courseId),
    onSuccess: async () => {
      setConfirmUnenroll(false);
      await queryClient.invalidateQueries({
        queryKey: ["courses", "learner"],
      });
      navigate("/courses", { replace: true });
    },
  });

  const progressMutation = useMutation({
    mutationFn: (payload: {
      current_nav: string;
      current_module_id?: string | null;
    }) =>
      saveLearnerCourseProgress(courseId, {
        current_nav: payload.current_nav,
        current_module_id: payload.current_module_id ?? null,
        practice_answers: null,
      }),
  });

  const moduleQuizMutation = useMutation({
    mutationFn: ({
      moduleId,
      quiz,
      answers,
    }: {
      moduleId: string;
      quiz: NormalizedCourseQuiz;
      answers: QuizAnswers;
    }) =>
      submitModuleQuizAttempt(course!.courseId, moduleId, {
        assessment_id: quiz.assessment_id,
        answers: buildLearnerQuizAnswerItems(quiz, answers),
      }),

    onSuccess: async (response, variables) => {
      setModuleQuizResults((current) => ({
        ...current,
        [variables.moduleId]: response,
      }));

      await queryClient.refetchQueries({
        queryKey: ["learner-course-details", courseId],
        type: "active",
      });

      await queryClient.invalidateQueries({
        queryKey: ["learner-statistics"],
      });
    },
  });

  const finalQuizMutation = useMutation({
    mutationFn: ({
      quiz,
      answers,
    }: {
      quiz: NormalizedCourseQuiz;
      answers: QuizAnswers;
    }) =>
      submitFinalQuizAttempt(courseId, {
        assessment_id: quiz.assessment_id,
        answers: buildLearnerQuizAnswerItems(quiz, answers),
      }),
    onSuccess: async (response) => {
      setFinalQuizResult(response);

      await queryClient.refetchQueries({
        queryKey: ["learner-course-details", courseId],
        type: "active",
      });

      await queryClient.invalidateQueries({
        queryKey: ["learner-statistics"],
      });
    },
  });

  function handleNavSelect(nextNav: CoursePreviewSectionKey) {
    setActiveNav(nextNav);

    const module = getModuleFromNav(nextNav, course?.modules ?? []);

    if (module) {
      setActiveModuleTab("content");
    }

    if (course?.isEnrolled) {
      progressMutation.mutate({
        current_nav: nextNav,
        current_module_id: module?.id ?? null,
      });
    }
  }

  if (!Number.isFinite(courseId)) {
    return (
      <ErrorState
        title="Invalid course"
        description="The course ID is missing or invalid."
        actionLabel="Back to My Courses"
        onAction={() => navigate("/courses")}
      />
    );
  }

  if (courseQuery.isLoading) {
    return <LoadingState description={t("messages.loading")} />;
  }

  if (courseQuery.error || !course) {
    return (
      <ErrorState
        title="Could not load course"
        description={
          courseQuery.error instanceof Error
            ? courseQuery.error.message
            : "The course details could not be loaded right now."
        }
        actionLabel="Retry"
        onAction={() => void courseQuery.refetch()}
      />
    );
  }

  return (
    <section className="course-details-page">
      <div className="course-details-page__topbar">
        <ButtonLink
          to="/courses"
          variant="secondary"
          className="course-details-page__topbar-action"
        >
          <ArrowLeft size={16} strokeWidth={2.3} aria-hidden="true" />
          <span>{t("actions.backToCourses")}</span>
        </ButtonLink>

        {course.isEnrolled && (
          <Button
            type="button"
            variant="danger"
            className="course-details-page__topbar-action"
            onClick={() => setConfirmUnenroll(true)}
            disabled={unenrollMutation.isPending}
          >
            <UserMinus size={16} strokeWidth={2.3} aria-hidden="true" />
            <span>{t("actions.unenroll")}</span>
          </Button>
        )}
      </div>

      {previewCourse && (
        <CoursePreview
          course={previewCourse}
          activeSection={activeNav}
          activeModuleTab={toPreviewModuleTab(activeModuleTab)}
          onSectionChange={handleNavSelect}
          onModuleTabChange={(tab) =>
            setActiveModuleTab(toCourseModuleTab(tab))
          }
          notice={
            !course.isEnrolled ? (
              <LockedCourseNotice
                isWorking={enrollMutation.isPending}
                onEnroll={() => enrollMutation.mutate()}
              />
            ) : null
          }
          renderers={{
            overview: () => renderTextBlock(course.overview, course.courseId),

            courseInfo: () => (
              <section>
                <div className="course-details-page__info-grid">
                  <article>
                    <span>{t("infoGrid.difficulty")}: </span>
                    <strong>{course.difficulty}</strong>
                  </article>

                  <article>
                    <span>{t("infoGrid.duration")}: </span>
                    <strong>{course.duration}</strong>
                  </article>

                  <article>
                    <span>{t("infoGrid.modules")}: </span>
                    <strong>{course.modules.length}</strong>
                  </article>

                  <article>
                    <span>{t("infoGrid.courseProgress")}: </span>
                    <strong>{course.progressPercent}%</strong>
                  </article>
                </div>

                {course.skills.length > 0 && (
                  <>
                    <h3>{t("sections.skillsAndTags")}</h3>
                    <div className="course-details-page__chips">
                      {course.skills.map((skill) => (
                        <span key={skill}>{skill}</span>
                      ))}
                    </div>
                  </>
                )}

                <h3>{t("sections.prerequisites")}</h3>
                {course.prerequisites.length > 0 ? (
                  <ul>
                    {course.prerequisites.map((item) => (
                      <li key={item}>{item}</li>
                    ))}
                  </ul>
                ) : (
                  <p className="course-details-page__info">
                    {t("messages.noFormalPrerequisites")}
                  </p>
                )}

                <h3>{t("sections.instructors")}</h3>
                {course.instructors.length > 0 ? (
                  <div className="course-details-page__resources">
                    {course.instructors.map((instructor) => (
                      <article key={instructor.name}>
                        <strong>{instructor.name}</strong>
                        {instructor.bio && <p>{instructor.bio}</p>}
                      </article>
                    ))}
                  </div>
                ) : (
                  <p className="course-details-page__muted">
                    {t("messages.noContent")}
                  </p>
                )}

                {course.grading.notes.length > 0 && (
                  <>
                    <h3>{t("gradingPolicy")}</h3>
                    <ul>
                      {course.grading.notes.map((note) => (
                        <li key={note}>{note}</li>
                      ))}
                    </ul>
                  </>
                )}
              </section>
            ),

            module: () =>
              activeModule ? (
                <CourseModuleSection
                  courseId={course.courseId}
                  module={activeModule}
                  activeTab={activeModuleTab}
                  quizResult={moduleQuizResults[activeModule.id] ?? null}
                  persistedQuizAnswers={quizAttemptToAnswers(moduleAttempt)}
                  persistedQuizResult={quizAttemptToResult(moduleAttempt)}
                  isQuizSubmitting={moduleQuizMutation.isPending}
                  practiceAnswers={
                    courseQuery.data?.progress_snapshot?.practice_answers ?? {}
                  }
                  onTabChange={setActiveModuleTab}
                  onQuizSubmit={(quiz, answers) =>
                    moduleQuizMutation.mutate({
                      moduleId: activeModule.id,
                      quiz,
                      answers,
                    })
                  }
                />
              ) : null,

            finalAssessment: () =>
              course.finalQuiz ? (
                <FinalAssessmentSection
                  quiz={course.finalQuiz}
                  isEligible={course.finalAssessmentStatus.isEligible}
                  requiredModules={course.finalAssessmentStatus.requiredModules}
                  result={finalQuizResult}
                  persistedAnswers={quizAttemptToAnswers(
                    course.latestAttempts.final_quiz,
                  )}
                  persistedResult={quizAttemptToResult(
                    course.latestAttempts.final_quiz,
                  )}
                  isSubmitting={finalQuizMutation.isPending}
                  onSubmit={(quiz, answers) =>
                    finalQuizMutation.mutate({
                      quiz,
                      answers,
                    })
                  }
                />
              ) : null,

            grades: () => <CourseGradesSection course={course} />,
          }}
        />
      )}

      <ConfirmDialog
        isOpen={confirmUnenroll}
        title={t("confirm.unenrollTitle")}
        description={t("confirm.unenrollDescription", { title: course.title })}
        confirmLabel={t("confirm.yesUnenroll")}
        cancelLabel={t("confirm.cancel")}
        workingLabel={t("confirm.working")}
        isConfirming={unenrollMutation.isPending}
        onCancel={() => setConfirmUnenroll(false)}
        onConfirm={() => unenrollMutation.mutate()}
      />
    </section>
  );
}
