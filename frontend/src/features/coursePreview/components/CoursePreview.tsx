// frontend/src/features/coursePreview/components/CoursePreview.tsx

import { useState } from "react";
import { CoursePreviewHeader } from "./CoursePreviewHeader";
import { CoursePreviewStats } from "./CoursePreviewStats";
import { CoursePreviewCurriculum } from "./CoursePreviewCurriculum";
import { CoursePreviewContent } from "./CoursePreviewContent";
import type {
  CoursePreviewCourse,
  CoursePreviewModuleTabKey,
  CoursePreviewSectionKey,
} from "../types/CoursePreview";
import "./CoursePreview.css";

type CoursePreviewRenderers = React.ComponentProps<
  typeof CoursePreviewContent
>["renderers"];

type CoursePreviewProps = {
  course: CoursePreviewCourse;
  activeSection?: CoursePreviewSectionKey;
  activeModuleTab?: CoursePreviewModuleTabKey;
  notice?: React.ReactNode;
  renderers?: CoursePreviewRenderers;
  onSectionChange?: (key: CoursePreviewSectionKey) => void;
  onModuleTabChange?: (key: CoursePreviewModuleTabKey) => void;
};

export function CoursePreview({
  course,
  activeSection,
  activeModuleTab,
  notice,
  renderers,
  onSectionChange,
  onModuleTabChange,
}: CoursePreviewProps) {
  const [internalSection, setInternalSection] =
    useState<CoursePreviewSectionKey>("overview");

  const [internalModuleTab, setInternalModuleTab] =
    useState<CoursePreviewModuleTabKey>("content");

  const resolvedSection = activeSection ?? internalSection;
  const resolvedModuleTab = activeModuleTab ?? internalModuleTab;

  function handleSectionChange(key: CoursePreviewSectionKey) {
    setInternalSection(key);
    onSectionChange?.(key);
  }

  function handleModuleTabChange(key: CoursePreviewModuleTabKey) {
    setInternalModuleTab(key);
    onModuleTabChange?.(key);
  }

  return (
    <section className="course-preview">
      <CoursePreviewHeader course={course} />
      <CoursePreviewStats course={course} />

      {notice && <div className="course-preview__notice">{notice}</div>}

      <div className="course-preview__layout">
        <CoursePreviewCurriculum
          course={course}
          activeKey={resolvedSection}
          onSelect={handleSectionChange}
        />

        <CoursePreviewContent
          course={course}
          activeSection={resolvedSection}
          activeModuleTab={resolvedModuleTab}
          onModuleTabChange={handleModuleTabChange}
          renderers={renderers}
        />
      </div>
    </section>
  );
}
