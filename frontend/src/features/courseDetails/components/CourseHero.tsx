// frontend/src/features/courseDetails/components/CourseHero.tsx

import "./CourseDetailsComponents.css";

type CourseHeroProps = {
  provider: string;
  title: string;
  level: string;
  language: string;
  duration: string;
  moduleCount: number;
  resourceCount: number;
  progressPercent: number;
};

export function CourseHero({
  provider,
  title,
  level,
  language,
  duration,
  moduleCount,
  resourceCount,
  progressPercent,
}: CourseHeroProps) {
  return (
    <section className="course-hero">
      <p className="course-hero__provider">{provider}</p>
      <h1>{title}</h1>
      <p className="course-hero__meta">
        {level} · {language} · {duration}
      </p>
      <p className="course-hero__meta">
        {moduleCount} modules · {resourceCount} resources · {progressPercent}%
        progress
      </p>
    </section>
  );
}
