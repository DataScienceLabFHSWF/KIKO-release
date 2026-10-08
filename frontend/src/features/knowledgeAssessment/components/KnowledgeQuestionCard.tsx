// frontend/src/features/knowledgeAssessment/components/KnowledgeQuestionCard.tsx

import { CircleHelp } from "lucide-react";
import { useTranslation } from "node_modules/react-i18next";
import type { AssessmentQuestion } from "../types/KnowledgeAssessment";

type KnowledgeQuestionCardProps = {
  question: AssessmentQuestion;
  value: string;
  index: number;
  disabled?: boolean;
  onChange: (questionId: number, value: string) => void;
};

export function KnowledgeQuestionCard({
  question,
  value,
  index,
  disabled = false,
  onChange,
}: KnowledgeQuestionCardProps) {
  const { t } = useTranslation("knowledgeAssessment");

  return (
    <article className="knowledge-question-card">
      <div className="knowledge-question-card__header">
        <div>
          <p className="knowledge-question-card__topic">
            {question.topic || t("question.fallbackTopic")}
          </p>

          <h2>
            {t("question.number", { number: index + 1 })} {question.question}
            <span aria-hidden="true"> *</span>
          </h2>
        </div>
      </div>

      <label className="knowledge-question-card__field">
        <span>{t("question.answerLabel")}</span>

        <textarea
          value={value}
          disabled={disabled}
          placeholder={t("question.placeholder")}
          onChange={(event) =>
            onChange(question.question_id, event.currentTarget.value)
          }
        />
      </label>
    </article>
  );
}
