// frontend/src/features/courseGenerator/components/GeneratedQaReviewTable.tsx

import { useMemo, useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { SendHorizontal } from "lucide-react";
import { useTranslation } from "node_modules/react-i18next";
import { MarkdownView, Button } from "@/components";
import { gradeGeneratedQuestion } from "../api/CourseGeneratorApi";
import type { GeneratedQaReviewItem } from "../types/CourseGenerator";
import { getAnswerText, getQuestionText } from "../utils/CourseGeneratorUtils";

type GeneratedQaReviewTableProps = {
  items: GeneratedQaReviewItem[];
  defaultReasoningModel: string;
  language: string;
};

const pageSizes = [5, 10, 20];

const fallbackGradingModels = ["nemotron-3-super:120b", "deepseek-r1:70b"];

function getAvailableModels(defaultReasoningModel: string) {
  const models = [defaultReasoningModel, ...fallbackGradingModels].filter(
    Boolean,
  );

  return Array.from(new Set(models));
}

export function GeneratedQaReviewTable({
  items,
  defaultReasoningModel,
  language,
}: GeneratedQaReviewTableProps) {
  const { t } = useTranslation("courseGenerator");
  const gradingModels = useMemo(
    () => getAvailableModels(defaultReasoningModel),
    [defaultReasoningModel],
  );

  const fallbackModel = gradingModels[0] ?? "";

  const [pageSize, setPageSize] = useState(5);
  const [page, setPage] = useState(1);
  const [answers, setAnswers] = useState<Record<number, string>>({});
  const [summaries, setSummaries] = useState<Record<number, string>>({});
  const [models, setModels] = useState<Record<number, string>>({});
  const [activeRow, setActiveRow] = useState<number | null>(null);
  const [rowErrors, setRowErrors] = useState<Record<number, string>>({});
  const [consideredMisconceptions, setConsideredMisconceptions] = useState<
    Record<number, string[]>
  >({});

  const totalPages = Math.max(1, Math.ceil(items.length / pageSize));

  const visibleItems = useMemo(() => {
    const start = (page - 1) * pageSize;

    return items.slice(start, start + pageSize).map((item, index) => ({
      item,
      absoluteIndex: start + index,
    }));
  }, [items, page, pageSize]);

  const gradeMutation = useMutation({
    mutationFn: async (index: number) => {
      const reviewItem = items[index];
      const question = reviewItem.question;

      const userAnswer = answers[index]?.trim() ?? "";
      const selectedModel = models[index] ?? fallbackModel;

      if (!userAnswer) {
        throw new Error(t("qaReview.enterAnswer"));
      }

      if (!selectedModel) {
        throw new Error(t("qaReview.noGradingModel"));
      }

      return gradeGeneratedQuestion(
        {
          question: getQuestionText(question),
          reference_answer: getAnswerText(question),
          user_answer: userAnswer,
          reasoning_model_name: selectedModel,

          // Important:
          // all misconceptions from the question's module.
          misconceptions: reviewItem.misconceptions,
        },
        language,
      );
    },

    onMutate: (index) => {
      setActiveRow(index);

      setRowErrors((current) => ({
        ...current,
        [index]: "",
      }));
    },

    onSuccess: (data, index) => {
      setSummaries((current) => ({
        ...current,
        [index]: data.summary || t("qaReview.noSummary"),
      }));

      setConsideredMisconceptions((current) => ({
        ...current,
        [index]: data.misconceptions_considered ?? [],
      }));
    },

    onError: (error, index) => {
      setRowErrors((current) => ({
        ...current,
        [index]:
          error instanceof Error ? error.message : t("qaReview.gradingFailed"),
      }));
    },

    onSettled: () => {
      setActiveRow(null);
    },
  });

  if (items.length === 0) {
    return <p className="course-generator-empty">No Q&A pairs generated.</p>;
  }

  return (
    <section className="generated-qa">
      <div className="generated-qa__toolbar">
        <label>
          <span>{t("qaReview.rowsPerPage")}</span>
          <select
            value={pageSize}
            onChange={(event) => {
              const nextValue = Number(event.currentTarget.value);
              setPageSize(nextValue);
              setPage(1);
            }}
          >
            {pageSizes.map((size) => (
              <option key={size} value={size}>
                {size}
              </option>
            ))}
          </select>
        </label>

        <p>
          {t("qaReview.showing", {
            from: (page - 1) * pageSize + 1,
            to: Math.min(page * pageSize, items.length),
            total: items.length,
          })}
        </p>
      </div>

      <div className="generated-qa__list">
        {visibleItems.map(({ item, absoluteIndex }) => {
          const question = item.question;
          const questionText = getQuestionText(question);
          const answerText = getAnswerText(question);
          const isActive = activeRow === absoluteIndex;
          const selectedModel = models[absoluteIndex] ?? fallbackModel;
          const misconceptions = item.misconceptions;
          const considered = consideredMisconceptions[absoluteIndex] ?? [];

          return (
            <article
              key={`${questionText}-${absoluteIndex}`}
              className="generated-qa-card generated-qa-card--table"
            >
              <div className="generated-qa-card__question">
                <span className="generated-qa-card__number">
                  {absoluteIndex + 1}
                </span>

                <div>
                  <h3>{questionText || t("qaReview.untitledQuestion")}</h3>

                  {item.moduleTitle && (
                    <p className="generated-qa-card__module-context">
                      {t("qaReview.moduleContext", {
                        module: item.moduleTitle,
                        count: misconceptions.length,
                      })}
                    </p>
                  )}

                  <div className="generated-qa-card__llm-answer">
                    <span>{t("qaReview.llmAnswer")}</span>
                    <p>{answerText || t("qaReview.noReferenceAnswer")}</p>
                  </div>
                </div>
              </div>

              <label className="generated-qa-card__answer">
                <span>{t("qaReview.yourTestAnswer")}</span>
                <textarea
                  value={answers[absoluteIndex] ?? ""}
                  onChange={(event) => {
                    const nextValue = event.currentTarget.value;

                    setAnswers((current) => ({
                      ...current,
                      [absoluteIndex]: nextValue,
                    }));
                  }}
                />
              </label>

              <label className="generated-qa-card__model">
                <span>{t("qaReview.gradingModel")}</span>
                <select
                  value={selectedModel}
                  onChange={(event) => {
                    const nextValue = event.currentTarget.value;

                    setModels((current) => ({
                      ...current,
                      [absoluteIndex]: nextValue,
                    }));
                  }}
                >
                  {gradingModels.map((model) => (
                    <option key={model} value={model}>
                      {model}
                    </option>
                  ))}
                </select>
              </label>

              <div className="generated-qa-card__actions">
                <Button
                  type="button"
                  variant="primary"
                  className="course-generator-action-button"
                  disabled={gradeMutation.isPending}
                  isLoading={isActive}
                  onClick={() => gradeMutation.mutate(absoluteIndex)}
                >
                  <SendHorizontal size={16} />
                  {isActive ? t("qaReview.sending") : t("qaReview.send")}
                </Button>
              </div>

              {rowErrors[absoluteIndex] && (
                <p className="generated-qa-card__error" role="alert">
                  {rowErrors[absoluteIndex]}
                </p>
              )}

              {summaries[absoluteIndex] && (
                <details open className="generated-qa-card__summary">
                  <summary>{t("qaReview.gradeSummary")}</summary>
                  <MarkdownView content={summaries[absoluteIndex]} />
                </details>
              )}
              {considered.length > 0 && (
                <details className="generated-qa-card__summary">
                  <summary>
                    {t("qaReview.misconceptionsUsed")} ({considered.length})
                  </summary>

                  <ul>
                    {considered.map((misconception, misconceptionIndex) => (
                      <li
                        key={`${absoluteIndex}-misconception-${misconceptionIndex}`}
                      >
                        {misconception}
                      </li>
                    ))}
                  </ul>
                </details>
              )}
            </article>
          );
        })}
      </div>

      <div className="generated-qa__pagination">
        <Button
          type="button"
          variant="ghost"
          className="course-generator-action-button course-generator-action-button--secondary"
          disabled={page <= 1}
          onClick={() => setPage((current) => Math.max(1, current - 1))}
        >
          {t("qaReview.previousPage")}
        </Button>

        <span>{t("qaReview.pageOf", { page, totalPages })}</span>

        <Button
          type="button"
          variant="ghost"
          className="course-generator-action-button course-generator-action-button--secondary"
          disabled={page >= totalPages}
          onClick={() =>
            setPage((current) => Math.min(totalPages, current + 1))
          }
        >
          {t("qaReview.nextPage")}
        </Button>
      </div>
    </section>
  );
}
