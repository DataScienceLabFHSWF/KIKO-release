// frontend/src/app/providers/AppProviders.tsx

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { RouterProvider } from "react-router-dom";
import { AuthProvider } from "./AuthProvider";
import { router } from "../router";
import "../../i18n/i18n";

const queryClient = new QueryClient();

export function AppProviders() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <RouterProvider router={router} />
      </AuthProvider>
    </QueryClientProvider>
  );
}
