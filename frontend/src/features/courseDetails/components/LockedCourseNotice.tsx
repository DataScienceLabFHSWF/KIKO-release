// frontend/src/features/courseDetails/components/LockedCourseNotice.tsx

import { Lock, UserPlus } from "lucide-react";
import { useTranslation } from "node_modules/react-i18next";
import { Button } from "@/components";
import "./CourseDetailsComponents.css";

type LockedCourseNoticeProps = {
  onEnroll: () => void;
  isWorking?: boolean;
};

export function LockedCourseNotice({
  onEnroll,
  isWorking = false,
}: LockedCourseNoticeProps) {
  const { t } = useTranslation("courseDetails");

  return (
    <section className="locked-course-notice" role="status">
      <div className="locked-course-notice__message">
        <Lock size={18} strokeWidth={2.3} aria-hidden="true" />
        <div>
          <strong>{t("locked.title")}</strong>
          <p>{t("locked.description")}</p>
        </div>
      </div>

      <Button
        type="button"
        variant="primary"
        className="locked-course-notice__button"
        onClick={onEnroll}
        isLoading={isWorking}
      >
        <UserPlus size={16} strokeWidth={2.3} aria-hidden="true" />
        <span>{isWorking ? t("actions.enrolling") : t("actions.enroll")}</span>
      </Button>
    </section>
  );
}
