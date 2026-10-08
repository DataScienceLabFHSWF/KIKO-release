// frontend/src/components/molecules/StatCard/StatCard.tsx

import type { ReactNode } from "react";
import "./StatCard.css";

type StatCardProps = {
  label: string;
  value: ReactNode;
  helperText?: string;
};

export function StatCard({ label, value, helperText }: StatCardProps) {
  return (
    <article className="stat-card">
      <span className="stat-card__label">{label}</span>
      <strong className="stat-card__value">{value}</strong>
      {helperText && <p>{helperText}</p>}
    </article>
  );
}
