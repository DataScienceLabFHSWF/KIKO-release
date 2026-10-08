// frontend/src/features/courseDetails/components/FinalAssessmentSection.tsx

import { AlertTriangle, FileText } from "lucide-react";
import { useTranslation } from "node_modules/react-i18next";
import { QuizAssessmentPanel } from "./QuizAssessmentPanel";
import type {
  LearnerQuizSubmitResponse,
  NormalizedCourseQuiz,
  QuizAnswers,
} from "../types/LearnerCourseDetails";
import "./FinalAssessmentSection.css";

type FinalAssessmentSectionProps = {
  quiz: NormalizedCourseQuiz;
  isEligible: boolean;
  requiredModules: string[];
  result: LearnerQuizSubmitResponse | null;
  persistedAnswers?: QuizAnswers;
  persistedResult?: LearnerQuizSubmitResponse | null;
  isSubmitting: boolean;
  onSubmit: (quiz: NormalizedCourseQuiz, answers: QuizAnswers) => void;
};

export function FinalAssessmentSection({
  quiz,
  isEligible,
  requiredModules,
  result,
  persistedAnswers,
  persistedResult,
  isSubmitting,
  onSubmit,
}: FinalAssessmentSectionProps) {
  const { t } = useTranslation("courseDetails");

  return (
    <section className="final-assessment-section">
      <div className="course-details-page__section-title">
        <FileText size={28} strokeWidth={2.2} />
        <h2>{t("sections.finalAssessment")}</h2>
      </div>

      {!isEligible && (
        <div className="final-assessment-section__locked" role="status">
          <AlertTriangle size={18} strokeWidth={2.2} />

          <div>
            <strong>{t("finalAssessment.lockedTitle")}</strong>
            <p>
              {t("finalAssessment.lockedDescription", {
                modules: requiredModules.length
                  ? requiredModules.join(", ")
                  : t("finalAssessment.requiredModulesFallback"),
              })}
            </p>
          </div>
        </div>
      )}

      {isEligible && (
        <QuizAssessmentPanel
          quiz={quiz}
          result={result}
          initialAnswers={persistedAnswers}
          initialResult={persistedResult}
          isSubmitting={isSubmitting}
          onSubmit={(answers) => onSubmit(quiz, answers)}
        />
      )}
    </section>
  );
}
