// frontend/src/components/molecules/PageHeader/PageHeader.tsx

import type { ReactNode } from "react";
import "./PageHeader.css";

type PageHeaderProps = {
  icon?: ReactNode;
  title: string;
  subtitle?: string;
  action?: ReactNode;
};

export function PageHeader({ icon, title, subtitle, action }: PageHeaderProps) {
  return (
    <header className="page-header">
      <div className="page-header__main">
        <div className="page-header__title-row">
          {icon && <span className="page-header__icon">{icon}</span>}
          <div className="page-header__text">
            <h1>{title}</h1>
            {subtitle && <p>{subtitle}</p>}
          </div>
        </div>

        {action && <div className="page-header__action">{action}</div>}
      </div>
    </header>
  );
}
