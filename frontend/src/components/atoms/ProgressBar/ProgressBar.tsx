// frontend/src/components/atoms/ProgressBar/ProgressBar.tsx

import "./ProgressBar.css";

type ProgressBarProps = {
  value: number;
  max?: number;
  label?: string;
};

export function ProgressBar({ value, max = 100, label }: ProgressBarProps) {
  const normalizedValue = Math.min(Math.max(value, 0), max);
  const percent = Math.round((normalizedValue / max) * 100);

  return (
    <div className="ui-progress">
      {label && <div className="ui-progress__label">{label}</div>}
      <div
        className="ui-progress__track"
        role="progressbar"
        aria-valuemin={0}
        aria-valuemax={max}
        aria-valuenow={normalizedValue}
        aria-label={label}
      >
        <div className="ui-progress__bar" style={{ width: `${percent}%` }} />
      </div>
    </div>
  );
}
