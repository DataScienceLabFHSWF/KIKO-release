// frontend/src/features/learner/pages/LearnerDashboardPage.tsx

import {
  BookOpen,
  Bot,
  CheckCircle2,
  Clock3,
  FileText,
  GraduationCap,
  Hourglass,
  Trophy,
  XCircle,
} from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { useTranslation } from "node_modules/react-i18next";
import { usePageMeta } from "@/app/hooks/usePageMeta";
import {
  DashboardMetricCard,
  ErrorState,
  LoadingState,
  PageHeader,
} from "@/components";
import { getLearnerStatistics } from "../api/LearnerApi";
import type { LearnerStatistics } from "../types/Learner";
import "./LearnerDashboardPage.css";

function formatDateTime(value: string) {
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

export function LearnerDashboardPage() {
  const { t } = useTranslation("learnerDashboard");

  const [statistics, setStatistics] = useState<LearnerStatistics | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  usePageMeta({
    title: t("metaTitle"),
  });

  async function loadStatistics() {
    setIsLoading(true);
    setError(null);

    try {
      const response = await getLearnerStatistics();
      setStatistics(response);
    } catch (error) {
      setError(
        error instanceof Error ? error.message : t("messages.loadFailed"),
      );
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    void loadStatistics();
  }, []);

  const progressPercent = useMemo(() => {
    if (!statistics) return 0;

    return Math.max(0, Math.min(100, statistics.courses_progress_percent ?? 0));
  }, [statistics]);

  if (isLoading) {
    return <LoadingState description={t("messages.loading")} />;
  }

  if (error || !statistics) {
    return (
      <ErrorState
        title={t("messages.unavailableTitle")}
        description={error ?? t("messages.unavailableDescription")}
        actionLabel={t("actions.retry")}
        onAction={() => void loadStatistics()}
      />
    );
  }

  return (
    <section className="learner-dashboard-page">
      <PageHeader
        icon={<GraduationCap size={30} strokeWidth={2.3} />}
        title={t("title")}
        subtitle={t("subtitle")}
      />

      <section className="learner-dashboard-page__section">
        <div className="learner-dashboard-page__section-heading">
          <span className="learner-dashboard-page__section-icon">
            <BookOpen size={24} strokeWidth={2.2} />
          </span>

          <div>
            <h2>{t("sections.learningStatistics")}</h2>
            <p>{t("sections.learningStatisticsDescription")}</p>
          </div>
        </div>

        <div className="learner-dashboard-page__metrics">
          <DashboardMetricCard
            icon={<BookOpen size={22} strokeWidth={2.2} />}
            label={t("metrics.coursesEnrolled")}
            value={statistics.courses_enroll}
          />

          <DashboardMetricCard
            icon={<Hourglass size={22} strokeWidth={2.2} />}
            label={t("metrics.coursesInProgress")}
            value={statistics.courses_inprogress}
          />

          <DashboardMetricCard
            icon={<CheckCircle2 size={22} strokeWidth={2.2} />}
            label={t("metrics.coursesCompleted")}
            value={statistics.courses_completed}
          />

          <DashboardMetricCard
            icon={<Trophy size={22} strokeWidth={2.2} />}
            label={t("metrics.examsPassed")}
            value={statistics.exams_passed}
          />

          <DashboardMetricCard
            icon={<XCircle size={22} strokeWidth={2.2} />}
            label={t("metrics.examsFailed")}
            value={statistics.exams_failed}
          />

          <DashboardMetricCard
            icon={<Clock3 size={22} strokeWidth={2.2} />}
            label={t("metrics.examsInProgress")}
            value={statistics.exams_inprogress}
          />

          <DashboardMetricCard
            icon={<Bot size={22} strokeWidth={2.2} />}
            label={t("metrics.questionsAsked")}
            value={statistics.questions_asked}
          />

          <DashboardMetricCard
            icon={<FileText size={22} strokeWidth={2.2} />}
            label={t("metrics.documentsUploaded")}
            value={statistics.documents_uploaded}
          />

          <DashboardMetricCard
            icon={<Clock3 size={22} strokeWidth={2.2} />}
            label={t("metrics.lastActivity")}
            value={formatDateTime(statistics.last_activity)}
          />
        </div>
      </section>

      <section className="learner-dashboard-page__section">
        <div className="learner-dashboard-page__progress-header">
          <div>
            <h2>{t("sections.courseProgress")}</h2>
            <p>{t("sections.courseProgressDescription")}</p>
          </div>

          <strong>{progressPercent}%</strong>
        </div>

        <div
          className="learner-dashboard-page__progress"
          role="progressbar"
          aria-valuenow={progressPercent}
          aria-valuemin={0}
          aria-valuemax={100}
          aria-label={t("sections.courseProgress")}
        >
          <span style={{ width: `${progressPercent}%` }} />
        </div>
      </section>
    </section>
  );
}
