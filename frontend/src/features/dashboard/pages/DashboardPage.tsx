// frontend/src/features/dashboard/pages/DashboardPage.tsx

import { useTranslation } from "node_modules/react-i18next";
import { useAuth } from "@/app/providers/AuthProvider";
import { LoadingState } from "@/components";
import { LearnerDashboardPage } from "@/features/learner/pages/LearnerDashboardPage";
import { InstructorDashboardPage } from "@/features/instructor/pages/InstructorDashboardPage";
import { AdminDashboardPage } from "@/features/admin/pages/AdminDashboardPage";

export function DashboardPage() {
  const { t } = useTranslation("common");
  const { user, isLoading } = useAuth();

  if (isLoading) {
    return <LoadingState description={t("loading")} />;
  }

  if (user?.role === "Admin") {
    return <AdminDashboardPage />;
  }

  if (user?.role === "Instructor") {
    return <InstructorDashboardPage />;
  }

  return <LearnerDashboardPage />;
}
