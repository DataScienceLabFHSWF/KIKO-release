// frontend/src/components/atoms/Badge/Badge.tsx

import clsx from "clsx";
import "./Badge.css";

type BadgeVariant = "default" | "success" | "warning" | "danger" | "info";

type BadgeProps = {
  children: React.ReactNode;
  variant?: BadgeVariant;
};

export function Badge({ children, variant = "default" }: BadgeProps) {
  return (
    <span className={clsx("ui-badge", `ui-badge--${variant}`)}>{children}</span>
  );
}
