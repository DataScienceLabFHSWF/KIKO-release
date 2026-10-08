// frontend/src/features/instructor/api/InstructorApi.ts

import { apiRequest } from "@/api/client";
import type { InstructorStatistics } from "../types/Instructor";

export function getInstructorStatistics() {
  return apiRequest<InstructorStatistics>("/instructor/statistics");
}
