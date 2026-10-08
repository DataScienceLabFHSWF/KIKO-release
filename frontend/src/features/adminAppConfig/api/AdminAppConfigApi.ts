// frontend/src/features/adminAppConfig/api/adminAppConfigApi.ts

import { apiRequest } from "@/api/client";
import type {
  AppConfigResponse,
  AppConfigUpdateRequest,
  EditableAppConfig,
} from "../types/AdminAppConfig";

export const adminAppConfigQueryKeys = {
  all: ["admin-app-config"] as const,
  appConfig: ["admin-app-config", "app-config"] as const,
};

export async function getAdminAppConfig(): Promise<AppConfigResponse> {
  return apiRequest<AppConfigResponse>("/app_configurations/app_config");
}

/**
 * Backend dependency:
 * Add PUT /api/app_configurations/app_config for this to persist.
 */
export async function updateAdminAppConfig(
  appConfig: EditableAppConfig,
): Promise<AppConfigResponse> {
  const payload: AppConfigUpdateRequest = {
    app_config: appConfig,
  };

  return apiRequest<AppConfigResponse>("/app_configurations/app_config", {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}
