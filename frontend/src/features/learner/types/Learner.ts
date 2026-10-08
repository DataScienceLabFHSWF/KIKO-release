// frontend/src/features/learner/types/Learner.ts

export type LearnerStatistics = {
  courses_enroll: number;
  courses_completed: number;
  courses_inprogress: number;
  courses_progress_percent: number;
  exams_passed: number;
  exams_failed: number;
  exams_inprogress: number;
  questions_asked: number;
  documents_uploaded: number;
  last_activity: string;
};
