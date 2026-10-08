// frontend/src/components/atoms/Spinner/Spinner.tsx

import "./Spinner.css";

type SpinnerProps = {
  size?: "sm" | "md" | "lg";
};

export function Spinner({ size = "md" }: SpinnerProps) {
  return (
    <span className={`ui-spinner ui-spinner--${size}`} aria-hidden="true" />
  );
}
