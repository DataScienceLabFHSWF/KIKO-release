// frontend/src/features/admin/pages/AdminDashboardPage.tsx

import {
  BookOpen,
  ClipboardCheck,
  FileText,
  Gauge,
  MessageSquareText,
  SearchCheck,
  Settings,
  ShieldCheck,
  UsersRound,
  UserCog,
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
import { getAdminStatistics } from "../api/AdminApi";
import type { AdminStatistics } from "../types/Admin";
import "./AdminDashboardPage.css";

function formatDateTime(value: string) {
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

export function AdminDashboardPage() {
  const { t } = useTranslation("adminDashboard");

  const [statistics, setStatistics] = useState<AdminStatistics | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  usePageMeta({ title: t("metaTitle") });

  async function loadStatistics() {
    setIsLoading(true);
    setError(null);

    try {
      const response = await getAdminStatistics();
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
    <section className="admin-dashboard-page">
      <PageHeader
        icon={<ShieldCheck size={30} strokeWidth={2.3} />}
        title={t("title")}
        subtitle={t("subtitle")}
      />

      <section className="admin-dashboard-page__section">
        <div>
          <h2>{t("sections.systemOverview")}</h2>
          <p>{t("sections.systemOverviewDescription")}</p>
        </div>

        <div className="admin-dashboard-page__metrics">
          <DashboardMetricCard
            icon={<UsersRound size={22} strokeWidth={2.2} />}
            label={t("metrics.usersRegistered")}
            value={statistics.users_registered}
          />

          <DashboardMetricCard
            icon={<UsersRound size={22} strokeWidth={2.2} />}
            label={t("metrics.learnersRegistered")}
            value={statistics.learners_registered}
          />

          <DashboardMetricCard
            icon={<UserCog size={22} strokeWidth={2.2} />}
            label={t("metrics.instructorsRegistered")}
            value={statistics.instructors_registered}
          />

          <DashboardMetricCard
            icon={<ShieldCheck size={22} strokeWidth={2.2} />}
            label={t("metrics.adminsRegistered")}
            value={statistics.admins_registered}
          />

          <DashboardMetricCard
            icon={<BookOpen size={22} strokeWidth={2.2} />}
            label={t("metrics.coursesCreated")}
            value={statistics.courses_created}
          />

          <DashboardMetricCard
            icon={<FileText size={22} strokeWidth={2.2} />}
            label={t("metrics.documentsUploaded")}
            value={statistics.documents_uploaded}
          />

          <DashboardMetricCard
            icon={<MessageSquareText size={22} strokeWidth={2.2} />}
            label={t("metrics.chatQuestions")}
            value={statistics.chat_questions}
          />

          <DashboardMetricCard
            icon={<Gauge size={22} strokeWidth={2.2} />}
            label={t("metrics.pipelineStatus")}
            value={statistics.pipelines_status}
          />

          <DashboardMetricCard
            icon={<Clock3 size={22} strokeWidth={2.2} />}
            label={t("metrics.lastActivity")}
            value={formatDateTime(statistics.last_activity)}
          />
        </div>
      </section>

      <section className="admin-dashboard-page__section">
        <div>
          <h2>{t("sections.adminActions")}</h2>
          <p>{t("sections.adminActionsDescription")}</p>
        </div>

        <div className="admin-dashboard-page__actions">
          <DashboardQuickAction
            to="/admin-console"
            icon={<Settings size={22} strokeWidth={2.2} />}
            title={t("actionsGrid.adminConsole.title")}
            description={t("actionsGrid.adminConsole.description")}
          />

          <DashboardQuickAction
            to="/knowledge-check-config"
            icon={<ClipboardCheck size={22} strokeWidth={2.2} />}
            title={t("actionsGrid.knowledgeCheck.title")}
            description={t("actionsGrid.knowledgeCheck.description")}
          />

          <DashboardQuickAction
            to="/documents"
            icon={<FileText size={22} strokeWidth={2.2} />}
            title={t("actionsGrid.documents.title")}
            description={t("actionsGrid.documents.description")}
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
