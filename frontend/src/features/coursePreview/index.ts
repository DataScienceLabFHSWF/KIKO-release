// frontend/src/features/coursePreview/index.ts

export { CoursePreview } from "./components/CoursePreview";
export { CoursePreviewHeader } from "./components/CoursePreviewHeader";
export { CoursePreviewStats } from "./components/CoursePreviewStats";
export { CoursePreviewCurriculum } from "./components/CoursePreviewCurriculum";
export { CoursePreviewContent } from "./components/CoursePreviewContent";
export { CoursePreviewTabs } from "./components/CoursePreviewTabs";

export { createCoursePreviewFromCourseJson } from "./adapters/courseJsonPreviewAdapter";
export { createCoursePreviewFromLearnerCourse } from "./adapters/learnerCoursePreviewAdapter";

export type {
  CoursePreviewCourse,
  CoursePreviewModule,
  CoursePreviewModuleTabKey,
  CoursePreviewSectionKey,
  CoursePreviewTab,
} from "./types/CoursePreview";
