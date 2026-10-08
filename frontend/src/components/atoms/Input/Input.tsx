// frontend/src/components/atoms/Input/Input.tsx

import type { InputHTMLAttributes } from "react";
import "./Input.css";

type InputProps = InputHTMLAttributes<HTMLInputElement> & {
  label: string;
};

export function Input({ label, id, ...props }: InputProps) {
  const inputId = id ?? label.toLowerCase().replaceAll(" ", "-");

  return (
    <label className="ui-input" htmlFor={inputId}>
      <span>{label}</span>
      <input id={inputId} {...props} />
    </label>
  );
}
