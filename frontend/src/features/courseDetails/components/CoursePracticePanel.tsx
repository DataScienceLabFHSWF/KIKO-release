// frontend/src/features/courseDetails/components/CoursePracticePanel.tsx

import { useEffect, useMemo, useState } from "react";
import {
  CheckCircle2,
  Eye,
  EyeOff,
  FileBarChart,
  Trash2,
  XCircle,
} from "lucide-react";
import { useMutation } from "@tanstack/react-query";
import { useTranslation } from "node_modules/react-i18next";
import { MarkdownView, Button } from "@/components";
import {
  evaluatePracticeAnswer,
  saveLearnerCourseProgress,
  type PracticeAnswerEvaluationResponse,
} from "../api/LearnerCourseDetailsApi";
import type {
  CoursePracticeQuestion,
  PracticeAnswers,
  PracticeEvaluation,
} from "../types/LearnerCourseDetails";
import "./CoursePracticePanel.css";

type CoursePracticePanelProps = {
  courseId: number;
  moduleId: string;
  currentNav: string;
  questions: CoursePracticeQuestion[];
  moduleMisconceptions: string[];
  initialAnswers?: Record<string, unknown> | null;
};

type PracticeQuestionRow = {
  question: CoursePracticeQuestion;
  answerKey: string;
};

function buildAnswerKey(moduleId: string, questionId: string) {
  return `${moduleId}_${questionId}`;
}

function normalizeInitialAnswers(
  value?: Record<string, unknown> | null,
): PracticeAnswers {
  if (!value || typeof value !== "object") {
    return {};
  }

  return Object.fromEntries(
    Object.entries(value).map(([key, item]) => [
      key,
      typeof item === "string" ? item : String(item ?? ""),
    ]),
  );
}

function buildQuestionRows(
  moduleId: string,
  questions: CoursePracticeQuestion[],
): PracticeQuestionRow[] {
  const seenIds = new Map<string, number>();

  return questions.map((question, index) => {
    const baseId =
      typeof question.id === "string" && question.id.trim()
        ? question.id.trim()
        : `practice-${index + 1}`;

    const previousCount = seenIds.get(baseId) ?? 0;
    seenIds.set(baseId, previousCount + 1);

    const safeQuestionId =
      previousCount === 0 ? baseId : `${baseId}-${index + 1}`;

    return {
      question,
      answerKey: buildAnswerKey(moduleId, safeQuestionId),
    };
  });
}

function getGradeVariant(grade: PracticeEvaluation["grade"]) {
  const numericGrade = Number(grade);

  if (!Number.isFinite(numericGrade)) return "info";
  if (numericGrade <= 2) return "success";
  if (numericGrade <= 4) return "warning";

  return "error";
}

function getGradeLabel(grade: PracticeEvaluation["grade"]) {
  if (grade === null || grade === undefined || grade === "") {
    return "—";
  }

  const numericGrade = Number(grade);

  if (!Number.isFinite(numericGrade)) {
    return String(grade);
  }

  if (numericGrade <= 1) return `Grade ${numericGrade} · Excellent`;
  if (numericGrade <= 2) return `Grade ${numericGrade} · Good`;
  if (numericGrade <= 3) return `Grade ${numericGrade} · Satisfactory`;
  if (numericGrade <= 4) return `Grade ${numericGrade} · Sufficient`;

  return `Grade ${numericGrade} · Insufficient`;
}

export function CoursePracticePanel({
  courseId,
  moduleId,
  currentNav,
  questions,
  moduleMisconceptions,
  initialAnswers,
}: CoursePracticePanelProps) {
  const { t } = useTranslation("courseDetails");

  const [answers, setAnswers] = useState<PracticeAnswers>({});
  const [shownAnswers, setShownAnswers] = useState<Record<string, boolean>>({});
  const [evaluations, setEvaluations] = useState<
    Record<string, PracticeEvaluation>
  >({});
  const [localErrors, setLocalErrors] = useState<Record<string, string>>({});
  const [evaluatingAnswerKey, setEvaluatingAnswerKey] = useState<string | null>(
    null,
  );
  const [savingAnswerKey, setSavingAnswerKey] = useState<string | null>(null);

  const questionRows = useMemo(() => {
    return buildQuestionRows(moduleId, questions);
  }, [moduleId, questions]);

  const cleanModuleMisconceptions = useMemo(
    () =>
      (moduleMisconceptions ?? []).map((item) => item.trim()).filter(Boolean),
    [moduleMisconceptions],
  );

  useEffect(() => {
    setAnswers(normalizeInitialAnswers(initialAnswers));
    setEvaluations({});
    setShownAnswers({});
    setLocalErrors({});
    setEvaluatingAnswerKey(null);
    setSavingAnswerKey(null);
  }, [moduleId, initialAnswers]);

  const saveProgressMutation = useMutation({
    mutationFn: (nextAnswers: PracticeAnswers) =>
      saveLearnerCourseProgress(courseId, {
        current_nav: currentNav,
        current_module_id: moduleId,
        practice_answers: nextAnswers,
      }),
  });

  const evaluateMutation = useMutation({
    mutationFn: ({
      question,
      answer,
    }: {
      question: CoursePracticeQuestion;
      answer: string;
    }) =>
      evaluatePracticeAnswer({
        question: question.prompt,
        reference_answer: question.referenceAnswer,
        user_answer: answer,
        misconceptions: cleanModuleMisconceptions,
      }),
  });

  function updateAnswer(answerKey: string, value: string) {
    setAnswers((current) => ({
      ...current,
      [answerKey]: value,
    }));

    setLocalErrors((current) => ({
      ...current,
      [answerKey]: "",
    }));

    setEvaluations((current) => {
      const copy = { ...current };
      delete copy[answerKey];
      return copy;
    });
  }

  async function saveAnswers(nextAnswers: PracticeAnswers, answerKey: string) {
    setSavingAnswerKey(answerKey);

    try {
      await saveProgressMutation.mutateAsync(nextAnswers);
    } catch (error) {
      setLocalErrors((current) => ({
        ...current,
        [answerKey]:
          error instanceof Error ? error.message : t("practice.saveFailed"),
      }));
    } finally {
      setSavingAnswerKey(null);
    }
  }

  async function handleBlur(answerKey: string) {
    await saveAnswers(answers, answerKey);
  }

  async function handleClear(answerKey: string) {
    const nextAnswers = {
      ...answers,
      [answerKey]: "",
    };

    setAnswers(nextAnswers);

    setEvaluations((current) => {
      const copy = { ...current };
      delete copy[answerKey];
      return copy;
    });

    setLocalErrors((current) => ({
      ...current,
      [answerKey]: "",
    }));

    await saveAnswers(nextAnswers, answerKey);
  }

  async function handleEvaluate(
    question: CoursePracticeQuestion,
    answerKey: string,
  ) {
    const answer = answers[answerKey]?.trim() ?? "";

    if (!answer) {
      setLocalErrors((current) => ({
        ...current,
        [answerKey]: t("practice.validation.required"),
      }));
      return;
    }

    setLocalErrors((current) => ({
      ...current,
      [answerKey]: "",
    }));

    setEvaluatingAnswerKey(answerKey);

    try {
      const result: PracticeAnswerEvaluationResponse =
        await evaluateMutation.mutateAsync({
          question,
          answer,
        });

      setEvaluations((current) => ({
        ...current,
        [answerKey]: {
          message: result.message,
          grade: result.grade,
          summary: result.summary,
          misconceptions_considered: result.misconceptions_considered ?? [],
        },
      }));

      await saveAnswers(answers, answerKey);
    } catch (error) {
      setLocalErrors((current) => ({
        ...current,
        [answerKey]:
          error instanceof Error
            ? error.message
            : t("practice.evaluationFailed"),
      }));
    } finally {
      setEvaluatingAnswerKey(null);
    }
  }

  if (questionRows.length === 0) {
    return (
      <p className="course-practice-panel__empty">
        {t("messages.noPracticeQuestions")}
      </p>
    );
  }

  return (
    <div className="course-practice-panel">
      {questionRows.map(({ question, answerKey }, index) => {
        const answer = answers[answerKey] ?? "";
        const isAnswerVisible = Boolean(shownAnswers[answerKey]);
        const evaluation = evaluations[answerKey];
        const localError = localErrors[answerKey];

        const isThisQuestionEvaluating = evaluatingAnswerKey === answerKey;
        const isAnotherQuestionEvaluating =
          evaluatingAnswerKey !== null && evaluatingAnswerKey !== answerKey;
        const isThisQuestionSaving = savingAnswerKey === answerKey;

        const variant = getGradeVariant(evaluation?.grade);

        return (
          <article key={answerKey} className="course-practice-card">
            <h3 className="course-practice-card__question">
              Q{index + 1}. {question.prompt}
            </h3>

            <label className="course-practice-card__answer">
              <span>{t("practice.yourAnswer")}</span>

              <textarea
                rows={5}
                value={answer}
                onChange={(event) =>
                  updateAnswer(answerKey, event.currentTarget.value)
                }
                onBlur={() => void handleBlur(answerKey)}
                placeholder={t("practice.answerPlaceholder")}
                disabled={isThisQuestionEvaluating}
              />
            </label>

            {localError && (
              <p className="course-practice-card__error" role="alert">
                {localError}
              </p>
            )}

            <div className="course-practice-card__actions">
              <Button
                type="button"
                variant="ghost"
                onClick={() =>
                  setShownAnswers((current) => ({
                    ...current,
                    [answerKey]: !current[answerKey],
                  }))
                }
                disabled={isThisQuestionEvaluating}
              >
                {isAnswerVisible ? (
                  <EyeOff size={16} strokeWidth={2.2} />
                ) : (
                  <Eye size={16} strokeWidth={2.2} />
                )}
                {isAnswerVisible
                  ? t("practice.hideAnswer")
                  : t("practice.showAnswer")}
              </Button>

              <Button
                type="button"
                variant="danger"
                onClick={() => void handleClear(answerKey)}
                disabled={isThisQuestionSaving || isThisQuestionEvaluating}
              >
                <Trash2 size={16} strokeWidth={2.2} />
                {t("practice.clear")}
              </Button>

              <Button
                type="button"
                variant="primary"
                onClick={() => void handleEvaluate(question, answerKey)}
                disabled={
                  isThisQuestionSaving ||
                  isThisQuestionEvaluating ||
                  isAnotherQuestionEvaluating
                }
                isLoading={isThisQuestionEvaluating}
              >
                <FileBarChart size={16} strokeWidth={2.2} />
                {isThisQuestionEvaluating
                  ? t("practice.evaluating")
                  : t("practice.evaluateAnswer")}
              </Button>
            </div>

            {evaluation && (
              <section
                className={`course-practice-card__result course-practice-card__result--${variant}`}
                aria-live="polite"
              >
                <div className="course-practice-card__result-title">
                  {variant === "success" ? (
                    <CheckCircle2 size={18} strokeWidth={2.2} />
                  ) : (
                    <XCircle size={18} strokeWidth={2.2} />
                  )}

                  <strong>
                    {t("practice.evaluationCompleted", {
                      grade: getGradeLabel(evaluation.grade),
                    })}
                  </strong>
                </div>

                {evaluation.message && evaluation.message !== "success" && (
                  <p>{evaluation.message}</p>
                )}

                {evaluation.summary && (
                  <details open className="course-practice-card__details">
                    <summary>{t("practice.evaluation")}</summary>
                    <MarkdownView
                      content={evaluation.summary}
                      courseId={courseId}
                    />
                  </details>
                )}
                {evaluation.misconceptions_considered?.length ? (
                  <details className="course-practice-card__details">
                    <summary>{t("practice.misconceptionsConsidered")}</summary>
                    <ul className="course-practice-card__misconception-list">
                      {evaluation.misconceptions_considered.map(
                        (item, itemIndex) => (
                          <li key={`${answerKey}-misconception-${itemIndex}`}>
                            {item}
                          </li>
                        ),
                      )}
                    </ul>
                  </details>
                ) : null}
              </section>
            )}

            {isAnswerVisible && (
              <details open className="course-practice-card__details">
                <summary>{t("practice.suggestedAnswer")}</summary>
                <MarkdownView
                  content={
                    question.referenceAnswer || t("practice.noSuggestedAnswer")
                  }
                  courseId={courseId}
                />
              </details>
            )}
          </article>
        );
      })}
    </div>
  );
}
