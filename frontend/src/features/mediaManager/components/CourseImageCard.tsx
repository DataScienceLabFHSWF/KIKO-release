// frontend/src/features/mediaManager/components/CourseImageCard.tsx

import { Check, Clipboard, Download, Trash2 } from "lucide-react";
import { useEffect, useState } from "react";
import { useTranslation } from "node_modules/react-i18next";
import { Button } from "@/components";
import {
  buildMarkdownImageReference,
  getCourseImageBlob,
} from "../api/MediaManagerApi";
import type { CourseImage } from "../types/MediaManager";
import { formatDateTime, formatFileSize } from "../utils/MediaManagerUtils";

type CourseImageCardProps = {
  image: CourseImage;
  disabled?: boolean;
  onDelete: (image: CourseImage) => void;
};

export function CourseImageCard({
  image,
  disabled = false,
  onDelete,
}: CourseImageCardProps) {
  const { t } = useTranslation("mediaManager");
  const [imageSrc, setImageSrc] = useState<string | null>(null);
  const [isImageLoading, setIsImageLoading] = useState(true);
  const [imageError, setImageError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  const markdownReference = buildMarkdownImageReference(image);

  useEffect(() => {
    let isMounted = true;
    let objectUrl: string | null = null;

    async function loadImage() {
      setIsImageLoading(true);
      setImageError(null);

      try {
        const blob = await getCourseImageBlob(
          image.course_id,
          image.stored_filename,
        );

        objectUrl = URL.createObjectURL(blob);

        if (isMounted) {
          setImageSrc(objectUrl);
        }
      } catch (error) {
        if (isMounted) {
          setImageError(
            error instanceof Error ? error.message : t("gallery.loadFailed"),
          );
        }
      } finally {
        if (isMounted) {
          setIsImageLoading(false);
        }
      }
    }

    void loadImage();

    return () => {
      isMounted = false;

      if (objectUrl) {
        URL.revokeObjectURL(objectUrl);
      }
    };
  }, [image.course_id, image.stored_filename, t]);

  async function handleCopy() {
    await navigator.clipboard.writeText(markdownReference);
    setCopied(true);
    window.setTimeout(() => setCopied(false), 1800);
  }

  function handleDownload() {
    if (!imageSrc) return;

    const link = document.createElement("a");
    link.href = imageSrc;
    link.download = image.original_filename;
    link.click();
  }

  return (
    <article className="media-image-card">
      <div className="media-image-card__preview">
        {isImageLoading && <span>{t("gallery.loadingImage")}</span>}

        {!isImageLoading && imageError && (
          <span className="media-image-card__error">{imageError}</span>
        )}

        {!isImageLoading && !imageError && imageSrc && (
          <img src={imageSrc} alt={image.original_filename} loading="lazy" />
        )}
      </div>

      <div className="media-image-card__body">
        <h3 title={image.original_filename}>{image.original_filename}</h3>

        <dl>
          <div>
            <dt>{t("gallery.size")}</dt>
            <dd>{formatFileSize(image.size_bytes)}</dd>
          </div>

          <div>
            <dt>{t("gallery.type")}</dt>
            <dd>{image.content_type ?? "—"}</dd>
          </div>

          <div>
            <dt>{t("gallery.uploadedAt")}</dt>
            <dd>{formatDateTime(image.uploaded_at)}</dd>
          </div>
        </dl>

        <label className="media-image-card__markdown">
          <span>{t("gallery.markdownLabel")}</span>
          <code>{markdownReference}</code>
        </label>
      </div>

      <div className="media-image-card__actions">
        <Button type="button" variant="ghost" onClick={handleCopy}>
          {copied ? <Check size={16} /> : <Clipboard size={16} />}
          {copied ? t("gallery.copied") : t("gallery.copy")}
        </Button>

        <Button
          type="button"
          variant="ghost"
          disabled={!imageSrc}
          onClick={handleDownload}
        >
          <Download size={16} />
          {t("gallery.download")}
        </Button>

        <Button
          type="button"
          variant="danger"
          disabled={disabled}
          onClick={() => onDelete(image)}
        >
          <Trash2 size={16} />
          {t("gallery.delete")}
        </Button>
      </div>
    </article>
  );
}
