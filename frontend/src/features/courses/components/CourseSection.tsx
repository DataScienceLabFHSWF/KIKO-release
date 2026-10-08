// frontend/src/features/courses/components/CourseSection.tsx

import type { ReactNode } from "react";
import "./CourseSection.css";

type CourseSectionProps = {
  title: string;
  description?: string;
  icon?: ReactNode;
  children: ReactNode;
};

export function CourseSection({
  title,
  description,
  icon,
  children,
}: CourseSectionProps) {
  return (
    <section className="course-section">
      <div className="course-section__header">
        {icon && <span className="course-section__icon">{icon}</span>}

        <div>
          <h2>{title}</h2>
          {description && <p>{description}</p>}
        </div>
      </div>

      <div className="course-section__content">{children}</div>
    </section>
  );
}
