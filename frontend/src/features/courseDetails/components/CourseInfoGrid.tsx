// frontend/src/features/courseDetails/components/CourseInfoGrid.tsx

import { useTranslation } from "node_modules/react-i18next";
import "./CourseDetailsComponents.css";

type CourseInfoGridProps = {
  difficulty: string;
  duration: string;
  modules: number;
  progressPercent: number;
};

export function CourseInfoGrid({
  difficulty,
  duration,
  modules,
  progressPercent,
}: CourseInfoGridProps) {
  const { t } = useTranslation("courseDetails");
  return (
    <div className="course-info-grid">
      <article>
        <span>{t("infoGrid.difficulty")}</span>
        <strong>{difficulty}</strong>
      </article>

      <article>
        <span>{t("infoGrid.duration")}</span>
        <strong>{duration}</strong>
      </article>

      <article>
        <span>{t("infoGrid.modules")}</span>
        <strong>{modules}</strong>
      </article>

      <article>
        <span>{t("infoGrid.courseProgress")}</span>
        <strong>{progressPercent}%</strong>
      </article>
    </div>
  );
}
