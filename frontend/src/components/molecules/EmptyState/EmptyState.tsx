// frontend/src/components/molecules/EmptyState/EmptyState.tsx

import { Button } from "../../atoms";
import "./EmptyState.css";

type EmptyStateProps = {
  title: string;
  description?: string;
  actionLabel?: string;
  onAction?: () => void;
};

export function EmptyState({
  title,
  description,
  actionLabel,
  onAction,
}: EmptyStateProps) {
  return (
    <section className="empty-state">
      <h2>{title}</h2>
      {description && <p>{description}</p>}
      {actionLabel && onAction && (
        <Button type="button" variant="primary" onClick={onAction}>
          {actionLabel}
        </Button>
      )}
    </section>
  );
}
