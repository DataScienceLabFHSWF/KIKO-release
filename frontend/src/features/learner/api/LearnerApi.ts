// frontend/src/features/learner/api/LearnerApi.ts

import { apiRequest } from "@/api/client";
import type { LearnerStatistics } from "../types/Learner";

export function getLearnerStatistics() {
  return apiRequest<LearnerStatistics>("/learner/statistics");
}
