// frontend/src/features/coursePreview/adapters/learnerCoursePreviewAdapter.ts

import type { NormalizedCourseDetails } from "@/features/courseDetails/types/LearnerCourseDetails";
import type {
  CoursePreviewCourse,
  CoursePreviewQuiz,
} from "../types/CoursePreview";

function convertQuiz(
  quiz: NormalizedCourseDetails["finalQuiz"],
): CoursePreviewQuiz | null {
  if (!quiz) return null;

  return {
    id: quiz.assessment_id,
    title: quiz.title,
    passPercent: quiz.pass_threshold,
    questions: quiz.questions.map((question) => ({
      id: question.item_id,
      text: question.text,
      type: question.type,
      points: question.points,
      choices: question.choices.map((choice) => ({
        id: choice.id,
        text: choice.text,
      })),
    })),
  };
}

export function createCoursePreviewFromLearnerCourse(
  course: NormalizedCourseDetails,
): CoursePreviewCourse {
  return {
    courseId: course.courseId,
    title: course.title,
    provider: course.provider,
    difficulty: course.difficulty,
    language: course.language,
    duration: course.duration,
    progressPercent: course.progressPercent,
    overview: course.overview,
    modules: course.modules.map((module) => ({
      id: module.id,
      title: module.title,
      content: module.content,
      practiceQuestions: module.practiceQuestions.map((question) => ({
        id: question.id,
        prompt: question.prompt,
        referenceAnswer: question.referenceAnswer,
        points: question.points,
      })),
      quiz: convertQuiz(module.quiz),
      furtherReading: module.furtherReading,
      misconceptions: module.misconceptions,
    })),
    resources: course.resources,
    finalQuiz: convertQuiz(course.finalQuiz),
    tags: course.skills,
    prerequisites: course.prerequisites,
    instructors: course.instructors,
    gradingNotes: course.grading.notes,
    isEnrolled: course.isEnrolled,
  };
}
