// frontend/src/components/molecules/LoadingState/LoadingState.tsx

import { Spinner } from "../../atoms";
import "./LoadingState.css";

type LoadingStateProps = {
  title?: string;
  description?: string;
};

export function LoadingState({
  title = "Loading",
  description,
}: LoadingStateProps) {
  return (
    <div className="loading-state" role="status" aria-live="polite">
      <Spinner />
      <div>
        <h2>{title}</h2>
        {description && <p>{description}</p>}
      </div>
    </div>
  );
}
