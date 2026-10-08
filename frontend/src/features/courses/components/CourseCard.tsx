// frontend/src/features/courses/components/CourseCard.tsx

import { BookOpen, CheckCircle2, Info } from "lucide-react";
import { useTranslation } from "node_modules/react-i18next";
import { Button, ButtonLink } from "@/components";
import type { CourseCardAction } from "../types/Courses";
import { safePercent, shortenText } from "../utils/CourseText";
import "./CourseCard.css";

type CourseCardProps = {
  title: string;
  summary?: string | null;
  reason?: string | null;
  courseId?: number;
  progressPercent?: number;
  statusLabel?: string;
  meta?: Array<{
    label: string;
    value: string | number;
    icon?: React.ReactNode;
  }>;
  actions: CourseCardAction[];
};

function mapButtonVariant(
  variant: CourseCardAction["variant"],
): "primary" | "secondary" | "ghost" | "danger" | "success" {
  return variant ?? "primary";
}

export function CourseCard({
  title,
  summary,
  reason,
  courseId,
  progressPercent,
  statusLabel,
  meta = [],
  actions,
}: CourseCardProps) {
  const { t } = useTranslation("courses");
  const progress = safePercent(progressPercent);
  const shouldShowProgress = progressPercent !== undefined;

  return (
    <article className="course-card">
      <div className="course-card__main">
        <div className="course-card__title-row">
          <BookOpen size={22} strokeWidth={2.2} aria-hidden="true" />
          <h3>{title}</h3>
          {courseId !== undefined && (
            <span className="course-card__id">#{courseId}</span>
          )}
        </div>

        {summary && (
          <p className="course-card__description">{shortenText(summary)}</p>
        )}

        {reason && (
          <p className="course-card__reason">
            <Info size={15} strokeWidth={2.2} aria-hidden="true" />
            {reason}
          </p>
        )}

        {meta.length > 0 && (
          <div className="course-card__meta">
            {meta.map((item) => (
              <span key={item.label}>
                {item.icon}
                {item.label}: <strong>{item.value}</strong>
              </span>
            ))}
          </div>
        )}

        {shouldShowProgress && (
          <div className="course-card__progress-block">
            <div className="course-card__progress-label">
              <span>{t("progress")}</span>
              <strong>{progress}%</strong>
            </div>

            <div
              className="course-card__progress"
              role="progressbar"
              aria-valuenow={progress}
              aria-valuemin={0}
              aria-valuemax={100}
            >
              <span style={{ width: `${progress}%` }} />
            </div>
          </div>
        )}

        {statusLabel && (
          <p className="course-card__status">
            <CheckCircle2 size={16} strokeWidth={2.2} aria-hidden="true" />
            {statusLabel}
          </p>
        )}
      </div>

      <div className="course-card__actions">
        {actions.map((action) => {
          const content = (
            <>
              {action.icon}
              <span>{action.label}</span>
            </>
          );

          if (action.to) {
            return (
              <ButtonLink
                key={action.label}
                to={action.to}
                variant={mapButtonVariant(action.variant)}
                className="course-card__action"
                aria-label={action.ariaLabel ?? action.label}
              >
                {content}
              </ButtonLink>
            );
          }

          return (
            <Button
              key={action.label}
              type="button"
              variant={mapButtonVariant(action.variant)}
              className="course-card__action"
              onClick={action.onClick}
              disabled={action.disabled}
              aria-label={action.ariaLabel ?? action.label}
            >
              {content}
            </Button>
          );
        })}
      </div>
    </article>
  );
}
