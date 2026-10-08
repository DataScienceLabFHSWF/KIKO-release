// frontend/src/features/mediaManager/components/DeleteImageDialog.tsx

import { AlertTriangle } from "lucide-react";
import { useTranslation } from "node_modules/react-i18next";
import { Button } from "@/components";
import type { CourseImage } from "../types/MediaManager";

type DeleteImageDialogProps = {
  image: CourseImage;
  isDeleting: boolean;
  onCancel: () => void;
  onConfirm: () => void;
};

export function DeleteImageDialog({
  image,
  isDeleting,
  onCancel,
  onConfirm,
}: DeleteImageDialogProps) {
  const { t } = useTranslation("mediaManager");

  return (
    <div className="media-manager-dialog-backdrop" role="presentation">
      <section
        className="media-manager-dialog"
        role="dialog"
        aria-modal="true"
        aria-labelledby="delete-image-title"
      >
        <div className="media-manager-dialog__header">
          <AlertTriangle size={26} strokeWidth={2.3} />
          <h2 id="delete-image-title">{t("deleteDialog.title")}</h2>
        </div>

        <p>{t("deleteDialog.body", { filename: image.original_filename })}</p>

        <p className="media-manager-warning">{t("deleteDialog.warning")}</p>

        <div className="media-manager-dialog__actions">
          <Button
            type="button"
            variant="ghost"
            disabled={isDeleting}
            onClick={onCancel}
          >
            {t("deleteDialog.cancel")}
          </Button>

          <Button
            type="button"
            variant="danger"
            isLoading={isDeleting}
            disabled={isDeleting}
            onClick={onConfirm}
          >
            {isDeleting
              ? t("deleteDialog.deleting")
              : t("deleteDialog.confirm")}
          </Button>
        </div>
      </section>
    </div>
  );
}
