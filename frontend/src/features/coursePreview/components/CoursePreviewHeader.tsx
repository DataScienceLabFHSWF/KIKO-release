// frontend/src/features/coursePreview/components/CoursePreviewHeader.tsx

import type { CoursePreviewCourse } from "../types/CoursePreview";

type CoursePreviewHeaderProps = {
  course: CoursePreviewCourse;
};

export function CoursePreviewHeader({ course }: CoursePreviewHeaderProps) {
  return (
    <section className="course-preview-header">
      <p className="course-preview-header__provider">{course.provider}</p>

      <h1>{course.title}</h1>

      <p className="course-preview-header__meta">
        {course.difficulty} · {course.language} · {course.duration}
      </p>

      <p className="course-preview-header__meta">
        {course.modules.length} modules · {course.resources.length} resources ·{" "}
        {course.progressPercent}% progress
      </p>
    </section>
  );
}
