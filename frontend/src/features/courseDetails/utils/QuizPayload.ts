// frontend/src/features/courseDetails/utils/QuizPayload.ts

import type {
  LearnerQuizAnswerItem,
  NormalizedCourseQuiz,
  QuizAnswers,
} from "../types/LearnerCourseDetails";

export function buildLearnerQuizAnswerItems(
  quiz: NormalizedCourseQuiz,
  answers: QuizAnswers,
): LearnerQuizAnswerItem[] {
  return quiz.questions.map((question) => {
    const value = answers[question.item_id];

    if (Array.isArray(value)) {
      return {
        item_id: question.item_id,
        selected_choice_ids: value.map(String),
        selected_value: value.map(String),
      };
    }

    const selectedValue =
      value !== undefined && value !== null ? String(value) : "";

    return {
      item_id: question.item_id,
      selected_choice_ids: selectedValue ? [selectedValue] : [],
      selected_value: selectedValue || null,
    };
  });
}
