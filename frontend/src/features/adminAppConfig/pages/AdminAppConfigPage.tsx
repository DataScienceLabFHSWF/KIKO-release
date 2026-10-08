// frontend/src/features/adminAppConfig/pages/AdminAppConfigPage.tsx

import { useEffect, useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  AlertTriangle,
  Brain,
  Cpu,
  FileQuestion,
  Languages,
  RotateCcw,
  Save,
  ScanText,
  Settings,
} from "lucide-react";
import { useTranslation } from "node_modules/react-i18next";

import { Button, ErrorState, LoadingState, PageHeader } from "@/components";
import { usePageMeta } from "@/app/hooks/usePageMeta";

import {
  adminAppConfigQueryKeys,
  getAdminAppConfig,
  updateAdminAppConfig,
} from "../api/AdminAppConfigApi";
import { AdminAppConfigField } from "../components/AdminAppConfigField";
import { AdminAppConfigSection } from "../components/AdminAppConfigSection";
import type { EditableAppConfig } from "../types/AdminAppConfig";
import {
  pickEditableAppConfig,
  validateEditableAppConfig,
} from "../utils/AdminAppConfigDefaults";
import "./AdminAppConfigPage.css";

type NumberField = {
  key: keyof EditableAppConfig;
  label: string;
  min?: number;
  max?: number;
};

const MODEL_OPTIONS = {
  embedding: ["nomic-embed-text:v1.5"],
  llm: ["llama3.3:70b", "nemotron:70b"],
  reasoning: ["nemotron-3-super:120b", "deepseek-r1:70b"],
  vlm: ["qwen2.5vl:7b"],
  ocr: ["trocr"],
  ocrLanguage: ["auto", "eng", "deu"],
  defaultLanguage: ["deu", "eng", "auto"],
};

function toNumber(value: string) {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : 0;
}

function cloneConfig(config: EditableAppConfig): EditableAppConfig {
  return JSON.parse(JSON.stringify(config)) as EditableAppConfig;
}

export function AdminAppConfigPage() {
  const { t } = useTranslation("adminAppConfig");
  const queryClient = useQueryClient();

  usePageMeta({
    title: t("title"),
  });

  const [editableConfig, setEditableConfig] =
    useState<EditableAppConfig | null>(null);

  const configQuery = useQuery({
    queryKey: adminAppConfigQueryKeys.appConfig,
    queryFn: getAdminAppConfig,
    staleTime: 60_000,
  });

  const appConfigResponse = configQuery.data;

  useEffect(() => {
    if (!appConfigResponse || editableConfig) return;

    setEditableConfig(pickEditableAppConfig(appConfigResponse.app_config));
  }, [appConfigResponse, editableConfig]);

  const originalEditableConfig = useMemo(() => {
    if (!appConfigResponse) return null;
    return pickEditableAppConfig(appConfigResponse.app_config);
  }, [appConfigResponse]);

  const validationErrors = useMemo(() => {
    if (!editableConfig) return [];
    return validateEditableAppConfig(editableConfig);
  }, [editableConfig]);

  const hasUnsavedChanges = useMemo(() => {
    if (!editableConfig || !originalEditableConfig) return false;

    return (
      JSON.stringify(editableConfig) !== JSON.stringify(originalEditableConfig)
    );
  }, [editableConfig, originalEditableConfig]);

  const updateMutation = useMutation({
    mutationFn: updateAdminAppConfig,
    onSuccess: async (response) => {
      await queryClient.setQueryData(
        adminAppConfigQueryKeys.appConfig,
        response,
      );

      setEditableConfig(pickEditableAppConfig(response.app_config));

      await queryClient.invalidateQueries({
        queryKey: adminAppConfigQueryKeys.appConfig,
      });
    },
  });

  function updateField<K extends keyof EditableAppConfig>(
    key: K,
    value: EditableAppConfig[K],
  ) {
    setEditableConfig((current) => {
      if (!current) return current;

      return {
        ...current,
        [key]: value,
      };
    });
  }

  function renderTextSelectField(
    key: keyof EditableAppConfig,
    label: string,
    options: string[],
    description?: string,
  ) {
    if (!editableConfig) return null;

    const value = String(editableConfig[key] ?? "");

    return (
      <AdminAppConfigField label={label} description={description}>
        <select
          value={value}
          onChange={(event) =>
            updateField(key, event.currentTarget.value as never)
          }
        >
          {!options.includes(value) && value && (
            <option value={value}>{value}</option>
          )}

          {options.map((option) => (
            <option key={option} value={option}>
              {option}
            </option>
          ))}
        </select>
      </AdminAppConfigField>
    );
  }

  function renderNumberField({ key, label, min = 0, max }: NumberField) {
    if (!editableConfig) return null;

    return (
      <AdminAppConfigField label={label}>
        <input
          type="number"
          min={min}
          max={max}
          value={Number(editableConfig[key] ?? 0)}
          onChange={(event) =>
            updateField(key, toNumber(event.currentTarget.value) as never)
          }
        />
      </AdminAppConfigField>
    );
  }

  function renderBooleanField(
    key: keyof EditableAppConfig,
    label: string,
    description?: string,
  ) {
    if (!editableConfig) return null;

    return (
      <label className="admin-app-config-page__switch">
        <input
          type="checkbox"
          checked={Boolean(editableConfig[key])}
          onChange={(event) =>
            updateField(key, event.currentTarget.checked as never)
          }
        />
        <span aria-hidden="true" />
        <div>
          <strong>{label}</strong>
          {description && <small>{description}</small>}
        </div>
      </label>
    );
  }

  function handleReset() {
    if (!originalEditableConfig) return;
    setEditableConfig(cloneConfig(originalEditableConfig));
  }

  function handleSave() {
    if (!editableConfig || validationErrors.length > 0) return;
    updateMutation.mutate(editableConfig);
  }

  if (configQuery.isLoading || !editableConfig) {
    return <LoadingState description={t("status.loading")} />;
  }

  if (configQuery.isError) {
    return (
      <ErrorState
        title={t("errors.loadTitle")}
        description={
          configQuery.error instanceof Error
            ? configQuery.error.message
            : t("errors.loadDescription")
        }
        actionLabel={t("actions.retry")}
        onAction={() => void configQuery.refetch()}
      />
    );
  }

  return (
    <section className="admin-app-config-page">
      <PageHeader
        icon={<Settings size={42} strokeWidth={1.9} />}
        title={t("title")}
        subtitle={t("subtitle")}
        action={
          <div className="admin-app-config-page__header-actions">
            <Button
              type="button"
              variant="ghost"
              onClick={handleReset}
              disabled={!hasUnsavedChanges || updateMutation.isPending}
            >
              <RotateCcw size={16} strokeWidth={2.3} />
              {t("actions.reset")}
            </Button>

            <Button
              type="button"
              onClick={handleSave}
              isLoading={updateMutation.isPending}
              disabled={
                !hasUnsavedChanges ||
                validationErrors.length > 0 ||
                updateMutation.isPending
              }
            >
              <Save size={16} strokeWidth={2.3} />
              {t("actions.save")}
            </Button>
          </div>
        }
      />

      {validationErrors.length > 0 && (
        <section className="admin-app-config-page__notice admin-app-config-page__notice--warning">
          <AlertTriangle size={18} strokeWidth={2.3} />
          <div>
            <strong>{t("validation.title")}</strong>
            <ul>
              {validationErrors.map((error) => (
                <li key={`${error.field}-${error.message}`}>{error.message}</li>
              ))}
            </ul>
          </div>
        </section>
      )}

      {updateMutation.isSuccess && (
        <p
          className="admin-app-config-page__notice admin-app-config-page__notice--success"
          role="status"
        >
          {t("status.saved")}
        </p>
      )}

      {updateMutation.isError && (
        <p
          className="admin-app-config-page__notice admin-app-config-page__notice--error"
          role="alert"
        >
          {updateMutation.error instanceof Error
            ? updateMutation.error.message
            : t("errors.saveDescription")}
        </p>
      )}

      <section className="admin-app-config-page__runtime">
        <article>
          <strong>{t("runtime.python")}</strong>
          <span>{appConfigResponse?.environment.python_version}</span>
        </article>

        <article>
          <strong>{t("runtime.platform")}</strong>
          <span>{appConfigResponse?.environment.platform}</span>
        </article>

        <article>
          <strong>{t("runtime.cuda")}</strong>
          <span>
            {appConfigResponse?.modules.torch.cuda.enabled
              ? t("runtime.enabled")
              : t("runtime.disabled")}
          </span>
        </article>

        <article>
          <strong>{t("runtime.device")}</strong>
          <span>{appConfigResponse?.modules.torch.cuda.device ?? "—"}</span>
        </article>
      </section>

      <AdminAppConfigSection
        title={t("sections.models.title")}
        description={t("sections.models.description")}
        icon={<Brain size={24} strokeWidth={2.2} />}
      >
        <div className="admin-app-config-page__grid admin-app-config-page__grid--3">
          {renderTextSelectField(
            "default_embedding_model",
            t("fields.defaultEmbeddingModel"),
            MODEL_OPTIONS.embedding,
          )}

          {renderTextSelectField(
            "default_llm_model",
            t("fields.defaultLlmModel"),
            MODEL_OPTIONS.llm,
          )}

          {renderTextSelectField(
            "default_reasoning_model",
            t("fields.defaultReasoningModel"),
            MODEL_OPTIONS.reasoning,
          )}
        </div>
      </AdminAppConfigSection>

      <AdminAppConfigSection
        title={t("sections.courseGeneration.title")}
        description={t("sections.courseGeneration.description")}
        icon={<FileQuestion size={24} strokeWidth={2.2} />}
      >
        <div className="admin-app-config-page__range-grid">
          <h3>{t("groups.qa")}</h3>
          {renderNumberField({
            key: "course_generator_qa_count_min",
            label: t("fields.minimum"),
            min: 1,
          })}
          {renderNumberField({
            key: "course_generator_qa_count_default",
            label: t("fields.default"),
            min: 1,
          })}
          {renderNumberField({
            key: "course_generator_qa_count_max",
            label: t("fields.maximum"),
            min: 1,
          })}

          <h3>{t("groups.quizQuestions")}</h3>
          {renderNumberField({
            key: "course_generator_quiz_question_count_min",
            label: t("fields.minimum"),
            min: 1,
          })}
          {renderNumberField({
            key: "course_generator_quiz_question_count_default",
            label: t("fields.default"),
            min: 1,
          })}
          {renderNumberField({
            key: "course_generator_quiz_question_count_max",
            label: t("fields.maximum"),
            min: 1,
          })}

          <h3>{t("groups.quizOptions")}</h3>
          {renderNumberField({
            key: "course_generator_quiz_option_count_min",
            label: t("fields.minimum"),
            min: 2,
          })}
          {renderNumberField({
            key: "course_generator_quiz_option_count_default",
            label: t("fields.default"),
            min: 2,
          })}
          {renderNumberField({
            key: "course_generator_quiz_option_count_max",
            label: t("fields.maximum"),
            min: 2,
          })}

          <h3>{t("groups.misconceptions")}</h3>
          {renderNumberField({
            key: "course_generator_misconception_count_min",
            label: t("fields.minimum"),
            min: 1,
          })}
          {renderNumberField({
            key: "course_generator_misconception_count_default",
            label: t("fields.default"),
            min: 1,
          })}
          {renderNumberField({
            key: "course_generator_misconception_count_max",
            label: t("fields.maximum"),
            min: 1,
          })}
        </div>
      </AdminAppConfigSection>

      <AdminAppConfigSection
        title={t("sections.vlm.title")}
        description={t("sections.vlm.description")}
        icon={<Cpu size={24} strokeWidth={2.2} />}
      >
        <div className="admin-app-config-page__grid admin-app-config-page__grid--2">
          {renderBooleanField("enable_vlm", t("fields.enableVlm"))}

          {renderTextSelectField(
            "preferred_vlm_model",
            t("fields.preferredVlmModel"),
            MODEL_OPTIONS.vlm,
          )}
        </div>
      </AdminAppConfigSection>

      <AdminAppConfigSection
        title={t("sections.ocr.title")}
        description={t("sections.ocr.description")}
        icon={<ScanText size={24} strokeWidth={2.2} />}
      >
        <div className="admin-app-config-page__grid admin-app-config-page__grid--3">
          {renderBooleanField("use_advanced_ocr", t("fields.useAdvancedOcr"))}

          {renderTextSelectField(
            "preferred_ocr_engine",
            t("fields.preferredOcrEngine"),
            MODEL_OPTIONS.ocr,
          )}

          {renderTextSelectField(
            "ocr_language",
            t("fields.ocrLanguage"),
            MODEL_OPTIONS.ocrLanguage,
          )}

          {renderBooleanField(
            "ocr_preprocessing",
            t("fields.ocrPreprocessing"),
          )}

          {renderBooleanField(
            "ocr_skew_correction",
            t("fields.ocrSkewCorrection"),
          )}

          {renderBooleanField(
            "ocr_noise_reduction",
            t("fields.ocrNoiseReduction"),
          )}
        </div>
      </AdminAppConfigSection>

      <AdminAppConfigSection
        title={t("sections.multilingual.title")}
        description={t("sections.multilingual.description")}
        icon={<Languages size={24} strokeWidth={2.2} />}
      >
        <div className="admin-app-config-page__grid admin-app-config-page__grid--3">
          {renderBooleanField(
            "enable_multilingual",
            t("fields.enableMultilingual"),
          )}

          {renderBooleanField(
            "language_detection",
            t("fields.languageDetection"),
          )}

          {renderTextSelectField(
            "default_language",
            t("fields.defaultLanguage"),
            MODEL_OPTIONS.defaultLanguage,
          )}
        </div>
      </AdminAppConfigSection>
    </section>
  );
}
