// frontend/src/features/instructor/pages/InstructorDashboardPage.tsx

import {
  BookOpen,
  Bot,
  FileText,
  GraduationCap,
  PenLine,
  SearchCheck,
  UsersRound,
  MessageSquareText,
  Clock3,
} from "lucide-react";
import { useEffect, useState } from "react";
import { useTranslation } from "node_modules/react-i18next";
import { usePageMeta } from "@/app/hooks/usePageMeta";
import {
  DashboardMetricCard,
  DashboardQuickAction,
  ErrorState,
  LoadingState,
  PageHeader,
} from "@/components";
import { getInstructorStatistics } from "../api/InstructorApi";
import type { InstructorStatistics } from "../types/Instructor";
import "./InstructorDashboardPage.css";

function formatDateTime(value: string) {
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

export function InstructorDashboardPage() {
  const { t } = useTranslation("instructorDashboard");

  const [statistics, setStatistics] = useState<InstructorStatistics | null>(
    null,
  );
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  usePageMeta({ title: t("metaTitle") });

  async function loadStatistics() {
    setIsLoading(true);
    setError(null);

    try {
      const response = await getInstructorStatistics();
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
    <section className="instructor-dashboard-page">
      <PageHeader
        icon={<GraduationCap size={30} strokeWidth={2.3} />}
        title={t("title")}
        subtitle={t("subtitle")}
      />

      <section className="instructor-dashboard-page__section">
        <div>
          <h2>{t("sections.overview")}</h2>
          <p>{t("sections.overviewDescription")}</p>
        </div>

        <div className="instructor-dashboard-page__metrics">
          <DashboardMetricCard
            icon={<BookOpen size={22} strokeWidth={2.2} />}
            label={t("metrics.coursesCreated")}
            value={statistics.courses_created}
          />

          <DashboardMetricCard
            icon={<UsersRound size={22} strokeWidth={2.2} />}
            label={t("metrics.students")}
            value={statistics.students}
          />

          <DashboardMetricCard
            icon={<MessageSquareText size={22} strokeWidth={2.2} />}
            label={t("metrics.learnerQuestions")}
            value={statistics.learner_questions}
          />

          <DashboardMetricCard
            icon={<PenLine size={22} strokeWidth={2.2} />}
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

      <section className="instructor-dashboard-page__section">
        <div>
          <h2>{t("sections.nextActions")}</h2>
          <p>{t("sections.nextActionsDescription")}</p>
        </div>

        <div className="instructor-dashboard-page__actions">
          <DashboardQuickAction
            to="/course-generator"
            icon={<PenLine size={22} strokeWidth={2.2} />}
            title={t("actionsGrid.courseSetup.title")}
            description={t("actionsGrid.courseSetup.description")}
          />

          <DashboardQuickAction
            to="/courses"
            icon={<BookOpen size={22} strokeWidth={2.2} />}
            title={t("actionsGrid.myCourses.title")}
            description={t("actionsGrid.myCourses.description")}
          />

          <DashboardQuickAction
            to="/documents"
            icon={<FileText size={22} strokeWidth={2.2} />}
            title={t("actionsGrid.documents.title")}
            description={t("actionsGrid.documents.description")}
          />

          <DashboardQuickAction
            to="/chat"
            icon={<Bot size={22} strokeWidth={2.2} />}
            title={t("actionsGrid.chat.title")}
            description={t("actionsGrid.chat.description")}
          />

          <DashboardQuickAction
            to="/evaluation"
            icon={<SearchCheck size={22} strokeWidth={2.2} />}
            title={t("actionsGrid.evaluation.title")}
            description={t("actionsGrid.evaluation.description")}
          />
        </div>
      </section>
    </section>
  );
}
