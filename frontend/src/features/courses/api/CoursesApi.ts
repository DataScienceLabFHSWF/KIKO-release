// frontend/src/features/courses/api/CoursesApi.ts

import { apiRequest } from "@/api/client";
import type {
  InstructorCourse,
  InstructorCourseDetails,
  InstructorCourseUpdateRequest,
  InstructorCourseUpdateResponse,
  LearnerAvailableCourse,
  LearnerEnrolledCourse,
} from "../types/Courses";

export const courseQueryKeys = {
  learner: ["courses", "learner"] as const,
  learnerEnrolled: ["courses", "learner", "enrolled"] as const,
  learnerRecommended: ["courses", "learner", "recommended"] as const,
  learnerAvailable: ["courses", "learner", "available"] as const,
  instructor: ["courses", "instructor"] as const,
  instructorDetails: (courseId: number) =>
    ["courses", "instructor", "details", courseId] as const,

  learnerDetails: (courseId: number) =>
    ["courses", "learner", "details", courseId] as const,

  learnerStatistics: ["dashboard", "learner", "statistics"] as const,
};

export function getInstructorCourseDetails(courseId: number) {
  return apiRequest<InstructorCourseDetails>(`/course/${courseId}`);
}

export function updateInstructorCourse(
  courseId: number,
  payload: InstructorCourseUpdateRequest,
) {
  return apiRequest<InstructorCourseUpdateResponse>(`/course/${courseId}`, {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}

export function getLearnerEnrolledCourses() {
  return apiRequest<LearnerEnrolledCourse[]>("/learner/courses/enrolled");
}

export function getLearnerRecommendedCourses() {
  return apiRequest<LearnerAvailableCourse[]>("/learner/courses/recommended");
}

export function getLearnerAvailableCourses() {
  return apiRequest<LearnerAvailableCourse[]>("/learner/courses/all");
}

export function enrollInCourse(courseId: number) {
  return apiRequest<void>(`/learner/courses/${courseId}/enroll`, {
    method: "POST",
  });
}

export function unenrollFromCourse(courseId: number) {
  return apiRequest<void>(`/learner/courses/${courseId}/enrollment`, {
    method: "DELETE",
  });
}

export function dismissRecommendedCourse(courseId: number) {
  return apiRequest<void>(`/learner/courses/recommended/${courseId}`, {
    method: "DELETE",
  });
}

export function getInstructorCourses() {
  return apiRequest<InstructorCourse[]>("/course/my_courses");
}

export function deleteInstructorCourse(courseId: number) {
  return apiRequest<void>(`/course/${courseId}`, {
    method: "DELETE",
  });
}
