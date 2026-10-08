// frontend/src/features/mediaManager/components/CourseSelector.tsx

import { BookOpen } from "lucide-react";
import { useTranslation } from "node_modules/react-i18next";
import type { InstructorCourseSummary } from "../types/MediaManager";

type CourseSelectorProps = {
  courses: InstructorCourseSummary[];
  selectedCourseId: number | null;
  disabled?: boolean;
  onChange: (courseId: number) => void;
};

export function CourseSelector({
  courses,
  selectedCourseId,
  disabled = false,
  onChange,
}: CourseSelectorProps) {
  const { t } = useTranslation("mediaManager");

  return (
    <section className="media-manager-card">
      <div className="media-manager-card__header">
        <BookOpen size={24} strokeWidth={2.2} />
        <div>
          <h2>{t("courseSelector.title")}</h2>
          <p>{t("courseSelector.subtitle")}</p>
        </div>
      </div>

      <label className="media-manager-field">
        <span>{t("courseSelector.label")}</span>

        <select
          value={selectedCourseId ?? ""}
          disabled={disabled || courses.length === 0}
          onChange={(event) => onChange(Number(event.currentTarget.value))}
        >
          {courses.map((course) => (
            <option key={course.course_id} value={course.course_id}>
              {course.title}
            </option>
          ))}
        </select>
      </label>
    </section>
  );
}
