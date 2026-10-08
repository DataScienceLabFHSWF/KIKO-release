// frontend/src/features/courseGenerator/components/CourseGeneratorControls.tsx

import { FileText, Plus, Minus, X } from "lucide-react";
import { useTranslation } from "node_modules/react-i18next";
import { IconButton } from "@/components";

type CountRange = {
  min: number;
  max: number;
  value: number;
};

type CourseGeneratorControlsProps = {
  file: File | null;
  isBusy: boolean;
  showPdfOptions: boolean;
  qaCount: number;
  quizQuestionCount: number;
  quizOptionCount: number;
  misconceptionCount: number;
  ranges: {
    qa: CountRange;
    quiz: CountRange;
    options: CountRange;
    misconceptions: CountRange;
  };
  onFileChange: (file: File | null) => void;
  onQaCountChange: (value: number) => void;
  onQuizQuestionCountChange: (value: number) => void;
  onQuizOptionCountChange: (value: number) => void;
  onMisconceptionCountChange: (value: number) => void;
};

type StepperProps = {
  label: string;
  value: number;
  min: number;
  max: number;
  disabled: boolean;
  onChange: (value: number) => void;
  t: (key: string, options?: any) => string;
};

function Stepper({
  label,
  value,
  min,
  max,
  disabled,
  onChange,
  t,
}: StepperProps) {
  function update(next: number) {
    onChange(Math.min(Math.max(next, min), max));
  }

  return (
    <label className="course-generator-stepper">
      <span>{label}</span>

      <div className="course-generator-stepper__control">
        <input value={value} readOnly />

        <IconButton
          variant="plain"
          disabled={disabled || value <= min}
          onClick={() => update(value - 1)}
          label={t("controls.decrease", { label })}
          icon={<Minus size={16} />}
        />

        <IconButton
          variant="plain"
          disabled={disabled || value >= max}
          onClick={() => update(value + 1)}
          label={t("controls.increase", { label })}
          icon={<Plus size={16} />}
        />
      </div>
    </label>
  );
}

export function CourseGeneratorControls({
  file,
  isBusy,
  showPdfOptions,
  qaCount,
  quizQuestionCount,
  quizOptionCount,
  misconceptionCount,
  ranges,
  onFileChange,
  onQaCountChange,
  onQuizQuestionCountChange,
  onQuizOptionCountChange,
  onMisconceptionCountChange,
}: CourseGeneratorControlsProps) {
  const { t } = useTranslation("courseGenerator");
  return (
    <section className="course-generator-controls">
      <label className="course-generator-upload">
        <span>{t("optionToChoose")}</span>

        <div className="course-generator-upload__box">
          {file ? (
            <div className="course-generator-upload__file">
              <FileText size={24} />
              <div>
                <strong>{file.name}</strong>
                <small>{(file.size / 1024 / 1024).toFixed(1)} MB</small>
              </div>
            </div>
          ) : (
            <span>{t("fileOptions")}</span>
          )}

          <input
            type="file"
            accept=".pdf,.md,.markdown,application/pdf,text/markdown"
            disabled={isBusy}
            onChange={(event) =>
              onFileChange(event.currentTarget.files?.[0] ?? null)
            }
          />
        </div>
      </label>

      {showPdfOptions && (
        <>
          <div className="course-generator-controls__grid">
            <Stepper
              label={t("controls.qaPairs")}
              value={qaCount}
              min={ranges.qa.min}
              max={ranges.qa.max}
              disabled={isBusy}
              onChange={onQaCountChange}
              t={t}
            />

            <Stepper
              label={t("controls.quizQuestions")}
              value={quizQuestionCount}
              min={ranges.quiz.min}
              max={ranges.quiz.max}
              disabled={isBusy}
              onChange={onQuizQuestionCountChange}
              t={t}
            />

            <Stepper
              label={t("controls.optionsPerQuizQuestion")}
              value={quizOptionCount}
              min={ranges.options.min}
              max={ranges.options.max}
              disabled={isBusy}
              onChange={onQuizOptionCountChange}
              t={t}
            />

            <Stepper
              label={t("controls.misconceptions")}
              value={misconceptionCount}
              min={ranges.misconceptions.min}
              max={ranges.misconceptions.max}
              disabled={isBusy}
              onChange={onMisconceptionCountChange}
              t={t}
            />
          </div>

          <p className="course-generator-controls__hint">
            {t("controls.pdfHint")}
          </p>
        </>
      )}
    </section>
  );
}
