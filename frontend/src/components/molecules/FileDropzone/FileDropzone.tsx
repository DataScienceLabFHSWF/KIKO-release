// frontend/src/components/molecules/FileDropzone/FileDropzone.tsx

import { useRef, useState, type DragEvent } from "react";
import clsx from "clsx";
import { Button } from "@/components";
import "./FileDropzone.css";

type FileDropzoneProps = {
  label: string;
  accept?: string;
  multiple?: boolean;
  disabled?: boolean;
  onFilesSelected: (files: File[]) => void;
};

export function FileDropzone({
  label,
  accept,
  multiple = false,
  disabled = false,
  onFilesSelected,
}: FileDropzoneProps) {
  const inputRef = useRef<HTMLInputElement | null>(null);
  const [isDragging, setIsDragging] = useState(false);

  function handleFiles(fileList: FileList | null) {
    if (!fileList) return;
    onFilesSelected(Array.from(fileList));
  }

  function handleDrop(event: DragEvent<HTMLDivElement>) {
    event.preventDefault();
    setIsDragging(false);

    if (disabled) return;

    handleFiles(event.dataTransfer.files);
  }

  return (
    <div
      className={clsx("ui-file-dropzone", {
        "ui-file-dropzone--dragging": isDragging,
        "ui-file-dropzone--disabled": disabled,
      })}
      onDragOver={(event) => {
        event.preventDefault();
        if (!disabled) setIsDragging(true);
      }}
      onDragLeave={() => setIsDragging(false)}
      onDrop={handleDrop}
    >
      <input
        ref={inputRef}
        type="file"
        accept={accept}
        multiple={multiple}
        disabled={disabled}
        hidden
        onChange={(event) => handleFiles(event.target.files)}
      />

      <Button
        type="button"
        variant="secondary"
        size="sm"
        disabled={disabled}
        onClick={() => inputRef.current?.click()}
      >
        {label}
      </Button>

      <p>Drag and drop files here, or click to browse.</p>
    </div>
  );
}
