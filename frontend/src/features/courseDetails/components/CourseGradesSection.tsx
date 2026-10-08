// frontend/src/features/courseDetails/components/CourseGradesSection.tsx

import { CheckCircle2 } from "lucide-react";
import { useTranslation } from "node_modules/react-i18next";
import type { NormalizedCourseDetails } from "../types/LearnerCourseDetails";
import "./CourseGradesSection.css";

type GradeStatus = "passed" | "failed" | "not_attempted";

type CourseGradeRow = {
  id: string;
  title: string;
  weight: number;
  status: GradeStatus;
  percent: number | null;
  germanGrade: number | string | null;
};

type CourseGradesSectionProps = {
  course: NormalizedCourseDetails;
};

function getModuleStatusLabel(row: CourseGradeRow) {
  const { t } = useTranslation("courseDetails");
  if (row.status === "not_attempted") return t("gradesSummary.Not attempted");
  if (row.status === "passed") return t("gradesSummary.Passed");
  return t("gradesSummary.Failed");
}

function getStatusClass(row: CourseGradeRow) {
  return `course-grade-row__status course-grade-row__status--${row.status}`;
}

export function CourseGradesSection({ course }: CourseGradesSectionProps) {
  const { t } = useTranslation("courseDetails");

  const moduleTotalWeight = Number(
    course.grading.assessmentWeights.module_quizzes ?? 60,
  );

  const moduleWeight =
    course.modules.length > 0 ? moduleTotalWeight / course.modules.length : 0;

  const finalWeight = Number(course.grading.assessmentWeights.final_quiz ?? 40);

  const rows: CourseGradeRow[] = [
    ...course.modules.map((module) => {
      const attempt = course.latestAttempts.module_quizzes[module.id];

      return {
        id: module.id,
        title: module.title,
        weight: moduleWeight,
        status: !attempt
          ? "not_attempted"
          : attempt.passed
            ? "passed"
            : "failed",
        percent: attempt?.percent ?? null,
        germanGrade: attempt?.german_grade ?? null,
      };
    }),

    ...(course.finalQuiz
      ? [
          {
            id: "final-quiz",
            title: course.finalQuiz.title,
            weight: finalWeight,
            status: !course.latestAttempts.final_quiz
              ? "not_attempted"
              : course.latestAttempts.final_quiz.passed
                ? "passed"
                : "failed",
            percent: course.latestAttempts.final_quiz?.percent ?? null,
            germanGrade: course.latestAttempts.final_quiz?.german_grade ?? null,
          } satisfies CourseGradeRow,
        ]
      : []),
  ];

  return (
    <section className="course-grades-section">
      <div className="course-details-page__section-title">
        <CheckCircle2 size={28} strokeWidth={2.2} />
        <h2>{t("sections.grades")}</h2>
      </div>

      <div className="course-grades-section__summary">
        <strong>{course.finalAssessmentStatus.weightedPercent ?? 0}%</strong>

        {course.finalAssessmentStatus.germanGrade && (
          <span>
            {t("quiz.germanGrade", {
              grade: course.finalAssessmentStatus.germanGrade,
            })}
          </span>
        )}
      </div>

      {course.finalAssessmentStatus.completed && (
        <div className="course-grades-section__success" role="status">
          {t("grades.requirementMet")}
        </div>
      )}

      {!course.finalAssessmentStatus.completed &&
        course.finalAssessmentStatus.weightedPercent !== null &&
        course.finalAssessmentStatus.weightedPercent !== undefined &&
        course.finalAssessmentStatus.weightedPercent <
          course.grading.passPercent && (
          <div className="course-grades-section__warning" role="status">
            {t("grades.requirementNotMet", {
              threshold: course.grading.passPercent,
            })}
          </div>
        )}

      <div className="course-grades-section__rows">
        {rows.map((row) => (
          <article key={row.id} className="course-grade-row">
            <strong>{row.title}</strong>

            <span>{Math.round(row.weight)}%</span>

            <span className={getStatusClass(row)}>
              {getModuleStatusLabel(row)}
            </span>

            <span>{row.germanGrade ?? "—"}</span>
          </article>
        ))}
      </div>
    </section>
  );
}
