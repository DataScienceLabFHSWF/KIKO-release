// frontend/src/features/courseGenerator/pages/CourseGeneratorPage.tsx

import { FilePenLine, Rocket, Save, FileX } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { useTranslation } from "node_modules/react-i18next";
import { Button, ErrorState, LoadingState, PageHeader } from "@/components";
import { usePageMeta } from "@/app/hooks/usePageMeta";
import {
  cancelPdfCourseUploadJob,
  createCourseFromGeneratedContent,
  getCourseGeneratorConfig,
  getPdfCourseUploadJob,
  startPdfCourseUploadJob,
  uploadCourseDocument,
} from "../api/CourseGeneratorApi";
import { CourseGeneratorControls } from "../components/CourseGeneratorControls";
import { CourseGeneratorJobStatus } from "../components/CourseGeneratorJobStatus";
import { CourseGeneratorPreviewTabs } from "../components/CourseGeneratorPreviewTabs";
import type {
  CourseJson,
  CourseUploadJobResponse,
  CourseUploadResult,
} from "../types/CourseGenerator";
import {
  buildSaveCourseFormData,
  buildUploadFormData,
  clampNumber,
  getCourseTitle,
  isPdfFile,
} from "../utils/CourseGeneratorUtils";
import "./CourseGeneratorPage.css";

function normalizeLanguage(language: string) {
  return language.startsWith("de") ? "de" : "en";
}

export function CourseGeneratorPage() {
  const { t, i18n } = useTranslation("courseGenerator");
  const language = normalizeLanguage(i18n.language);

  usePageMeta({ title: t("title") });

  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [activeJobId, setActiveJobId] = useState<string | null>(null);
  const [uploadResult, setUploadResult] = useState<CourseUploadResult | null>(
    null,
  );
  const [editedCourseJson, setEditedCourseJson] = useState<CourseJson | null>(
    null,
  );
  const [courseTitle, setCourseTitle] = useState("");
  const [statusMessage, setStatusMessage] = useState<string | null>(null);
  const [statusVariant, setStatusVariant] = useState<
    "success" | "warning" | "error" | "info"
  >("info");

  const configQuery = useQuery({
    queryKey: ["course-generator", "config"],
    queryFn: getCourseGeneratorConfig,
    staleTime: 5 * 60_000,
  });

  const appConfig = configQuery.data?.app_config ?? {};

  const defaultCounts = useMemo(() => {
    const qaMin = Number(appConfig.course_generator_qa_count_min ?? 1);
    const qaMax = Number(appConfig.course_generator_qa_count_max ?? 10);
    const qaDefault = clampNumber(
      Number(appConfig.course_generator_qa_count_default ?? 5),
      qaMin,
      qaMax,
    );

    const quizMin = Number(
      appConfig.course_generator_quiz_question_count_min ?? 1,
    );
    const quizMax = Number(
      appConfig.course_generator_quiz_question_count_max ?? 4,
    );
    const quizDefault = clampNumber(
      Number(appConfig.course_generator_quiz_question_count_default ?? 3),
      quizMin,
      quizMax,
    );

    const optionMin = Number(
      appConfig.course_generator_quiz_option_count_min ?? 2,
    );
    const optionMax = Number(
      appConfig.course_generator_quiz_option_count_max ?? 4,
    );
    const optionDefault = clampNumber(
      Number(appConfig.course_generator_quiz_option_count_default ?? 3),
      optionMin,
      optionMax,
    );

    const misconceptionMin = Number(
      appConfig.course_generator_misconception_count_min ?? 1,
    );
    const misconceptionMax = Number(
      appConfig.course_generator_misconception_count_max ?? 4,
    );
    const misconceptionDefault = clampNumber(
      Number(appConfig.course_generator_misconception_count_default ?? 2),
      misconceptionMin,
      misconceptionMax,
    );

    return {
      qa: { min: qaMin, max: qaMax, value: qaDefault },
      quiz: { min: quizMin, max: quizMax, value: quizDefault },
      options: { min: optionMin, max: optionMax, value: optionDefault },
      misconceptions: {
        min: misconceptionMin,
        max: misconceptionMax,
        value: misconceptionDefault,
      },
    };
  }, [appConfig]);

  const [qaCount, setQaCount] = useState(5);
  const [quizQuestionCount, setQuizQuestionCount] = useState(3);
  const [quizOptionCount, setQuizOptionCount] = useState(3);
  const [misconceptionCount, setMisconceptionCount] = useState(2);

  useEffect(() => {
    setQaCount(defaultCounts.qa.value);
    setQuizQuestionCount(defaultCounts.quiz.value);
    setQuizOptionCount(defaultCounts.options.value);
    setMisconceptionCount(defaultCounts.misconceptions.value);
  }, [defaultCounts]);

  const uploadMutation = useMutation({
    mutationFn: async () => {
      if (!selectedFile) {
        throw new Error(t("errors.noFile"));
      }

      const embeddingModel = appConfig.default_embedding_model;
      const llmModel = appConfig.default_llm_model;

      if (!embeddingModel || !llmModel) {
        throw new Error(t("errors.missingModelConfig"));
      }

      const formData = buildUploadFormData({
        file: selectedFile,
        embeddingModel,
        llmModel,
        qaCount,
        quizQuestionCount,
        quizOptionCount,
        misconceptionCount,
        replaceExisting: false,
      });

      if (isPdfFile(selectedFile)) {
        return startPdfCourseUploadJob(formData, language);
      }

      return uploadCourseDocument(formData, language);
    },
    onSuccess: (data) => {
      if ("job_id" in data) {
        setActiveJobId(data.job_id);
        setStatusMessage(null);
        return;
      }

      handleUploadResult(data);
    },
    onError: (error) => {
      setStatusVariant("error");
      setStatusMessage(
        error instanceof Error ? error.message : t("errors.processingFailed"),
      );
    },
  });

  const jobQuery = useQuery({
    queryKey: ["course-generator", "pdf-job", activeJobId, language],
    queryFn: () => getPdfCourseUploadJob(activeJobId!, language),
    enabled: Boolean(activeJobId),
    refetchInterval: activeJobId ? 2_000 : false,
  });

  useEffect(() => {
    const job = jobQuery.data;

    if (!job) return;

    if (
      job.status === "queued" ||
      job.status === "processing" ||
      job.status === "cancelling"
    ) {
      return;
    }

    if (job.status === "completed") {
      setActiveJobId(null);

      if (job.result) {
        handleUploadResult(job.result);
      } else {
        setStatusVariant("error");
        setStatusMessage(t("errors.emptyJobResult"));
      }

      return;
    }

    if (job.status === "cancelled") {
      setActiveJobId(null);
      setUploadResult(null);
      setEditedCourseJson(null);
      setStatusVariant("warning");
      setStatusMessage(t("status.cancelled"));
      return;
    }

    if (job.status === "failed") {
      setActiveJobId(null);
      setStatusVariant("error");
      setStatusMessage(job.error || t("errors.processingFailed"));
    }
  }, [jobQuery.data, t]);

  const cancelMutation = useMutation({
    mutationFn: () => cancelPdfCourseUploadJob(activeJobId!, language),
    onSuccess: (job: CourseUploadJobResponse) => {
      setStatusVariant("warning");
      setStatusMessage(job.message);
    },
  });

  const saveMutation = useMutation({
    mutationFn: () => {
      if (!uploadResult) {
        throw new Error(t("errors.nothingToSave"));
      }

      const formData = buildSaveCourseFormData({
        result: uploadResult,
        editedCourseJson,
        title: courseTitle,
      });

      return createCourseFromGeneratedContent(formData, language);
    },
    onSuccess: (course) => {
      setStatusVariant("success");
      setStatusMessage(t("save.saved", { title: course.title }));
    },
    onError: (error) => {
      setStatusVariant("error");
      setStatusMessage(
        error instanceof Error ? error.message : t("save.failed"),
      );
    },
  });

  function handleUploadResult(result: CourseUploadResult) {
    if (result.message === "file_exists") {
      setStatusVariant("warning");
      setStatusMessage(result.detail || t("status.fileExists"));
      return;
    }

    if (result.message === "markdown_exists") {
      setStatusVariant("warning");
      setStatusMessage(result.detail || t("status.markdownExists"));
      return;
    }

    setUploadResult(result);
    setEditedCourseJson(result.course_json ?? null);
    setCourseTitle(getCourseTitle(result.course_json));
    setStatusVariant("success");
    setStatusMessage(t("status.complete"));
  }

  function handleFileChange(file: File | null) {
    setSelectedFile(file);
    setUploadResult(null);
    setEditedCourseJson(null);
    setActiveJobId(null);
    setStatusMessage(null);
    setCourseTitle("");
  }

  if (configQuery.isLoading) {
    return <LoadingState description={t("status.loadingConfig")} />;
  }

  if (configQuery.isError) {
    return (
      <ErrorState
        title={t("errors.configTitle")}
        description={
          configQuery.error instanceof Error
            ? configQuery.error.message
            : t("errors.configDescription")
        }
        actionLabel={t("actions.retry")}
        onAction={() => void configQuery.refetch()}
      />
    );
  }

  const isBusy =
    uploadMutation.isPending ||
    Boolean(activeJobId) ||
    jobQuery.data?.status === "processing" ||
    jobQuery.data?.status === "queued";

  return (
    <section className="course-generator-page">
      <PageHeader
        icon={<FilePenLine size={44} strokeWidth={1.9} />}
        title={t("title")}
        subtitle={t("subtitle")}
      />

      <CourseGeneratorControls
        file={selectedFile}
        isBusy={isBusy}
        qaCount={qaCount}
        quizQuestionCount={quizQuestionCount}
        quizOptionCount={quizOptionCount}
        misconceptionCount={misconceptionCount}
        ranges={defaultCounts}
        showPdfOptions={isPdfFile(selectedFile)}
        onFileChange={handleFileChange}
        onQaCountChange={setQaCount}
        onQuizQuestionCountChange={setQuizQuestionCount}
        onQuizOptionCountChange={setQuizOptionCount}
        onMisconceptionCountChange={setMisconceptionCount}
      />

      <div className="course-generator-page__actions">
        <Button
          type="button"
          onClick={() => uploadMutation.mutate()}
          disabled={!selectedFile || isBusy}
          isLoading={uploadMutation.isPending}
        >
          <Rocket size={18} />
          {isBusy ? t("actions.processing") : t("actions.process")}
        </Button>

        {activeJobId && (
          <Button
            type="button"
            variant="danger"
            onClick={() => cancelMutation.mutate()}
            disabled={
              cancelMutation.isPending || jobQuery.data?.status === "cancelling"
            }
          >
            <FileX size={18} />
            {t("actions.abort")}
          </Button>
        )}
      </div>

      {statusMessage && !activeJobId && (
        <p
          className={`course-generator-page__status course-generator-page__status--${statusVariant}`}
          role={statusVariant === "error" ? "alert" : "status"}
        >
          {statusMessage}
        </p>
      )}

      {activeJobId && jobQuery.data && (
        <CourseGeneratorJobStatus job={jobQuery.data} />
      )}

      {uploadResult && (
        <>
          <CourseGeneratorPreviewTabs
            result={uploadResult}
            editedCourseJson={editedCourseJson}
            defaultReasoningModel={appConfig.default_reasoning_model || ""}
            language={language}
            onCourseJsonChange={setEditedCourseJson}
          />

          <section className="course-generator-save">
            <div className="course-generator-save__header">
              <Save size={30} strokeWidth={2.1} />
              <h2>{t("save.title")}</h2>
            </div>

            <label className="course-generator-save__field">
              <span>{t("save.courseTitle")}</span>
              <input
                value={courseTitle}
                onChange={(event) => setCourseTitle(event.currentTarget.value)}
              />
            </label>

            <Button
              type="button"
              onClick={() => saveMutation.mutate()}
              disabled={saveMutation.isPending}
              isLoading={saveMutation.isPending}
            >
              <Save size={18} />
              {t("save.button")}
            </Button>
          </section>
        </>
      )}
    </section>
  );
}
