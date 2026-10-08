// frontend/src/components/molecules/FormField/FormField.tsx

import type { InputHTMLAttributes, ReactNode } from "react";
import clsx from "clsx";
import "./FormField.css";

type FormFieldProps = InputHTMLAttributes<HTMLInputElement> & {
  label: string;
  error?: string;
  icon?: ReactNode;
  layout?: "row" | "stack";
};

export function FormField({
  label,
  error,
  icon,
  id,
  required,
  layout = "row",
  className,
  ...props
}: FormFieldProps) {
  const inputId = id ?? label.toLowerCase().replaceAll(" ", "-");

  return (
    <label
      className={clsx("ui-form-field", `ui-form-field--${layout}`, className)}
      htmlFor={inputId}
    >
      <span className="ui-form-field__label">
        {label}
        {required && <span aria-hidden="true"> *</span>}
      </span>

      <span className="ui-form-field__control">
        {icon && (
          <span className="ui-form-field__icon" aria-hidden="true">
            {icon}
          </span>
        )}

        <input
          id={inputId}
          required={required}
          aria-invalid={Boolean(error)}
          aria-describedby={error ? `${inputId}-error` : undefined}
          className={clsx({ "ui-form-field__input--with-icon": Boolean(icon) })}
          {...props}
        />
      </span>

      {error && (
        <small id={`${inputId}-error`} className="ui-form-field__error">
          {error}
        </small>
      )}
    </label>
  );
}
