// frontend/src/features/adminAppConfig/components/AdminAppConfigSection.tsx

import type { ReactNode } from "react";
import "./AdminAppConfigSection.css";

type AdminAppConfigSectionProps = {
  title: string;
  description?: string;
  icon?: ReactNode;
  children: ReactNode;
};

export function AdminAppConfigSection({
  title,
  description,
  icon,
  children,
}: AdminAppConfigSectionProps) {
  return (
    <section className="admin-app-config-section">
      <header className="admin-app-config-section__header">
        {icon && (
          <span className="admin-app-config-section__icon" aria-hidden="true">
            {icon}
          </span>
        )}

        <div>
          <h2>{title}</h2>
          {description && <p>{description}</p>}
        </div>
      </header>

      <div className="admin-app-config-section__body">{children}</div>
    </section>
  );
}
