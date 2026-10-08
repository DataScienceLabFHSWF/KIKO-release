// frontend/src/components/atoms/ReadOnlyField/ReadOnlyField.tsx

import type { ReactNode } from "react";
import { LockKeyhole } from "lucide-react";
import "./ReadOnlyField.css";

type ReadOnlyFieldProps = {
  label: string;
  value: ReactNode;
  helperText?: string;
};

export function ReadOnlyField({
  label,
  value,
  helperText,
}: ReadOnlyFieldProps) {
  return (
    <div className="read-only-field">
      <div className="read-only-field__label">
        <span>{label}</span>
        <LockKeyhole size={14} strokeWidth={2.2} aria-hidden="true" />
      </div>

      <div className="read-only-field__value">{value}</div>

      {helperText && <p className="read-only-field__helper">{helperText}</p>}
    </div>
  );
}
