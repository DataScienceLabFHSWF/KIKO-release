// frontend/src/features/coursePreview/components/CoursePreviewCurriculum.tsx

import {
  BookOpen,
  ClipboardCheck,
  FileText,
  GraduationCap,
  Info,
  LockKeyhole,
} from "lucide-react";
import { useTranslation } from "node_modules/react-i18next";
import clsx from "clsx";
import { Button } from "@/components";
import type {
  CoursePreviewCourse,
  CoursePreviewSectionKey,
} from "../types/CoursePreview";

type CoursePreviewCurriculumProps = {
  course: CoursePreviewCourse;
  activeKey: CoursePreviewSectionKey;
  onSelect: (key: CoursePreviewSectionKey) => void;
};

export function CoursePreviewCurriculum({
  course,
  activeKey,
  onSelect,
}: CoursePreviewCurriculumProps) {
  const { t } = useTranslation("coursePreview");
  const isLocked = course.isEnrolled === false;

  const items: Array<{
    key: CoursePreviewSectionKey;
    label: string;
    locked?: boolean;
    icon: React.ReactNode;
  }> = [
    {
      key: "overview",
      label: t("curriculum.overview"),
      icon: <BookOpen size={15} strokeWidth={2.2} />,
    },
    {
      key: "course-info",
      label: t("curriculum.courseInfo"),
      icon: <Info size={15} strokeWidth={2.2} />,
    },
    ...course.modules.map((module, index) => ({
      key: `module:${module.id}` as CoursePreviewSectionKey,
      label: t("curriculum.module", {
        index: index + 1,
        title: module.title,
      }),
      locked: isLocked,
      icon: isLocked ? (
        <LockKeyhole size={15} strokeWidth={2.2} />
      ) : (
        <BookOpen size={15} strokeWidth={2.2} />
      ),
    })),
    ...(course.finalQuiz
      ? [
          {
            key: "final-quiz" as CoursePreviewSectionKey,
            label: t("curriculum.finalQuiz"),
            locked: isLocked,
            icon: isLocked ? (
              <LockKeyhole size={15} strokeWidth={2.2} />
            ) : (
              <FileText size={15} strokeWidth={2.2} />
            ),
          },
        ]
      : []),
    {
      key: "grades",
      label: t("curriculum.grades"),
      locked: isLocked,
      icon: isLocked ? (
        <LockKeyhole size={15} strokeWidth={2.2} />
      ) : (
        <GraduationCap size={15} strokeWidth={2.2} />
      ),
    },
    {
      key: "resources",
      label: t("curriculum.resources"),
      icon: <ClipboardCheck size={15} strokeWidth={2.2} />,
    },
  ];

  return (
    <aside
      className="course-preview-curriculum"
      aria-label={t("curriculum.title")}
    >
      <h2>{t("curriculum.title")}</h2>

      <div className="course-preview-curriculum__items">
        {items.map((item) => (
          <Button
            key={item.key}
            type="button"
            variant="plain"
            disabled={item.locked}
            className={clsx("course-preview-curriculum__item", {
              "course-preview-curriculum__item--active": activeKey === item.key,
              "course-preview-curriculum__item--locked": item.locked,
            })}
            onClick={() => onSelect(item.key)}
          >
            {item.icon}
            <span>{item.label}</span>
          </Button>
        ))}
      </div>
    </aside>
  );
}
