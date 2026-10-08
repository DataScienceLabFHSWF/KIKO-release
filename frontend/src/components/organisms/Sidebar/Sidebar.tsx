// frontend/src/components/organisms/Sidebar/Sidebar.tsx

import { Link, NavLink } from "react-router-dom";
import { useTranslation } from "node_modules/react-i18next";
import { LogOut, ChevronRight, ChevronLeft } from "lucide-react";
import clsx from "clsx";
import { useAuth } from "@/app/providers/AuthProvider";
import { Button, IconButton } from "@/components";
import { BrandLogo } from "../../atoms";
import { sidebarNavItems } from "./sidebarConfig";
import "./Sidebar.css";

type SidebarProps = {
  isCollapsed: boolean;
  onToggle: () => void;
};

export function Sidebar({ isCollapsed, onToggle }: SidebarProps) {
  const { t } = useTranslation("sidebar");
  const { user, logout } = useAuth();

  const visibleItems = sidebarNavItems.filter((item) => {
    return user ? item.roles.includes(user.role) : false;
  });

  return (
    <aside
      className={clsx("sidebar", {
        "sidebar--collapsed": isCollapsed,
      })}
    >
      <div className="sidebar__top">
        <Link
          to="/dashboard"
          className="sidebar__brand-link"
          aria-label={t("goToDashboard")}
          title={t("goToDashboard")}
        >
          <BrandLogo variant={isCollapsed ? "compact" : "sidebar"} />
        </Link>

        <IconButton
          label={isCollapsed ? t("expand") : t("collapse")}
          icon={
            isCollapsed ? (
              <ChevronRight size={16} strokeWidth={2.4} />
            ) : (
              <ChevronLeft size={16} strokeWidth={2.4} />
            )
          }
          variant="ghost"
          size="md"
          className="sidebar__toggle"
          onClick={onToggle}
        />
      </div>

      <div className="sidebar__divider" />

      {!isCollapsed && (
        <div className="sidebar__user">
          <div>
            {t("welcome", { name: user?.full_name ?? t("userFallback") })}
          </div>
          <span>({user?.role})</span>
        </div>
      )}

      <div className="sidebar__divider" />

      <nav className="sidebar__nav" aria-label={t("navigation")}>
        {visibleItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            title={isCollapsed ? t(`nav.${item.key}`) : undefined}
            className={({ isActive }) =>
              clsx("sidebar__link", {
                "sidebar__link--active": isActive,
              })
            }
          >
            <span className="sidebar__icon" aria-hidden="true">
              <item.icon size={15} strokeWidth={2.2} />
            </span>

            {!isCollapsed && (
              <span className="sidebar__label">{t(`nav.${item.key}`)}</span>
            )}
          </NavLink>
        ))}
      </nav>

      <div className="sidebar__divider sidebar__divider--bottom" />

      <Button
        type="button"
        variant="danger"
        size="sm"
        fullWidth={!isCollapsed}
        className="sidebar__logout"
        onClick={logout}
        aria-label={t("logout")}
        title={isCollapsed ? t("logout") : undefined}
      >
        <LogOut size={15} strokeWidth={2.2} aria-hidden="true" />
        {!isCollapsed && <span>{t("logout")}</span>}
      </Button>
    </aside>
  );
}
