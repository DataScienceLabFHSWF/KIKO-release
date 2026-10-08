// frontend/src/components/templates/AuthLayout/AuthLayout.tsx

import type { ReactNode } from "react";
import { LanguageSwitch } from "../../molecules";
import { BrandLogo } from "../../atoms";
import "./AuthLayout.css";

type AuthLayoutProps = {
  title: string;
  titleIcon?: ReactNode;
  children: ReactNode;
  footer?: ReactNode;
};

export function AuthLayout({
  title,
  titleIcon,
  children,
  footer,
}: AuthLayoutProps) {
  return (
    <main className="auth-page">
      <div className="auth-page__language">
        <LanguageSwitch />
      </div>

      <section className="auth-card">
        <div className="auth-card__brand">
          <BrandLogo variant="auth" />
        </div>

        <h1 className="auth-card__title">
          {titleIcon && (
            <span className="auth-card__title-icon">{titleIcon}</span>
          )}
          <span>{title}</span>
        </h1>

        {children}

        {footer && <div className="auth-card__footer">{footer}</div>}
      </section>
    </main>
  );
}
