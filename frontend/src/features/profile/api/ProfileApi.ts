// frontend/src/features/profile/api/ProfileApi.ts

import { apiRequest } from "../../../api/client";
import type {
  UserProfileResponse,
  UserProfileUpdateRequest,
} from "@/api/types/auth";

export function getCurrentUserProfile() {
  return apiRequest<UserProfileResponse>("/profile/user_info");
}

export function updateCurrentUserProfile(payload: UserProfileUpdateRequest) {
  return apiRequest<UserProfileResponse>("/profile/user_info", {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}
