// frontend/src/features/admin/api/AdminApi.ts

import { apiRequest } from "@/api/client";
import type { AdminStatistics } from "../types/Admin";

export function getAdminStatistics() {
  return apiRequest<AdminStatistics>("/admin/statistics");
}
