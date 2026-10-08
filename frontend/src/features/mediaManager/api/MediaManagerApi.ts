// frontend/src/features/mediaManager/api/MediaManagerApi.ts

import { apiBlob, apiRequest } from "@/api/client";
import type {
  CourseImage,
  CourseImageUploadResponse,
  InstructorCourseSummary,
} from "../types/MediaManager";

export function listInstructorCourses() {
  return apiRequest<InstructorCourseSummary[]>("/course/my_courses");
}

export function listCourseImages(courseId: number) {
  return apiRequest<CourseImage[]>(`/course/${courseId}/images`);
}

export function uploadCourseImage(courseId: number, file: File) {
  const formData = new FormData();
  formData.append("file", file);

  return apiRequest<CourseImageUploadResponse>(`/course/${courseId}/images`, {
    method: "POST",
    body: formData,
  });
}

export function deleteCourseImage(courseId: number, storedFilename: string) {
  return apiRequest<void>(
    `/course/${courseId}/images/${encodeURIComponent(storedFilename)}`,
    {
      method: "DELETE",
    },
  );
}

export function getCourseImageBlob(courseId: number, storedFilename: string) {
  return apiBlob(
    `/course/${courseId}/images/${encodeURIComponent(storedFilename)}`,
  );
}

export function buildMarkdownImageReference(image: CourseImage) {
  const imageUrl =
    image.url ??
    `/api/course/${image.course_id}/images/${encodeURIComponent(
      image.stored_filename,
    )}`;

  return `![${image.original_filename}](${imageUrl})`;
}
