// frontend/src/features/courseDetails/components/CourseModuleTabs.tsx

import clsx from "clsx";
import {
  BookOpen,
  Hammer,
  Library,
  FilePenLine,
  TriangleAlert,
} from "lucide-react";
import { useTranslation } from "node_modules/react-i18next";
import { Button } from "@/components";
import type { CourseModuleTabKey } from "../types/LearnerCourseDetails";
import "./CourseModuleTabs.css";

type CourseModuleTabsProps = {
  activeTab: CourseModuleTabKey;
  onChange: (tab: CourseModuleTabKey) => void;
};

const tabs: Array<{
  key: CourseModuleTabKey;
  icon: typeof BookOpen;
  labelKey: string;
}> = [
  { key: "content", icon: BookOpen, labelKey: "tabs.content" },
  { key: "practice", icon: Hammer, labelKey: "tabs.practice" },
  { key: "quiz", icon: FilePenLine, labelKey: "tabs.quiz" },
  { key: "further-reading", icon: Library, labelKey: "tabs.furtherReading" },
  {
    key: "misconceptions",
    icon: TriangleAlert,
    labelKey: "tabs.misconceptions",
  },
];

export function CourseModuleTabs({
  activeTab,
  onChange,
}: CourseModuleTabsProps) {
  const { t } = useTranslation("courseDetails");

  return (
    <div className="course-module-tabs" role="tablist">
      {tabs.map((tab) => {
        const Icon = tab.icon;
        const isActive = activeTab === tab.key;

        return (
          <Button
            key={tab.key}
            type="button"
            variant="plain"
            role="tab"
            aria-selected={isActive}
            className={clsx("course-module-tabs__button", {
              "course-module-tabs__button--active": isActive,
            })}
            onClick={() => onChange(tab.key)}
          >
            <Icon size={16} strokeWidth={2.2} />
            <span>{t(tab.labelKey)}</span>
          </Button>
        );
      })}
    </div>
  );
}
