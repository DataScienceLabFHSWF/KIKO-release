// frontend/src/components/molecules/DashboardQuickAction/DashboardQuickAction.tsx

import { Link } from "react-router-dom";
import type { ReactNode } from "react";
import "./DashboardQuickAction.css";

type DashboardQuickActionProps = {
  to: string;
  icon: ReactNode;
  title: string;
  description: string;
};

export function DashboardQuickAction({
  to,
  icon,
  title,
  description,
}: DashboardQuickActionProps) {
  return (
    <Link to={to} className="dashboard-quick-action">
      <span className="dashboard-quick-action__icon" aria-hidden="true">
        {icon}
      </span>

      <span>
        <strong>{title}</strong>
        <small>{description}</small>
      </span>
    </Link>
  );
}
