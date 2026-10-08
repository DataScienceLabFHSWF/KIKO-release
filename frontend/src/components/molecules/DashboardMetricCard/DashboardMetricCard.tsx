// frontend/src/components/molecules/DashboardMetricCard/DashboardMetricCard.tsx

import type { ReactNode } from "react";
import "./DashboardMetricCard.css";

type DashboardMetricCardProps = {
  icon: ReactNode;
  label: string;
  value: ReactNode;
  helperText?: string;
};

export function DashboardMetricCard({
  icon,
  label,
  value,
  helperText,
}: DashboardMetricCardProps) {
  return (
    <article className="dashboard-metric-card">
      <div className="dashboard-metric-card__icon" aria-hidden="true">
        {icon}
      </div>

      <div>
        <p className="dashboard-metric-card__label">{label}</p>
        <strong className="dashboard-metric-card__value">{value}</strong>

        {helperText && (
          <p className="dashboard-metric-card__helper">{helperText}</p>
        )}
      </div>
    </article>
  );
}
