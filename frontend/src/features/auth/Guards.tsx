// frontend/src/features/auth/Guards.tsx

import { Navigate, Outlet, useLocation } from "react-router-dom";
import { useAuth } from "@/app/providers/AuthProvider";
import { LoadingState } from "@/components";
import type { UserRole } from "@/api/types/auth";

type RoleRouteProps = {
  roles: readonly UserRole[];
};

export function ProtectedRoute() {
  const { isAuthenticated, isLoading } = useAuth();
  const location = useLocation();

  if (isLoading) {
    return <LoadingState description="Restoring session..." />;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }

  return <Outlet />;
}

export function RoleRoute({ roles }: RoleRouteProps) {
  const { user, isAuthenticated, isLoading } = useAuth();
  const location = useLocation();

  if (isLoading) {
    return <LoadingState description="Checking permissions..." />;
  }

  if (!isAuthenticated || !user) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }

  if (!roles.includes(user.role)) {
    return (
      <Navigate to="/dashboard" replace state={{ deniedFrom: location }} />
    );
  }

  return <Outlet />;
}
