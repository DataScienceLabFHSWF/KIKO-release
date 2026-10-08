// frontend/src/features/faq/components/FaqQuickLinks.tsx

import { Link } from "react-router-dom";
import { Link2 } from "lucide-react";
import { useTranslation } from "node_modules/react-i18next";
import type { UserRole } from "@/api/types/auth";
import { faqQuickLinks } from "../data/FaqConfig";
import "./FaqQuickLinks.css";

type FaqQuickLinksProps = {
  role: UserRole;
};

export function FaqQuickLinks({ role }: FaqQuickLinksProps) {
  const { t } = useTranslation("faq");

  const visibleLinks = faqQuickLinks.filter((item) =>
    item.roles.includes(role),
  );

  return (
    <section className="faq-quick-links">
      <h2>
        <Link2 size={28} strokeWidth={2.2} aria-hidden="true" />
        {t("quickLinks.title")}
      </h2>

      <div className="faq-quick-links__grid">
        {visibleLinks.map((item) => (
          <Link key={item.to} to={item.to} className="faq-quick-links__item">
            <item.icon size={17} strokeWidth={2.2} aria-hidden="true" />
            <span>{t(`quickLinks.items.${item.key}`)}</span>
          </Link>
        ))}
      </div>
    </section>
  );
}
