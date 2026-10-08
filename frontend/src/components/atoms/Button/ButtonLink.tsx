// frontend/src/components/atoms/Button/ButtonLink.tsx

import { Link, type LinkProps } from "react-router-dom";
import clsx from "clsx";
import type { ButtonSize, ButtonVariant } from "./Button";
import "./Button.css";

type ButtonLinkProps = LinkProps & {
  variant?: ButtonVariant;
  size?: ButtonSize;
  fullWidth?: boolean;
  isDisabled?: boolean;
};

export function ButtonLink({
  variant = "primary",
  size = "md",
  fullWidth = false,
  isDisabled = false,
  className,
  children,
  onClick,
  tabIndex,
  ...props
}: ButtonLinkProps) {
  return (
    <Link
      {...props}
      aria-disabled={isDisabled || undefined}
      tabIndex={isDisabled ? -1 : tabIndex}
      className={clsx(
        "ui-button",
        `ui-button--${variant}`,
        `ui-button--${size}`,
        {
          "ui-button--full-width": fullWidth,
          "ui-button--disabled": isDisabled,
        },
        className,
      )}
      onClick={(event) => {
        if (isDisabled) {
          event.preventDefault();
          event.stopPropagation();
          return;
        }

        onClick?.(event);
      }}
    >
      {children}
    </Link>
  );
}
