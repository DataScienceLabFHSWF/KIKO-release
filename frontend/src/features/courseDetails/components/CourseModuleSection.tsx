// frontend/src/features/courseDetails/components/CourseModuleSection.tsx

import { BookOpen } from "lucide-react";
import { useTranslation } from "node_modules/react-i18next";
import { MarkdownView } from "@/components";
import { CourseModuleTabs } from "./CourseModuleTabs";
import { CoursePracticePanel } from "./CoursePracticePanel";
import { QuizAssessmentPanel } from "./QuizAssessmentPanel";
import type {
  LearnerQuizSubmitResponse,
  NormalizedCourseModule,
  NormalizedCourseQuiz,
  CourseModuleTabKey,
  QuizAnswers,
} from "../types/LearnerCourseDetails";
import "./CourseModuleSection.css";

type CourseModuleSectionProps = {
  courseId: number;
  module: NormalizedCourseModule;
  activeTab: CourseModuleTabKey;
  quizResult: LearnerQuizSubmitResponse | null;
  persistedQuizAnswers?: QuizAnswers;
  persistedQuizResult?: LearnerQuizSubmitResponse | null;
  isQuizSubmitting: boolean;
  practiceAnswers?: Record<string, unknown> | null;
  onTabChange: (tab: CourseModuleTabKey) => void;
  onQuizSubmit: (quiz: NormalizedCourseQuiz, answers: QuizAnswers) => void;
};

function EmptyMessage({ children }: { children: string }) {
  return <p className="course-module-section__empty">{children}</p>;
}

export function CourseModuleSection({
  courseId,
  module,
  activeTab,
  quizResult,
  persistedQuizAnswers,
  persistedQuizResult,
  isQuizSubmitting,
  practiceAnswers,
  onTabChange,
  onQuizSubmit,
}: CourseModuleSectionProps) {
  const { t } = useTranslation("courseDetails");

  return (
    <section className="course-module-section">
      <div className="course-details-page__section-title">
        <BookOpen size={28} strokeWidth={2.2} />
        <h2>{module.title}</h2>
      </div>

      <CourseModuleTabs activeTab={activeTab} onChange={onTabChange} />

      {activeTab === "content" && (
        <>
          {module.content ? (
            <MarkdownView content={module.content} courseId={courseId} />
          ) : (
            <EmptyMessage>{t("messages.noContent")}</EmptyMessage>
          )}
        </>
      )}

      {activeTab === "practice" && (
        <CoursePracticePanel
          courseId={courseId}
          moduleId={module.id}
          currentNav={`module:${module.id}`}
          questions={module.practiceQuestions}
          moduleMisconceptions={module.misconceptions}
          initialAnswers={practiceAnswers}
        />
      )}

      {activeTab === "quiz" && (
        <>
          {!module.quiz ? (
            <EmptyMessage>{t("messages.noModuleQuiz")}</EmptyMessage>
          ) : (
            <QuizAssessmentPanel
              quiz={module.quiz}
              result={quizResult}
              initialAnswers={persistedQuizAnswers}
              initialResult={persistedQuizResult}
              isSubmitting={isQuizSubmitting}
              onSubmit={(answers) => onQuizSubmit(module.quiz!, answers)}
            />
          )}
        </>
      )}

      {activeTab === "further-reading" && (
        <>
          {module.furtherReading.length === 0 ? (
            <EmptyMessage>{t("messages.noFurtherReading")}</EmptyMessage>
          ) : (
            <div className="course-details-page__resources">
              {module.furtherReading.map((resource) => (
                <article key={`${resource.title}-${resource.url}`}>
                  <strong>{resource.title}</strong>

                  {resource.type && <span>{resource.type}</span>}

                  {resource.url && (
                    <a href={resource.url} target="_blank" rel="noreferrer">
                      {resource.url}
                    </a>
                  )}
                </article>
              ))}
            </div>
          )}
        </>
      )}

      {activeTab === "misconceptions" && (
        <>
          {module.misconceptions.length === 0 ? (
            <EmptyMessage>{t("messages.noMisconceptions")}</EmptyMessage>
          ) : (
            <div className="course-module-section__misconceptions">
              {module.misconceptions.map((item) => (
                <article key={item}>
                  <p>{item}</p>
                </article>
              ))}
            </div>
          )}
        </>
      )}
    </section>
  );
}
