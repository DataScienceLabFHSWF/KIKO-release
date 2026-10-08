// frontend/src/components/atoms/IconButton/IconButton.tsx

import type { ButtonHTMLAttributes, ReactNode } from "react";
import clsx from "clsx";
import "./IconButton.css";

type IconButtonVariant =
  | "primary"
  | "secondary"
  | "ghost"
  | "danger"
  | "success"
  | "plain";

type IconButtonSize = "sm" | "md" | "lg";

type IconButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  label: string;
  icon: ReactNode;
  variant?: IconButtonVariant;
  size?: IconButtonSize;
};

export function IconButton({
  label,
  icon,
  variant = "ghost",
  size = "md",
  className,
  type = "button",
  ...props
}: IconButtonProps) {
  return (
    <button
      type={type}
      className={clsx(
        "ui-icon-button",
        `ui-icon-button--${variant}`,
        `ui-icon-button--${size}`,
        className,
      )}
      aria-label={label}
      title={label}
      {...props}
    >
      {icon}
    </button>
  );
}
