// frontend/src/features/knowledgeAssessment/pages/KnowledgeAssessmentPage.tsx

import { Brain, SendHorizontal } from "lucide-react";
import { useMemo, useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { useTranslation } from "node_modules/react-i18next";

import {
  Button,
  EmptyState,
  ErrorState,
  LoadingState,
  PageHeader,
} from "@/components";
import { usePageMeta } from "@/app/hooks/usePageMeta";

import {
  getAssessmentQuiz,
  submitAssessmentQuiz,
} from "../api/KnowledgeAssessmentApi";
import { KnowledgeQuestionCard } from "../components/KnowledgeQuestionCard";
import { KnowledgeAssessmentResultPanel } from "../components/KnowledgeAssessmentResultPanel";
import type {
  AssessmentResult,
  AssessmentSubmitRequest,
} from "../types/KnowledgeAssessment";

import "./KnowledgeAssessmentPage.css";

function normalizeLanguage(language: string) {
  return language.startsWith("de") ? "de" : "en";
}

export function KnowledgeAssessmentPage() {
  const { t, i18n } = useTranslation("knowledgeAssessment");

  usePageMeta({
    title: t("title"),
  });

  const [answers, setAnswers] = useState<Record<number, string>>({});
  const [validationMessage, setValidationMessage] = useState<string | null>(
    null,
  );
  const [result, setResult] = useState<AssessmentResult | null>(null);

  const quizQuery = useQuery({
    queryKey: ["knowledge-assessment", "quiz"],
    queryFn: getAssessmentQuiz,
    staleTime: 60_000,
  });

  const questions = quizQuery.data ?? [];

  const answeredCount = useMemo(() => {
    return questions.filter(
      (question) => answers[question.question_id]?.trim().length > 0,
    ).length;
  }, [answers, questions]);

  const isComplete = questions.length > 0 && answeredCount === questions.length;

  const submitMutation = useMutation({
    mutationFn: (payload: AssessmentSubmitRequest) =>
      submitAssessmentQuiz(payload, normalizeLanguage(i18n.language)),
    onSuccess: (data) => {
      setResult(data);
      setValidationMessage(null);
    },
  });

  function handleAnswerChange(questionId: number, value: string) {
    setAnswers((current) => ({
      ...current,
      [questionId]: value,
    }));

    setValidationMessage(null);
  }

  function handleSubmit() {
    if (!isComplete) {
      setValidationMessage(t("validation.allRequired"));
      return;
    }

    const payload: AssessmentSubmitRequest = {
      answers: questions.map((question) => ({
        question_id: question.question_id,
        user_answer: answers[question.question_id].trim(),
      })),
    };

    submitMutation.mutate(payload);
  }

  if (quizQuery.isLoading) {
    return <LoadingState description={t("status.loading")} />;
  }

  if (quizQuery.isError) {
    return (
      <ErrorState
        title={t("errors.loadTitle")}
        description={
          quizQuery.error instanceof Error
            ? quizQuery.error.message
            : t("errors.loadDescription")
        }
        actionLabel={t("actions.retry")}
        onAction={() => void quizQuery.refetch()}
      />
    );
  }

  return (
    <section className="knowledge-assessment-page">
      <PageHeader
        icon={<Brain size={42} strokeWidth={1.8} />}
        title={t("title")}
        subtitle={t("subtitle")}
      />

      {questions.length === 0 ? (
        <EmptyState
          title={t("empty.title")}
          description={t("empty.description")}
        />
      ) : (
        <>
          <div className="knowledge-assessment-page__intro">
            <p>{t("intro")}</p>

            <span>
              {t("progress", {
                answered: answeredCount,
                total: questions.length,
              })}
            </span>
          </div>

          <div className="knowledge-assessment-page__form">
            {questions.map((question, index) => (
              <KnowledgeQuestionCard
                key={question.question_id}
                question={question}
                index={index}
                value={answers[question.question_id] ?? ""}
                disabled={submitMutation.isPending}
                onChange={handleAnswerChange}
              />
            ))}

            {validationMessage && (
              <p className="knowledge-assessment-page__warning" role="alert">
                {validationMessage}
              </p>
            )}

            {submitMutation.isError && (
              <p className="knowledge-assessment-page__error" role="alert">
                {submitMutation.error instanceof Error
                  ? submitMutation.error.message
                  : t("errors.submitDescription")}
              </p>
            )}

            <div className="knowledge-assessment-page__actions">
              <Button
                type="button"
                onClick={handleSubmit}
                isLoading={submitMutation.isPending}
              >
                <span className="knowledge-assessment-page__submit-content">
                  <SendHorizontal size={17} strokeWidth={2.3} />
                  {submitMutation.isPending
                    ? t("actions.submitting")
                    : t("actions.submit")}
                </span>
              </Button>
            </div>
          </div>

          {result && <KnowledgeAssessmentResultPanel result={result} />}
        </>
      )}
    </section>
  );
}
