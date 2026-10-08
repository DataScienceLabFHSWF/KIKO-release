// frontend/src/features/adminKnowledgeCheck/pages/AdminKnowledgeCheckConfigPage.tsx

import { useEffect, useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  Brain,
  CheckSquare,
  Filter,
  Save,
  Search,
  Settings,
  Trash2,
  XCircle,
} from "lucide-react";
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
  adminKnowledgeCheckQueryKeys,
  deleteAdminKnowledgeQuestion,
  getAdminKnowledgeConfig,
  listAdminKnowledgeQuestions,
  updateAdminKnowledgeConfig,
} from "../api/AdminKnowledgeCheckApi";
import type {
  AdminKnowledgeQuestion,
  KnowledgeCheckConfig,
} from "../types/AdminKnowledgeCheck";
import "./AdminKnowledgeCheckConfigPage.css";

function sortNumbers(values: Set<number>) {
  return Array.from(values).sort((a, b) => a - b);
}

function getUniqueValues(
  questions: AdminKnowledgeQuestion[],
  key: "topic" | "type",
) {
  return Array.from(
    new Set(
      questions
        .map((question) => question[key])
        .filter((value): value is string => Boolean(value?.trim())),
    ),
  ).sort((a, b) => a.localeCompare(b));
}

function matchesSearch(question: AdminKnowledgeQuestion, searchText: string) {
  const query = searchText.trim().toLowerCase();

  if (!query) return true;

  return [
    question.question,
    question.topic,
    question.type,
    question.difficulty ?? "",
  ]
    .join(" ")
    .toLowerCase()
    .includes(query);
}

export function AdminKnowledgeCheckConfigPage() {
  const { t } = useTranslation("adminKnowledgeCheck");
  const queryClient = useQueryClient();

  usePageMeta({
    title: t("title"),
  });

  const [isHydrated, setIsHydrated] = useState(false);
  const [enabled, setEnabled] = useState(true);
  const [size, setSize] = useState(5);
  const [selectedIds, setSelectedIds] = useState<Set<number>>(new Set());

  const [topicFilter, setTopicFilter] = useState("all");
  const [typeFilter, setTypeFilter] = useState("all");
  const [searchText, setSearchText] = useState("");
  const [deleteTarget, setDeleteTarget] =
    useState<AdminKnowledgeQuestion | null>(null);

  const questionsQuery = useQuery({
    queryKey: adminKnowledgeCheckQueryKeys.questions,
    queryFn: listAdminKnowledgeQuestions,
    staleTime: 60_000,
  });

  const configQuery = useQuery({
    queryKey: adminKnowledgeCheckQueryKeys.config,
    queryFn: getAdminKnowledgeConfig,
    staleTime: 60_000,
  });

  const questions = questionsQuery.data ?? [];

  useEffect(() => {
    if (isHydrated || !configQuery.data) return;

    setEnabled(configQuery.data.enabled);
    setSize(configQuery.data.size);
    setSelectedIds(new Set(configQuery.data.question_ids));
    setIsHydrated(true);
  }, [configQuery.data, isHydrated]);

  const topics = useMemo(
    () => getUniqueValues(questions, "topic"),
    [questions],
  );
  const types = useMemo(() => getUniqueValues(questions, "type"), [questions]);

  const filteredQuestions = useMemo(() => {
    return questions.filter((question) => {
      if (topicFilter !== "all" && question.topic !== topicFilter) {
        return false;
      }

      if (typeFilter !== "all" && question.type !== typeFilter) {
        return false;
      }

      return matchesSearch(question, searchText);
    });
  }, [questions, searchText, topicFilter, typeFilter]);

  const selectedCount = selectedIds.size;
  const filteredSelectedCount = filteredQuestions.filter((question) =>
    selectedIds.has(question.question_id),
  ).length;

  const hasFilters =
    topicFilter !== "all" || typeFilter !== "all" || searchText.trim();

  const selectedIdsArray = useMemo(
    () => sortNumbers(selectedIds),
    [selectedIds],
  );

  const validationMessage = useMemo(() => {
    if (!enabled) return null;

    if (selectedCount === 0) {
      return t("validation.selectOne");
    }

    if (size < 1) {
      return t("validation.sizeMinimum");
    }

    if (size > selectedCount) {
      return t("validation.sizeTooLarge", {
        size,
        selected: selectedCount,
      });
    }

    return null;
  }, [enabled, selectedCount, size, t]);

  const saveMutation = useMutation({
    mutationFn: (config: KnowledgeCheckConfig) =>
      updateAdminKnowledgeConfig(config),
    onSuccess: async () => {
      await queryClient.invalidateQueries({
        queryKey: adminKnowledgeCheckQueryKeys.config,
      });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: deleteAdminKnowledgeQuestion,
    onSuccess: async (_, deletedQuestionId) => {
      setSelectedIds((current) => {
        const next = new Set(current);
        next.delete(deletedQuestionId);
        return next;
      });

      setDeleteTarget(null);

      await queryClient.invalidateQueries({
        queryKey: adminKnowledgeCheckQueryKeys.questions,
      });

      await queryClient.invalidateQueries({
        queryKey: adminKnowledgeCheckQueryKeys.config,
      });
    },
  });

  function handleToggleQuestion(questionId: number, checked: boolean) {
    setSelectedIds((current) => {
      const next = new Set(current);

      if (checked) {
        next.add(questionId);
      } else {
        next.delete(questionId);
      }

      return next;
    });
  }

  function handleSelectFiltered() {
    setSelectedIds((current) => {
      const next = new Set(current);

      filteredQuestions.forEach((question) => {
        next.add(question.question_id);
      });

      return next;
    });
  }

  function handleClearFiltered() {
    const filteredIds = new Set(
      filteredQuestions.map((question) => question.question_id),
    );

    setSelectedIds((current) => {
      const next = new Set(current);

      filteredIds.forEach((questionId) => {
        next.delete(questionId);
      });

      return next;
    });
  }

  function handleClearFilters() {
    setTopicFilter("all");
    setTypeFilter("all");
    setSearchText("");
  }

  function handleSave() {
    if (validationMessage) return;

    saveMutation.mutate({
      enabled,
      size: Math.max(1, Math.floor(size)),
      question_ids: selectedIdsArray,
    });
  }

  if (questionsQuery.isLoading || configQuery.isLoading) {
    return <LoadingState description={t("status.loading")} />;
  }

  if (questionsQuery.isError || configQuery.isError) {
    const error =
      questionsQuery.error instanceof Error
        ? questionsQuery.error
        : configQuery.error instanceof Error
          ? configQuery.error
          : null;

    return (
      <ErrorState
        title={t("errors.loadTitle")}
        description={error?.message ?? t("errors.loadDescription")}
        actionLabel={t("actions.retry")}
        onAction={() => {
          void questionsQuery.refetch();
          void configQuery.refetch();
        }}
      />
    );
  }

  return (
    <section className="admin-kc-page">
      <PageHeader
        icon={<Brain size={42} strokeWidth={1.8} />}
        title={t("title")}
        subtitle={t("subtitle")}
        action={
          <Button
            type="button"
            onClick={handleSave}
            isLoading={saveMutation.isPending}
            disabled={Boolean(validationMessage) || saveMutation.isPending}
          >
            <Save size={16} strokeWidth={2.3} />
            {t("actions.save")}
          </Button>
        }
      />

      {saveMutation.isSuccess && (
        <p className="admin-kc-page__success" role="status">
          {t("status.saved")}
        </p>
      )}

      {saveMutation.isError && (
        <p className="admin-kc-page__error" role="alert">
          {saveMutation.error instanceof Error
            ? saveMutation.error.message
            : t("errors.saveDescription")}
        </p>
      )}

      <div className="admin-kc-page__panel-grid">
        <section className="admin-kc-page__panel">
          <div className="admin-kc-page__section-title">
            <Settings size={22} strokeWidth={2.2} />
            <h2>{t("settings.title")}</h2>
          </div>

          <label className="admin-kc-page__toggle">
            <input
              type="checkbox"
              checked={enabled}
              onChange={(event) => setEnabled(event.currentTarget.checked)}
            />
            <span aria-hidden="true" />
            <strong>{t("settings.enabled")}</strong>
          </label>

          <label className="admin-kc-page__field">
            <span>{t("settings.questionsPerAssessment")}</span>
            <input
              type="number"
              min={1}
              value={size}
              onChange={(event) => {
                const nextValue = Number(event.currentTarget.value);
                setSize(Number.isFinite(nextValue) ? nextValue : 1);
              }}
            />
          </label>

          <p className="admin-kc-page__selected-count">
            {t("settings.selectedCount", {
              selected: selectedCount,
              total: questions.length,
            })}
          </p>

          {validationMessage && (
            <p className="admin-kc-page__warning" role="alert">
              {validationMessage}
            </p>
          )}
        </section>

        <section className="admin-kc-page__panel">
          <div className="admin-kc-page__section-title">
            <Filter size={22} strokeWidth={2.2} />
            <h2>{t("filters.title")}</h2>
          </div>

          <div className="admin-kc-page__filters">
            <label className="admin-kc-page__field">
              <span>{t("filters.topic")}</span>
              <select
                value={topicFilter}
                onChange={(event) => setTopicFilter(event.currentTarget.value)}
              >
                <option value="all">{t("filters.allTopics")}</option>
                {topics.map((topic) => (
                  <option key={topic} value={topic}>
                    {topic}
                  </option>
                ))}
              </select>
            </label>

            <label className="admin-kc-page__field">
              <span>{t("filters.type")}</span>
              <select
                value={typeFilter}
                onChange={(event) => setTypeFilter(event.currentTarget.value)}
              >
                <option value="all">{t("filters.allTypes")}</option>
                {types.map((type) => (
                  <option key={type} value={type}>
                    {type}
                  </option>
                ))}
              </select>
            </label>

            <label className="admin-kc-page__field">
              <span>{t("filters.search")}</span>
              <div className="admin-kc-page__search">
                <Search size={15} strokeWidth={2.2} aria-hidden="true" />
                <input
                  type="search"
                  value={searchText}
                  placeholder={t("filters.searchPlaceholder")}
                  onChange={(event) => setSearchText(event.currentTarget.value)}
                />
              </div>
            </label>
          </div>

          <div className="admin-kc-page__filter-actions">
            <Button
              type="button"
              variant="ghost"
              onClick={handleSelectFiltered}
              disabled={filteredQuestions.length === 0}
            >
              <CheckSquare size={16} strokeWidth={2.3} />
              {t("actions.selectFiltered")}
            </Button>

            <Button
              type="button"
              variant="ghost"
              onClick={handleClearFiltered}
              disabled={filteredSelectedCount === 0}
            >
              <XCircle size={16} strokeWidth={2.3} />
              {t("actions.clearFiltered")}
            </Button>

            {hasFilters && (
              <Button
                type="button"
                variant="plain"
                onClick={handleClearFilters}
              >
                {t("actions.clearFilters")}
              </Button>
            )}
          </div>
        </section>
      </div>

      <section className="admin-kc-page__question-section">
        <div className="admin-kc-page__section-heading">
          <div>
            <h2>{t("questions.title")}</h2>
            <p>
              {t("questions.visibleCount", {
                visible: filteredQuestions.length,
                total: questions.length,
              })}
            </p>
          </div>
        </div>

        {filteredQuestions.length === 0 ? (
          <EmptyState
            title={t("empty.title")}
            description={t("empty.description")}
          />
        ) : (
          <div className="admin-kc-page__question-list">
            {filteredQuestions.map((question) => {
              const isSelected = selectedIds.has(question.question_id);

              return (
                <article
                  key={question.question_id}
                  className="admin-kc-page__question-card"
                >
                  <div className="admin-kc-page__question-main">
                    <div className="admin-kc-page__question-meta">
                      <strong>
                        #{question.question_id} ·{" "}
                        {question.topic || t("questions.noTopic")}
                      </strong>
                      <span>{question.type || t("questions.noType")}</span>
                    </div>

                    <p>{question.question}</p>
                  </div>

                  <div className="admin-kc-page__question-actions">
                    <label className="admin-kc-page__include">
                      <input
                        type="checkbox"
                        checked={isSelected}
                        onChange={(event) =>
                          handleToggleQuestion(
                            question.question_id,
                            event.currentTarget.checked,
                          )
                        }
                      />
                      <span>{t("questions.include")}</span>
                    </label>

                    <Button
                      type="button"
                      variant="danger"
                      onClick={() => setDeleteTarget(question)}
                      disabled={deleteMutation.isPending}
                    >
                      <Trash2 size={15} strokeWidth={2.3} />
                      {t("actions.delete")}
                    </Button>
                  </div>
                </article>
              );
            })}
          </div>
        )}
      </section>

      {deleteTarget && (
        <div className="admin-kc-page__dialog-backdrop" role="presentation">
          <section
            className="admin-kc-page__dialog"
            role="dialog"
            aria-modal="true"
            aria-labelledby="delete-question-title"
          >
            <h2 id="delete-question-title">{t("delete.title")}</h2>

            <p>
              {t("delete.description", {
                id: deleteTarget.question_id,
              })}
            </p>

            <div className="admin-kc-page__dialog-question">
              {deleteTarget.question}
            </div>

            <div className="admin-kc-page__dialog-actions">
              <Button
                type="button"
                variant="ghost"
                onClick={() => setDeleteTarget(null)}
                disabled={deleteMutation.isPending}
              >
                {t("actions.cancel")}
              </Button>

              <Button
                type="button"
                variant="danger"
                isLoading={deleteMutation.isPending}
                onClick={() => deleteMutation.mutate(deleteTarget.question_id)}
              >
                <Trash2 size={15} strokeWidth={2.3} />
                {t("delete.confirm")}
              </Button>
            </div>
          </section>
        </div>
      )}
    </section>
  );
}
