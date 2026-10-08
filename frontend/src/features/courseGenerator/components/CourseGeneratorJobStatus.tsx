// frontend/src/features/courseGenerator/components/CourseGeneratorJobStatus.tsx

import { useTranslation } from "node_modules/react-i18next";
import type { CourseUploadJobResponse } from "../types/CourseGenerator";

type CourseGeneratorJobStatusProps = {
  job: CourseUploadJobResponse;
};

export function CourseGeneratorJobStatus({
  job,
}: CourseGeneratorJobStatusProps) {
  const { t } = useTranslation("courseGenerator");
  const progress = Math.min(Math.max(job.progress ?? 0, 0), 1);
  const percent = Math.round(progress * 100);

  return (
    <section className="course-generator-job">
      <p>{job.message}</p>

      <div className="course-generator-job__meta">
        <span>{t("job.percentComplete", { percent })}</span>
        <span>{t(`job.status.${job.status}`)}</span>
      </div>

      <div className="course-generator-job__bar">
        <span style={{ width: `${percent}%` }} />
      </div>
    </section>
  );
}
