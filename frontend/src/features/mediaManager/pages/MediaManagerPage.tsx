// frontend/src/features/mediaManager/pages/MediaManagerPage.tsx

import { Image, RefreshCw } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useTranslation } from "node_modules/react-i18next";

import {
  Button,
  EmptyState,
  ErrorState,
  LoadingState,
  PageHeader,
} from "@/components";
import { usePageMeta } from "@/app/hooks/usePageMeta";

import {
  deleteCourseImage,
  listCourseImages,
  listInstructorCourses,
  uploadCourseImage,
} from "../api/MediaManagerApi";
import { CourseSelector } from "../components/CourseSelector";
import { DeleteImageDialog } from "../components/DeleteImageDialog";
import { ImageGallery } from "../components/ImageGallery";
import { ImageUploadPanel } from "../components/ImageUploadPanel";
import type { CourseImage } from "../types/MediaManager";

import "./MediaManagerPage.css";

export function MediaManagerPage() {
  const { t } = useTranslation("mediaManager");
  const queryClient = useQueryClient();

  usePageMeta({
    title: t("title"),
  });

  const [selectedCourseId, setSelectedCourseId] = useState<number | null>(null);
  const [imageToDelete, setImageToDelete] = useState<CourseImage | null>(null);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);
  const [statusVariant, setStatusVariant] = useState<
    "success" | "warning" | "error" | "info"
  >("info");

  const coursesQuery = useQuery({
    queryKey: ["media-manager", "courses"],
    queryFn: listInstructorCourses,
    staleTime: 60_000,
  });

  const courses = coursesQuery.data ?? [];

  useEffect(() => {
    if (!selectedCourseId && courses.length > 0) {
      setSelectedCourseId(courses[0].course_id);
    }
  }, [courses, selectedCourseId]);

  const selectedCourse = useMemo(() => {
    return courses.find((course) => course.course_id === selectedCourseId);
  }, [courses, selectedCourseId]);

  const imagesQuery = useQuery({
    queryKey: ["media-manager", "course-images", selectedCourseId],
    queryFn: () => listCourseImages(selectedCourseId!),
    enabled: Boolean(selectedCourseId),
    staleTime: 15_000,
  });

  const uploadMutation = useMutation({
    mutationFn: (file: File) => {
      if (!selectedCourseId) {
        throw new Error(t("errors.noCourseSelected"));
      }

      return uploadCourseImage(selectedCourseId, file);
    },
    onSuccess: async (image) => {
      setStatusVariant("success");
      setStatusMessage(
        t("status.uploaded", {
          filename: image.original_filename,
        }),
      );

      await queryClient.invalidateQueries({
        queryKey: ["media-manager", "course-images", selectedCourseId],
      });
    },
    onError: (error) => {
      setStatusVariant("error");
      setStatusMessage(
        error instanceof Error ? error.message : t("errors.uploadFailed"),
      );
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (image: CourseImage) =>
      deleteCourseImage(image.course_id, image.stored_filename),
    onSuccess: async () => {
      setImageToDelete(null);
      setStatusVariant("success");
      setStatusMessage(t("status.deleted"));

      await queryClient.invalidateQueries({
        queryKey: ["media-manager", "course-images", selectedCourseId],
      });
    },
    onError: (error) => {
      setStatusVariant("error");
      setStatusMessage(
        error instanceof Error ? error.message : t("errors.deleteFailed"),
      );
    },
  });

  async function handleRefresh() {
    setStatusMessage(null);

    await Promise.all([
      queryClient.invalidateQueries({
        queryKey: ["media-manager", "courses"],
      }),
      queryClient.invalidateQueries({
        queryKey: ["media-manager", "course-images", selectedCourseId],
      }),
    ]);
  }

  if (coursesQuery.isLoading) {
    return <LoadingState description={t("loading.courses")} />;
  }

  if (coursesQuery.isError) {
    return (
      <ErrorState
        title={t("errors.loadCoursesTitle")}
        description={
          coursesQuery.error instanceof Error
            ? coursesQuery.error.message
            : t("errors.loadCoursesDescription")
        }
        actionLabel={t("actions.retry")}
        onAction={() => void coursesQuery.refetch()}
      />
    );
  }

  return (
    <section className="media-manager-page">
      <PageHeader
        icon={<Image size={42} strokeWidth={1.9} />}
        title={t("title")}
        subtitle={t("subtitle")}
      />

      <div className="media-manager-toolbar">
        {selectedCourse && (
          <span>
            {t("status.selectedCourse", {
              title: selectedCourse.title,
            })}
          </span>
        )}
      </div>

      {statusMessage && (
        <p
          className={`media-manager-status media-manager-status--${statusVariant}`}
          role={statusVariant === "error" ? "alert" : "status"}
        >
          {statusMessage}
        </p>
      )}

      {courses.length === 0 ? (
        <EmptyState
          title={t("empty.noCoursesTitle")}
          description={t("empty.noCoursesDescription")}
        />
      ) : (
        <>
          <CourseSelector
            courses={courses}
            selectedCourseId={selectedCourseId}
            disabled={uploadMutation.isPending || deleteMutation.isPending}
            onChange={(courseId) => {
              setSelectedCourseId(courseId);
              setStatusMessage(null);
            }}
          />

          <ImageUploadPanel
            disabled={!selectedCourseId}
            isUploading={uploadMutation.isPending}
            onUpload={(file) => uploadMutation.mutate(file)}
          />

          {imagesQuery.isLoading && (
            <LoadingState description={t("loading.images")} />
          )}

          {imagesQuery.isError && (
            <ErrorState
              title={t("errors.loadImagesTitle")}
              description={
                imagesQuery.error instanceof Error
                  ? imagesQuery.error.message
                  : t("errors.loadImagesDescription")
              }
              actionLabel={t("actions.retry")}
              onAction={() => void imagesQuery.refetch()}
            />
          )}

          {!imagesQuery.isLoading && !imagesQuery.isError && (
            <ImageGallery
              images={imagesQuery.data ?? []}
              disabled={deleteMutation.isPending}
              onDelete={setImageToDelete}
            />
          )}
        </>
      )}

      {imageToDelete && (
        <DeleteImageDialog
          image={imageToDelete}
          isDeleting={deleteMutation.isPending}
          onCancel={() => setImageToDelete(null)}
          onConfirm={() => deleteMutation.mutate(imageToDelete)}
        />
      )}
    </section>
  );
}
