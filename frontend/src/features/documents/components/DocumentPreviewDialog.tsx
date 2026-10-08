// frontend/src/features/documents/components/DocumentPreviewDialog.tsx

import { X } from "lucide-react";
import { useTranslation } from "node_modules/react-i18next";
import { IconButton } from "@/components";
import type { DocumentPreview } from "../types/Documents";
import "./DocumentPreviewDialog.css";

type DocumentPreviewDialogProps = {
  preview: DocumentPreview | null;
  onClose: () => void;
};

export function DocumentPreviewDialog({
  preview,
  onClose,
}: DocumentPreviewDialogProps) {
  const { t } = useTranslation("myDocuments");
  if (!preview) return null;

  return (
    <div className="document-preview-backdrop">
      <section
        className="document-preview"
        role="dialog"
        aria-modal="true"
        aria-label={preview.title}
      >
        <header>
          <strong>{preview.title}</strong>

          <IconButton
            variant="plain"
            label={t("actions.closePreview")}
            icon={<X size={18} strokeWidth={2.4} />}
            onClick={onClose}
          />
        </header>

        <div className="document-preview__body">
          {preview.type === "image" ? (
            <img src={preview.objectUrl} alt={preview.title} />
          ) : (
            <pre>{preview.content}</pre>
          )}
        </div>
      </section>
    </div>
  );
}
