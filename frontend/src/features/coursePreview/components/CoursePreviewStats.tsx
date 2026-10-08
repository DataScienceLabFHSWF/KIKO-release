// frontend/src/features/coursePreview/components/CoursePreviewStats.tsx

import { useTranslation } from "node_modules/react-i18next";
import type { CoursePreviewCourse } from "../types/CoursePreview";

type CoursePreviewStatsProps = {
  course: CoursePreviewCourse;
};

export function CoursePreviewStats({ course }: CoursePreviewStatsProps) {
  const { t } = useTranslation("coursePreview");

  return (
    <section className="course-preview-stats" aria-label="Course summary">
      <article>
        <span>{t("infoGrid.difficulty")}</span>
        <strong>{course.difficulty}</strong>
      </article>

      <article>
        <span>{t("infoGrid.duration")}</span>
        <strong>{course.duration}</strong>
      </article>

      <article>
        <span>{t("infoGrid.modules")}</span>
        <strong>{course.modules.length}</strong>
      </article>

      <article>
        <span>{t("infoGrid.courseProgress")}</span>
        <strong>{course.progressPercent}%</strong>
      </article>
    </section>
  );
}
