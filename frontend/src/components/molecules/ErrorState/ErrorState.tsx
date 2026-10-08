// frontend/src/components/molecules/ErrorState/ErrorState.tsx

import { Button } from "../../atoms";
import "./ErrorState.css";

type ErrorStateProps = {
  title?: string;
  description?: string;
  actionLabel?: string;
  onAction?: () => void;
};

export function ErrorState({
  title = "Something went wrong",
  description,
  actionLabel,
  onAction,
}: ErrorStateProps) {
  return (
    <div className="error-state" role="alert">
      <h2>{title}</h2>
      {description && <p>{description}</p>}
      {actionLabel && onAction && (
        <Button type="button" variant="ghost" onClick={onAction}>
          {actionLabel}
        </Button>
      )}
    </div>
  );
}
