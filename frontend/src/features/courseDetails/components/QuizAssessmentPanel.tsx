// frontend/src/features/courseDetails/components/QuizAssessmentPanel.tsx

import { useEffect, useMemo, useState } from "react";
import {
  BadgeCheck,
  ClipboardCheck,
  SendHorizontal,
  XCircle,
} from "lucide-react";
import { useTranslation } from "node_modules/react-i18next";
import { Button } from "@/components";
import { QuizOptionGroup } from "./QuizOptionGroup";
import type {
  LearnerQuizSubmitResponse,
  NormalizedCourseQuiz,
  QuizAnswers,
  QuizAnswerValue,
} from "../types/LearnerCourseDetails";
import "./QuizAssessmentPanel.css";

type QuizAssessmentPanelProps = {
  quiz: NormalizedCourseQuiz;
  result: LearnerQuizSubmitResponse | null;
  initialAnswers?: QuizAnswers;
  initialResult?: LearnerQuizSubmitResponse | null;
  isSubmitting: boolean;
  onSubmit: (answers: QuizAnswers) => void;
};

function hasAnswer(value: QuizAnswerValue | undefined) {
  if (Array.isArray(value)) {
    return value.length > 0;
  }

  return (
    value !== undefined && value !== null && String(value).trim().length > 0
  );
}

function getScore(result: LearnerQuizSubmitResponse) {
  return result.score ?? result.result?.score ?? 0;
}

function getMaxScore(result: LearnerQuizSubmitResponse) {
  return result.max_score ?? result.result?.total_points ?? 0;
}

function getPercent(result: LearnerQuizSubmitResponse) {
  return result.percent ?? result.result?.percent ?? 0;
}

function getPassed(result: LearnerQuizSubmitResponse) {
  return result.passed ?? result.result?.passed ?? false;
}

function getGermanGrade(result: LearnerQuizSubmitResponse) {
  return result.german_grade ?? result.result?.german_grade ?? null;
}

function getFeedbackItems(result: LearnerQuizSubmitResponse) {
  return result.graded_answers ?? result.result?.feedback ?? [];
}

export function QuizAssessmentPanel({
  quiz,
  result,
  initialAnswers,
  initialResult,
  isSubmitting,
  onSubmit,
}: QuizAssessmentPanelProps) {
  const { t } = useTranslation("courseDetails");
  const [answers, setAnswers] = useState<QuizAnswers>(initialAnswers ?? {});
  const [showValidation, setShowValidation] = useState(false);

  const initialAnswersKey = useMemo(
    () => JSON.stringify(initialAnswers ?? {}),
    [initialAnswers],
  );

  useEffect(() => {
    setAnswers(initialAnswers ?? {});
    setShowValidation(false);
  }, [quiz.assessment_id, initialAnswersKey]);

  const effectiveResult = result ?? initialResult;

  const allAnswered = useMemo(() => {
    return quiz.questions.every((question) =>
      hasAnswer(answers[question.item_id]),
    );
  }, [answers, quiz.questions]);

  const answeredCount = quiz.questions.filter((question) =>
    hasAnswer(answers[question.item_id]),
  ).length;

  function updateAnswer(questionId: string, value: QuizAnswerValue) {
    setAnswers((current) => ({
      ...current,
      [questionId]: value,
    }));
  }

  function handleSubmit() {
    if (!allAnswered) {
      setShowValidation(true);
      return;
    }

    setShowValidation(false);
    onSubmit(answers);
  }

  return (
    <section className="module-quiz-panel">
      <div className="module-quiz-panel__header">
        <div>
          <h3>
            <ClipboardCheck size={24} strokeWidth={2.2} />
            {quiz.title}
          </h3>

          <p>
            {t("quiz.passThreshold", {
              threshold: quiz.pass_threshold ?? 70,
            })}
          </p>
        </div>

        <span className="module-quiz-panel__progress">
          {t("quiz.answeredProgress", {
            answered: answeredCount,
            total: quiz.questions.length,
          })}
        </span>
      </div>

      <div className="module-quiz-panel__questions">
        {quiz.questions.map((question, index) => {
          const questionHasError =
            showValidation && !hasAnswer(answers[question.item_id]);

          return (
            <article
              key={question.item_id}
              className="module-quiz-question"
              aria-invalid={questionHasError}
            >
              <h4 id={question.item_id}>
                {t("quiz.questionLabel", {
                  index: index + 1,
                  question: question.text,
                })}
              </h4>

              <QuizOptionGroup
                questionId={question.item_id}
                type={question.type}
                choices={question.choices}
                value={answers[question.item_id]}
                onChange={(value) => updateAnswer(question.item_id, value)}
              />

              {questionHasError && (
                <p className="module-quiz-question__error">
                  {t("quiz.answerRequired")}
                </p>
              )}
            </article>
          );
        })}
      </div>

      <div className="module-quiz-panel__footer">
        <Button
          type="button"
          variant="primary"
          className="module-quiz-panel__submit"
          onClick={handleSubmit}
          disabled={isSubmitting}
          isLoading={isSubmitting}
        >
          <SendHorizontal size={16} strokeWidth={2.2} />
          {isSubmitting ? t("actions.submitting") : t("actions.submit")}
        </Button>

        {!allAnswered && showValidation && (
          <p className="module-quiz-panel__hint">
            {t("quiz.completeAllQuestions")}
          </p>
        )}
      </div>

      {effectiveResult && (
        <section
          className={
            getPassed(effectiveResult)
              ? "module-quiz-result module-quiz-result--passed"
              : "module-quiz-result module-quiz-result--failed"
          }
          aria-live="polite"
        >
          <div className="module-quiz-result__summary">
            {getPassed(effectiveResult) ? (
              <BadgeCheck size={20} strokeWidth={2.3} />
            ) : (
              <XCircle size={20} strokeWidth={2.3} />
            )}

            <strong>
              {t(
                getPassed(effectiveResult)
                  ? "quiz.resultPassed"
                  : "quiz.resultNotPassed",
              )}
            </strong>

            <span>
              {t("quiz.scoreSummary", {
                score: getScore(effectiveResult),
                maxScore: getMaxScore(effectiveResult),
                percent: getPercent(effectiveResult),
              })}
            </span>

            {getGermanGrade(effectiveResult) && (
              <span>
                {t("quiz.germanGrade", {
                  grade: getGermanGrade(effectiveResult),
                })}
              </span>
            )}
          </div>

          {getFeedbackItems(effectiveResult).length > 0 && (
            <details open className="module-quiz-result__details">
              <summary>{t("quiz.detailedFeedback")}</summary>

              <div className="module-quiz-result__feedback-list">
                {getFeedbackItems(effectiveResult).map((item, index) => (
                  <article key={`${item.item_id ?? index}`}>
                    <strong>
                      {t("quiz.feedbackItem", {
                        index: index + 1,
                        question: item.question ?? "",
                      })}
                    </strong>

                    <p>
                      {t("quiz.awarded", {
                        awarded: item.awarded_points ?? item.awarded ?? 0,
                        max: item.max_points ?? item.max ?? 0,
                        type: item.type ?? "-",
                      })}
                    </p>

                    {item.feedback && <p>{item.feedback}</p>}
                  </article>
                ))}
              </div>
            </details>
          )}
        </section>
      )}
    </section>
  );
}
