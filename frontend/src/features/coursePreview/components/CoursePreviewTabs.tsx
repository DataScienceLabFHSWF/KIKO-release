// frontend/src/features/coursePreview/components/CoursePreviewTabs.tsx

import clsx from "clsx";
import { Button } from "@/components";
import type { CoursePreviewTab } from "../types/CoursePreview";

type CoursePreviewTabsProps<T extends string> = {
  tabs: Array<CoursePreviewTab & { key: T }>;
  activeKey: T;
  ariaLabel: string;
  onChange: (key: T) => void;
};

export function CoursePreviewTabs<T extends string>({
  tabs,
  activeKey,
  ariaLabel,
  onChange,
}: CoursePreviewTabsProps<T>) {
  return (
    <nav className="course-preview-tabs" aria-label={ariaLabel}>
      {tabs.map((tab) => (
        <Button
          key={tab.key}
          type="button"
          variant="plain"
          className={clsx("course-preview-tabs__item", {
            "course-preview-tabs__item--active": activeKey === tab.key,
          })}
          disabled={tab.disabled}
          onClick={() => onChange(tab.key)}
        >
          {tab.icon}
          <span>{tab.label}</span>
        </Button>
      ))}
    </nav>
  );
}
