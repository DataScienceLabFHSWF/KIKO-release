// frontend/src/features/dashboard/pages/PlaceholderPage.tsx

import { useTranslation } from "node_modules/react-i18next";
import { EmptyState } from "@/components";

type PlaceholderPageProps = {
  title: string;
  description?: string;
};

export function PlaceholderPage({ title, description }: PlaceholderPageProps) {
  const { t } = useTranslation("common");

  return <EmptyState title={title} description={t("placeholderpage")} />;
}
