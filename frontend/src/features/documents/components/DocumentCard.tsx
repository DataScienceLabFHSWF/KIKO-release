// frontend/src/features/documents/components/DocumentCard.tsx

import { Download, Eye, FileText, FileType, Trash2 } from "lucide-react";
import { useTranslation } from "node_modules/react-i18next";
import { Button } from "@/components";
import type { DocumentCardAction, DocumentItem } from "../types/Documents";
import "./DocumentCard.css";

type DocumentCardProps = {
  document: DocumentItem;
  isBusy?: boolean;
  activeAction?: DocumentCardAction | null;
  onPreview: (document: DocumentItem) => void;
  onDownload: (document: DocumentItem) => void;
  onDelete: (document: DocumentItem) => void;
};

function formatDate(value: string) {
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

function isPdf(fileName: string) {
  return fileName.toLowerCase().endsWith(".pdf");
}

export function DocumentCard({
  document,
  isBusy = false,
  activeAction = null,
  onPreview,
  onDownload,
  onDelete,
}: DocumentCardProps) {
  const { t } = useTranslation("myDocuments");
  const Icon = isPdf(document.file_name) ? FileType : FileText;

  return (
    <article className="document-card">
      <div className="document-card__icon" aria-hidden="true">
        <Icon size={52} strokeWidth={1.8} />
      </div>

      <div className="document-card__content">
        <h2>{document.file_name}</h2>

        <p>
          {t("fields.uploaded")}:{" "}
          <span>{formatDate(document.uploaded_at)}</span>
        </p>

        <p>
          {t("fields.status")}: <span>{document.status ?? "unknown"}</span>
        </p>
      </div>

      <div className="document-card__actions">
        <Button
          type="button"
          variant={activeAction === "preview" ? "primary" : "ghost"}
          disabled={isBusy}
          className="document-card__action"
          aria-pressed={activeAction === "preview"}
          onClick={() => onPreview(document)}
        >
          <Eye size={16} strokeWidth={2.2} />
          {t("actions.preview")}
        </Button>

        <Button
          type="button"
          variant={activeAction === "download" ? "primary" : "ghost"}
          disabled={isBusy}
          className="document-card__action"
          aria-pressed={activeAction === "download"}
          onClick={() => onDownload(document)}
        >
          <Download size={16} strokeWidth={2.2} />
          {t("actions.download")}
        </Button>

        <Button
          type="button"
          variant="danger"
          disabled={isBusy}
          className="document-card__action"
          onClick={() => onDelete(document)}
        >
          <Trash2 size={16} strokeWidth={2.2} />
          {t("actions.delete")}
        </Button>
      </div>
    </article>
  );
}
