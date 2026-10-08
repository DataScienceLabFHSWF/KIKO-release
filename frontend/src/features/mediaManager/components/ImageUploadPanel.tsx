// frontend/src/features/mediaManager/components/ImageUploadPanel.tsx

import { ImagePlus, Upload, X } from "lucide-react";
import { useEffect, useState } from "react";
import { useTranslation } from "node_modules/react-i18next";
import { Button, IconButton } from "@/components";
import { formatFileSize, isValidImageFile } from "../utils/MediaManagerUtils";

type ImageUploadPanelProps = {
  disabled?: boolean;
  isUploading: boolean;
  onUpload: (file: File) => void;
};

export function ImageUploadPanel({
  disabled = false,
  isUploading,
  onUpload,
}: ImageUploadPanelProps) {
  const { t } = useTranslation("mediaManager");
  const [file, setFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [validationMessage, setValidationMessage] = useState<string | null>(
    null,
  );

  useEffect(() => {
    if (!file) {
      setPreviewUrl(null);
      return;
    }

    const objectUrl = URL.createObjectURL(file);
    setPreviewUrl(objectUrl);

    return () => URL.revokeObjectURL(objectUrl);
  }, [file]);

  function handleFileChange(nextFile: File | null) {
    setValidationMessage(null);

    if (!nextFile) {
      setFile(null);
      return;
    }

    if (!isValidImageFile(nextFile)) {
      setFile(null);
      setValidationMessage(t("upload.invalidType"));
      return;
    }

    setFile(nextFile);
  }

  function handleUpload() {
    if (!file) {
      setValidationMessage(t("upload.noFile"));
      return;
    }

    onUpload(file);
    setFile(null);
  }

  return (
    <section className="media-manager-card">
      <div className="media-manager-card__header">
        <ImagePlus size={24} strokeWidth={2.2} />
        <div>
          <h2>{t("upload.title")}</h2>
          <p>{t("upload.subtitle")}</p>
        </div>
      </div>

      <label className="media-manager-upload">
        {file ? (
          <div className="media-manager-upload__selected">
            <strong>{file.name}</strong>
            <small>{formatFileSize(file.size)}</small>

            <IconButton
              variant="plain"
              disabled={disabled || isUploading}
              onClick={(event) => {
                event.preventDefault();
                handleFileChange(null);
              }}
              label={t("upload.remove")}
              icon={<X size={15} />}
            />
          </div>
        ) : (
          <span>{t("upload.dropLabel")}</span>
        )}

        <input
          type="file"
          accept="image/png,image/jpeg,image/jpg,image/gif,image/webp,image/svg+xml"
          disabled={disabled || isUploading}
          onChange={(event) =>
            handleFileChange(event.currentTarget.files?.[0] ?? null)
          }
        />
      </label>

      {validationMessage && (
        <p className="media-manager-warning" role="alert">
          {validationMessage}
        </p>
      )}

      {previewUrl && file && (
        <div className="media-manager-upload-preview">
          <img src={previewUrl} alt={file.name} />
          <div>
            <strong>{file.name}</strong>
            <span>{formatFileSize(file.size)}</span>
          </div>
        </div>
      )}

      <div className="media-manager-actions">
        <Button
          type="button"
          disabled={!file || disabled || isUploading}
          isLoading={isUploading}
          onClick={handleUpload}
        >
          <Upload size={17} strokeWidth={2.3} />
          {isUploading ? t("upload.uploading") : t("upload.button")}
        </Button>
      </div>
    </section>
  );
}
