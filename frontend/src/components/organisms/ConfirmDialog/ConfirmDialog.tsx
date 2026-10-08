// frontend/src/components/organisms/ConfirmDialog/ConfirmDialog.tsx

import { useEffect, useState } from "react";
import { Info, X } from "lucide-react";
import { Button, IconButton } from "@/components";
import "./ConfirmDialog.css";

type ConfirmDialogProps = {
  isOpen: boolean;
  title: string;
  description?: string;
  confirmLabel?: string;
  cancelLabel?: string;
  workingLabel?: string;
  acknowledgementLabel?: string;
  isConfirming?: boolean;
  onConfirm: () => void;
  onCancel: () => void;
};

export function ConfirmDialog({
  isOpen,
  title,
  description,
  confirmLabel,
  cancelLabel,
  workingLabel = "Working...",
  acknowledgementLabel,
  isConfirming = false,
  onConfirm,
  onCancel,
}: ConfirmDialogProps) {
  const [isAcknowledged, setIsAcknowledged] = useState(false);

  useEffect(() => {
    if (isOpen) setIsAcknowledged(false);
  }, [isOpen]);

  useEffect(() => {
    function handleKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape") onCancel();
    }

    if (isOpen) window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, onCancel]);

  if (!isOpen) return null;

  const requiresAcknowledgement = Boolean(acknowledgementLabel);
  const canConfirm =
    !isConfirming && (!requiresAcknowledgement || isAcknowledged);

  return (
    <div className="confirm-dialog-backdrop">
      <section
        className="confirm-dialog"
        role="dialog"
        aria-modal="true"
        aria-labelledby="confirm-dialog-title"
      >
        <header className="confirm-dialog__header">
          <h2 id="confirm-dialog-title">{title}</h2>

          <IconButton
            label="Close dialog"
            icon={<X size={18} strokeWidth={2.4} />}
            variant="plain"
            size="sm"
            className="confirm-dialog__close"
            onClick={onCancel}
          />
        </header>

        {description && (
          <p className="confirm-dialog__description">
            <Info size={17} strokeWidth={2.2} aria-hidden="true" />
            <span>{description}</span>
          </p>
        )}

        {acknowledgementLabel && (
          <label className="confirm-dialog__acknowledgement">
            <input
              type="checkbox"
              checked={isAcknowledged}
              onChange={(event) =>
                setIsAcknowledged(event.currentTarget.checked)
              }
            />
            <span>{acknowledgementLabel}</span>
          </label>
        )}

        <div className="confirm-dialog__actions">
          <Button
            type="button"
            variant="danger"
            isLoading={isConfirming}
            disabled={!canConfirm}
            onClick={onConfirm}
          >
            {isConfirming ? workingLabel : confirmLabel}
          </Button>

          <Button
            type="button"
            variant="ghost"
            disabled={isConfirming}
            onClick={onCancel}
          >
            {cancelLabel}
          </Button>
        </div>
      </section>
    </div>
  );
}
