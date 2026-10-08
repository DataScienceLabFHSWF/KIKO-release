// frontend/src/features/courseDetails/components/QuizOptionGroup.tsx

import clsx from "clsx";
import { Check } from "lucide-react";
import { Button } from "@/components";
import type {
  CourseChoice,
  CourseQuestionType,
  QuizAnswerValue,
} from "../types/LearnerCourseDetails";
import "./QuizOptionGroup.css";

type QuizOptionGroupProps = {
  questionId: string;
  type: CourseQuestionType;
  choices: CourseChoice[];
  value?: QuizAnswerValue;
  onChange: (value: QuizAnswerValue) => void;
};

export function QuizOptionGroup({
  questionId,
  type,
  choices,
  value,
  onChange,
}: QuizOptionGroupProps) {
  const selectedValues = Array.isArray(value) ? value : value ? [value] : [];

  function handleSelect(choiceId: string) {
    if (type === "multi_select") {
      const nextValue = selectedValues.includes(choiceId)
        ? selectedValues.filter((item) => item !== choiceId)
        : [...selectedValues, choiceId];

      onChange(nextValue);
      return;
    }

    onChange(choiceId);
  }

  return (
    <div
      className="quiz-option-group"
      role="group"
      aria-labelledby={questionId}
    >
      {choices.map((choice) => {
        const isSelected = selectedValues.includes(choice.id);

        return (
          <Button
            key={choice.id}
            type="button"
            variant="plain"
            className={clsx("quiz-option", {
              "quiz-option--selected": isSelected,
            })}
            onClick={() => handleSelect(choice.id)}
          >
            <span
              className={clsx("quiz-option__indicator", {
                "quiz-option__indicator--multi": type === "multi_select",
              })}
              aria-hidden="true"
            >
              {isSelected && <Check size={14} strokeWidth={2.5} />}
            </span>

            <span>{choice.text}</span>
          </Button>
        );
      })}
    </div>
  );
}
