// frontend/src/features/knowledgeAssessment/components/KnowledgeAssessmentResultPanel.tsx

import { BookOpenCheck, GraduationCap, Route, Sparkles } from "lucide-react";
import { Link } from "react-router-dom";
import { useTranslation } from "node_modules/react-i18next";
import { MarkdownView } from "@/components";
import type { AssessmentResult } from "../types/KnowledgeAssessment";

type KnowledgeAssessmentResultPanelProps = {
  result: AssessmentResult;
};

function safeText(value: unknown): string {
  return typeof value === "string" && value.trim().length > 0 ? value : "";
}

export function KnowledgeAssessmentResultPanel({
  result,
}: KnowledgeAssessmentResultPanelProps) {
  const { t } = useTranslation("knowledgeAssessment");

  const recommendedCourses = Array.isArray(result.recommended_courses)
    ? result.recommended_courses
    : [];

  return (
    <section className="knowledge-result" aria-live="polite">
      <div className="knowledge-result__header">
        <Sparkles size={26} strokeWidth={2.2} />
        <div>
          <h2>{t("result.title")}</h2>
          <p>{t("result.subtitle")}</p>
        </div>
      </div>

      <div className="knowledge-result__grid">
        <article className="knowledge-result__card">
          <BookOpenCheck size={22} strokeWidth={2.2} />
          <h3>{t("result.knowledgeAssessment")}</h3>
          <MarkdownView
            content={
              safeText(result.knowledge_assessment) ||
              t("result.noGeneratedContent")
            }
          />
        </article>

        <article className="knowledge-result__card">
          <Route size={22} strokeWidth={2.2} />
          <h3>{t("result.learningPath")}</h3>
          <MarkdownView
            content={
              safeText(result.learning_path) || t("result.noGeneratedContent")
            }
          />
        </article>

        <article className="knowledge-result__card">
          <GraduationCap size={22} strokeWidth={2.2} />
          <h3>{t("result.nextStep")}</h3>
          <MarkdownView
            content={
              safeText(result.learning_step) || t("result.noGeneratedContent")
            }
          />
        </article>
      </div>

      <div className="knowledge-result__recommendations">
        <h3>{t("result.recommendedCourses")}</h3>

        {recommendedCourses.length === 0 ? (
          <p>{t("result.noRecommendations")}</p>
        ) : (
          <div className="knowledge-result__course-list">
            {result.recommended_courses.map((course, index) => (
              <article
                key={course.course_id ?? `${course.title}-${index}`}
                className="knowledge-result__course"
              >
                <strong>{course.title ?? t("result.untitledCourse")}</strong>

                {course.summary && <p>{course.summary}</p>}

                {course.reason && (
                  <small>{t("result.reason", { reason: course.reason })}</small>
                )}
              </article>
            ))}
          </div>
        )}

        <Link className="knowledge-result__courses-link" to="/courses">
          {t("result.goToCourses")}
        </Link>
      </div>
    </section>
  );
}
