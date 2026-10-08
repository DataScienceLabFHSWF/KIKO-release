// frontend/src/components/organisms/Topbar/Topbar.tsx

import { NavLink } from "react-router-dom";
import { useTranslation } from "node_modules/react-i18next";
import { UserRound } from "lucide-react";
import { LanguageSwitch } from "../../molecules";
import "./Topbar.css";

export function Topbar() {
  const { t } = useTranslation("sidebar");

  return (
    <header className="topbar">
      <LanguageSwitch />

      <NavLink
        to="/profile"
        className={({ isActive }) =>
          isActive
            ? "topbar__profile-link topbar__profile-link--active"
            : "topbar__profile-link"
        }
        aria-label={t("nav.profile")}
        title={t("nav.profile")}
      >
        <UserRound size={18} strokeWidth={2.4} aria-hidden="true" />
      </NavLink>

      <div className="topbar__mark" aria-hidden="true" />
    </header>
  );
}
