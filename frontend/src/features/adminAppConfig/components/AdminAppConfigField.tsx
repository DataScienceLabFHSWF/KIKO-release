// frontend/src/features/adminAppConfig/components/AdminAppConfigField.tsx

import type { ReactNode } from "react";
import "./AdminAppConfigField.css";

type AdminAppConfigFieldProps = {
  label: string;
  description?: string;
  children: ReactNode;
};

export function AdminAppConfigField({
  label,
  description,
  children,
}: AdminAppConfigFieldProps) {
  return (
    <label className="admin-app-config-field">
      <span className="admin-app-config-field__label">{label}</span>
      {description && (
        <span className="admin-app-config-field__description">
          {description}
        </span>
      )}
      {children}
    </label>
  );
}
