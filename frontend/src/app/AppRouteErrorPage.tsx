// frontend/src/app/AppRouteErrorPage.tsx

import { isRouteErrorResponse, useRouteError } from "react-router-dom";
import { ErrorState } from "@/components";

export function AppRouteErrorPage() {
  const error = useRouteError();

  const description = isRouteErrorResponse(error)
    ? error.statusText
    : error instanceof Error
      ? error.message
      : "Something went wrong.";

  return (
    <main style={{ padding: 32 }}>
      <ErrorState
        title="Something went wrong"
        description={description}
        actionLabel="Go to dashboard"
        onAction={() => {
          window.location.href = "/dashboard";
        }}
      />
    </main>
  );
}
