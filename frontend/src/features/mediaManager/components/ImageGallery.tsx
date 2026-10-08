// frontend/src/features/mediaManager/components/ImageGallery.tsx

import { Images } from "lucide-react";
import { useTranslation } from "node_modules/react-i18next";
import { EmptyState } from "@/components";
import { CourseImageCard } from "./CourseImageCard";
import type { CourseImage } from "../types/MediaManager";

type ImageGalleryProps = {
  images: CourseImage[];
  disabled?: boolean;
  onDelete: (image: CourseImage) => void;
};

export function ImageGallery({
  images,
  disabled = false,
  onDelete,
}: ImageGalleryProps) {
  const { t } = useTranslation("mediaManager");

  return (
    <section className="media-manager-gallery">
      <div className="media-manager-card__header">
        <Images size={24} strokeWidth={2.2} />
        <div>
          <h2>{t("gallery.title")}</h2>
          <p>
            {t("gallery.subtitle", {
              count: images.length,
            })}
          </p>
        </div>
      </div>

      {images.length === 0 ? (
        <EmptyState
          title={t("gallery.emptyTitle")}
          description={t("gallery.emptyDescription")}
        />
      ) : (
        <div className="media-manager-gallery__grid">
          {images.map((image) => (
            <CourseImageCard
              key={image.stored_filename}
              image={image}
              disabled={disabled}
              onDelete={onDelete}
            />
          ))}
        </div>
      )}
    </section>
  );
}
