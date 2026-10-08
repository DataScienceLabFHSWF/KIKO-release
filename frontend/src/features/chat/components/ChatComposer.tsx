// frontend/src/features/chat/components/ChatComposer.tsx

import { FilePlus2, Mic, SendHorizontal, X } from "lucide-react";
import {
  useRef,
  useState,
  type ChangeEvent,
  type DragEvent,
  type FormEvent,
} from "react";
import { useTranslation } from "node_modules/react-i18next";
import { IconButton } from "@/components";
import "./ChatComposer.css";

const MAX_FILE_SIZE_MB = 20;
const MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024;

type ChatComposerProps = {
  value: string;
  files: File[];
  isSubmitting?: boolean;
  isUploading?: boolean;
  onChange: (value: string) => void;
  onFilesChange: (files: File[]) => void;
  onSubmit: () => void;
};

function isPdfFile(file: File) {
  return (
    file.type === "application/pdf" || file.name.toLowerCase().endsWith(".pdf")
  );
}

export function ChatComposer({
  value,
  files,
  isSubmitting = false,
  isUploading = false,
  onChange,
  onFilesChange,
  onSubmit,
}: ChatComposerProps) {
  const { t } = useTranslation("chatAssistant");
  const inputRef = useRef<HTMLInputElement | null>(null);
  const [fileError, setFileError] = useState<string | null>(null);
  const [isDragging, setIsDragging] = useState(false);

  const isBusy = isSubmitting || isUploading;

  function openFilePicker() {
    inputRef.current?.click();
  }

  function validateAndAddFiles(nextFiles: File[]) {
    setFileError(null);

    const accepted: File[] = [];
    const rejected: string[] = [];

    nextFiles.forEach((file) => {
      if (!isPdfFile(file)) {
        rejected.push(`${file.name}: ${t("upload.errors.pdfOnly")}`);
        return;
      }

      if (file.size > MAX_FILE_SIZE_BYTES) {
        rejected.push(
          `${file.name}: ${t("upload.errors.maxSize", {
            size: MAX_FILE_SIZE_MB,
          })}`,
        );
        return;
      }

      accepted.push(file);
    });

    if (rejected.length > 0) {
      setFileError(rejected[0]);
    }

    if (accepted.length > 0) {
      const merged = [...files, ...accepted];
      const unique = merged.filter((file, index, list) => {
        return (
          list.findIndex(
            (item) =>
              item.name === file.name &&
              item.size === file.size &&
              item.lastModified === file.lastModified,
          ) === index
        );
      });

      onFilesChange(unique);
    }
  }

  function handleFileInputChange(event: ChangeEvent<HTMLInputElement>) {
    validateAndAddFiles(Array.from(event.currentTarget.files ?? []));
    event.currentTarget.value = "";
  }

  function handleDrop(event: DragEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsDragging(false);
    validateAndAddFiles(Array.from(event.dataTransfer.files));
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!value.trim() || isBusy) return;

    onSubmit();
  }

  function removeFile(fileToRemove: File) {
    onFilesChange(files.filter((file) => file !== fileToRemove));
  }

  return (
    <form
      className={`chat-composer ${isDragging ? "chat-composer--dragging" : ""}`}
      onSubmit={handleSubmit}
      onDragOver={(event) => {
        event.preventDefault();
        setIsDragging(true);
      }}
      onDragLeave={() => setIsDragging(false)}
      onDrop={handleDrop}
    >
      <input
        ref={inputRef}
        type="file"
        accept="application/pdf,.pdf"
        multiple
        className="chat-composer__file-input"
        onChange={handleFileInputChange}
      />

      {files.length > 0 && (
        <div className="chat-composer__files" aria-live="polite">
          {files.map((file) => (
            <span
              key={`${file.name}-${file.size}`}
              className="chat-composer__file-chip"
            >
              {file.name}
              <IconButton
                variant="plain"
                className="chat-composer__file-remove"
                label={t("upload.removeFile", { fileName: file.name })}
                icon={<X size={12} strokeWidth={2.4} />}
                onClick={() => removeFile(file)}
              />
            </span>
          ))}
        </div>
      )}

      {fileError && (
        <p className="chat-composer__error" role="alert">
          {fileError}
        </p>
      )}

      <div className="chat-composer__shell">
        <IconButton
          className="chat-composer__upload"
          label={t("upload.title")}
          title={t("upload.title")}
          disabled={isBusy}
          icon={<FilePlus2 size={22} strokeWidth={2.2} />}
          onClick={openFilePicker}
        />

        <input
          value={value}
          disabled={isBusy}
          placeholder={t("defaultPlaceHolder")}
          onChange={(event) => onChange(event.currentTarget.value)}
        />

        <IconButton
          className="chat-composer__mic"
          label={t("voice.disabled")}
          title={t("voice.disabled")}
          disabled
          icon={<Mic size={17} strokeWidth={2.2} />}
        />

        <IconButton
          type="submit"
          variant="primary"
          className="chat-composer__send"
          label={t("actions.send")}
          title={t("actions.send")}
          disabled={!value.trim() || isBusy}
          icon={<SendHorizontal size={18} strokeWidth={2.4} />}
        />
      </div>

      <p className="chat-composer__hint">
        {isDragging ? t("upload.dropHint") : t("upload.hint")}
      </p>
    </form>
  );
}
