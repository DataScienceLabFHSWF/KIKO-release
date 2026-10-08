// frontend/src/features/faq/pages/FaqPage.tsx

import {
  CircleHelp,
  GraduationCap,
  Info,
  LifeBuoy,
  ShieldCheck,
  UserCog,
} from "lucide-react";
import { useTranslation } from "node_modules/react-i18next";
import { useAuth } from "@/app/providers/AuthProvider";
import { usePageMeta } from "@/app/hooks/usePageMeta";
import { PageHeader } from "@/components";
import type { UserRole } from "@/api/types/auth";
import { commonFaqItems, getRoleFaqItems } from "../data/FaqConfig";
import { FaqQuickLinks } from "../components/FaqQuickLinks";
import { FaqSection } from "../components/FaqSection";
import "./FaqPage.css";

function getRoleIcon(role: UserRole) {
  if (role === "Admin") {
    return <ShieldCheck size={24} strokeWidth={2.2} />;
  }

  if (role === "Instructor") {
    return <UserCog size={24} strokeWidth={2.2} />;
  }

  return <GraduationCap size={24} strokeWidth={2.2} />;
}

function getRoleSectionKey(role: UserRole) {
  if (role === "Admin") return "admin";
  if (role === "Instructor") return "instructor";
  return "learner";
}

export function FaqPage() {
  const { t } = useTranslation("faq");
  const { user } = useAuth();

  const role = (user?.role ?? "Learner") as UserRole;
  const roleSectionKey = getRoleSectionKey(role);

  usePageMeta({
    title: t("title"),
  });

  return (
    <section className="faq-page">
      <PageHeader
        icon={<CircleHelp size={30} strokeWidth={2.4} />}
        title={t("title")}
        subtitle={t("subtitle", {
          name: user?.full_name ?? t("userFallback"),
          role: t(`roles.${role}`),
        })}
      />

      <FaqQuickLinks role={role} />

      <FaqSection
        title={t(`sections.${roleSectionKey}`)}
        icon={getRoleIcon(role)}
        items={getRoleFaqItems(role)}
      />

      <FaqSection
        title={t("sections.common")}
        icon={<LifeBuoy size={24} strokeWidth={2.2} />}
        items={commonFaqItems}
      />

      <aside className="faq-page__support">
        <Info size={17} strokeWidth={2.2} aria-hidden="true" />
        <span>
          {t("support.prefix")}{" "}
          <a href="mailto:kiko.support@fh-swf.de">kiko.support@fh-swf.de</a>
        </span>
      </aside>
    </section>
  );
}
