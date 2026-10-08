// frontend/src/features/courseDetails/components/CourseCurriculum.tsx

import {
  BookOpen,
  ClipboardCheck,
  FileText,
  GraduationCap,
  Info,
  LockKeyhole,
} from "lucide-react";
import clsx from "clsx";
import { Button } from "@/components";
import type { NormalizedCourseModule } from "../types/LearnerCourseDetails";
import "./CourseDetailsComponents.css";

type CurriculumItem = {
  key: string;
  label: string;
  locked?: boolean;
};

type CourseCurriculumProps = {
  modules: NormalizedCourseModule[];
  activeKey: string;
  isEnrolled: boolean;
  hasFinalQuiz: boolean;
  onSelect: (key: string) => void;
};

export function CourseCurriculum({
  modules,
  activeKey,
  isEnrolled,
  hasFinalQuiz,
  onSelect,
}: CourseCurriculumProps) {
  const items: CurriculumItem[] = [
    { key: "overview", label: "Overview" },
    { key: "course-info", label: "Course information" },
    ...modules.map((module, index) => ({
      key: `module:${module.id}`,
      label: `Module ${index + 1}: ${module.title}`,
      locked: !isEnrolled,
    })),
    {
      key: "final-quiz",
      label: "Final assessment",
      locked: !isEnrolled || !hasFinalQuiz,
    },
    { key: "grades", label: "Grades", locked: !isEnrolled },
    { key: "resources", label: "Resources" },
  ];

  function renderIcon(item: CurriculumItem) {
    if (item.locked) return <LockKeyhole size={14} />;
    if (item.key === "overview") return <BookOpen size={14} />;
    if (item.key === "course-info") return <Info size={14} />;
    if (item.key === "final-quiz") return <FileText size={14} />;
    if (item.key === "grades") return <GraduationCap size={14} />;
    if (item.key === "resources") return <ClipboardCheck size={14} />;
    return <BookOpen size={14} />;
  }

  return (
    <aside className="course-curriculum" aria-label="Course curriculum">
      <h2>Curriculum</h2>

      <div className="course-curriculum__items">
        {items.map((item) => (
          <Button
            key={item.key}
            type="button"
            variant="plain"
            className={clsx("course-curriculum__item", {
              "course-curriculum__item--active": activeKey === item.key,
              "course-curriculum__item--locked": item.locked,
            })}
            disabled={item.locked}
            onClick={() => onSelect(item.key)}
          >
            {renderIcon(item)}
            <span>{item.label}</span>
          </Button>
        ))}
      </div>
    </aside>
  );
}
