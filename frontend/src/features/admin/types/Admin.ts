// frontend/src/features/admin/types/Admin.ts

export type AdminStatistics = {
  users_registered: number;
  learners_registered: number;
  instructors_registered: number;
  admins_registered: number;
  documents_uploaded: number;
  courses_created: number;
  chat_questions: number;
  pipelines_status: string;
  system_uptime: string;
  last_activity: string;
};
