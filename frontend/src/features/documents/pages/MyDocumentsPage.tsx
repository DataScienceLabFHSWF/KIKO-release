// frontend/src/features/documents/pages/MyDocumentsPage.tsx

import { FileText, Trash2 } from "lucide-react";
import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useTranslation } from "node_modules/react-i18next";

import { PageHeader } from "@/components/molecules";
import { ConfirmDialog } from "@/components/organisms";
import { ErrorState, LoadingState, Button } from "@/components";
import { usePageMeta } from "@/app/hooks/usePageMeta";

import {
  deleteAllDocuments,
  deleteDocument,
  downloadDocument,
  listMyDocuments,
  previewMarkdownDocument,
  previewPdfDocument,
  documentQueryKeys,
} from "../api/DocumentsApi";
import { DocumentCard } from "../components/DocumentCard";
import { DocumentPreviewDialog } from "../components/DocumentPreviewDialog";
import type {
  DocumentItem,
  DocumentPreview,
  MarkdownPreviewResponse,
} from "../types/Documents";

import "./MyDocumentsPage.css";

type ConfirmState =
  | { type: "single"; document: DocumentItem }
  | { type: "all" }
  | null;

function isMarkdown(fileName: string) {
  return fileName.toLowerCase().endsWith(".md");
}

function normalizeDocuments(value: unknown): DocumentItem[] {
  return Array.isArray(value) ? value : [];
}

function isProcessingDocument(document: DocumentItem) {
  const status = document.status?.toLowerCase();

  return (
    status === "processing" ||
    status === "uploaded" ||
    status === "pending" ||
    status === "queued"
  );
}

function extractMarkdownPreview(payload: MarkdownPreviewResponse) {
  if (typeof payload.markdown === "string") return payload.markdown;
  if (typeof payload.content === "string") return payload.content;
  if (typeof payload.summary === "string") return payload.summary;

  return JSON.stringify(payload, null, 2);
}

export function MyDocumentsPage() {
  const { t } = useTranslation("myDocuments");
  const queryClient = useQueryClient();

  usePageMeta({
    title: t("title"),
  });

  const [busyDocumentId, setBusyDocumentId] = useState<number | null>(null);
  const [confirmState, setConfirmState] = useState<ConfirmState>(null);
  const [preview, setPreview] = useState<DocumentPreview | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);

  const documentsQuery = useQuery({
    queryKey: documentQueryKeys.myDocuments,
    queryFn: listMyDocuments,
    staleTime: 30_000,
    refetchOnWindowFocus: true,
    refetchInterval: (query) => {
      const documents = normalizeDocuments(query.state.data);
      return documents.some(isProcessingDocument) ? 5_000 : false;
    },
  });

  const documents = normalizeDocuments(documentsQuery.data);
  const hasDocuments = documents.length > 0;

  const deleteOneMutation = useMutation({
    mutationFn: deleteDocument,
    onSuccess: (_, documentId) => {
      queryClient.setQueryData<DocumentItem[]>(
        documentQueryKeys.myDocuments,
        (current) =>
          normalizeDocuments(current).filter(
            (document) => document.document_id !== documentId,
          ),
      );

      setConfirmState(null);
    },
    onError: (error) => {
      setActionError(
        error instanceof Error ? error.message : t("messages.deleteFailed"),
      );
    },
    onSettled: async () => {
      await queryClient.invalidateQueries({
        queryKey: documentQueryKeys.myDocuments,
      });
    },
  });

  const deleteAllMutation = useMutation({
    mutationFn: deleteAllDocuments,
    onSuccess: () => {
      queryClient.setQueryData<DocumentItem[]>(
        documentQueryKeys.myDocuments,
        [],
      );

      setConfirmState(null);
    },
    onError: (error) => {
      setActionError(
        error instanceof Error ? error.message : t("messages.deleteAllFailed"),
      );
    },
    onSettled: async () => {
      await queryClient.invalidateQueries({
        queryKey: documentQueryKeys.myDocuments,
      });
    },
  });

  async function handleDownload(document: DocumentItem) {
    setBusyDocumentId(document.document_id);
    setActionError(null);

    try {
      const blob = await downloadDocument(document.content_hash);
      const objectUrl = URL.createObjectURL(blob);

      const link = window.document.createElement("a");
      link.href = objectUrl;
      link.download = document.file_name;
      link.click();

      URL.revokeObjectURL(objectUrl);
    } catch (error) {
      setActionError(
        error instanceof Error ? error.message : t("messages.downloadFailed"),
      );
    } finally {
      setBusyDocumentId(null);
    }
  }

  async function handlePreview(document: DocumentItem) {
    setBusyDocumentId(document.document_id);
    setActionError(null);

    try {
      if (preview?.type === "image") {
        URL.revokeObjectURL(preview.objectUrl);
      }

      if (isMarkdown(document.file_name)) {
        const markdown = await previewMarkdownDocument(document.content_hash);

        setPreview({
          type: "markdown",
          title: document.file_name,
          content: extractMarkdownPreview(markdown),
        });
      } else {
        const blob = await previewPdfDocument(document.content_hash);
        const objectUrl = URL.createObjectURL(blob);

        setPreview({
          type: "image",
          title: document.file_name,
          objectUrl,
        });
      }
    } catch (error) {
      setActionError(
        error instanceof Error ? error.message : t("messages.previewFailed"),
      );
    } finally {
      setBusyDocumentId(null);
    }
  }

  function handleConfirmDelete() {
    setActionError(null);

    if (confirmState?.type === "single") {
      deleteOneMutation.mutate(confirmState.document.document_id);
      return;
    }

    if (confirmState?.type === "all") {
      deleteAllMutation.mutate();
    }
  }

  const isDeletingSingle = deleteOneMutation.isPending;
  const isDeletingAll = deleteAllMutation.isPending;

  if (documentsQuery.isLoading) {
    return <LoadingState description={t("status.loading")} />;
  }

  if (documentsQuery.isError) {
    return (
      <ErrorState
        title={t("messages.errorTitle")}
        description={
          documentsQuery.error instanceof Error
            ? documentsQuery.error.message
            : t("messages.loadFailed")
        }
        actionLabel={t("actions.retry")}
        onAction={() => void documentsQuery.refetch()}
      />
    );
  }

  return (
    <section className="documents-page">
      <PageHeader
        icon={<FileText size={44} strokeWidth={1.8} />}
        title={t("title")}
        subtitle={t("subtitle")}
        action={
          hasDocuments ? (
            <Button
              type="button"
              variant="danger"
              onClick={() => setConfirmState({ type: "all" })}
              disabled={isDeletingAll}
              isLoading={isDeletingAll}
            >
              <Trash2 size={16} strokeWidth={2.2} />
              {isDeletingAll ? t("confirm.working") : t("toolbar.deleteAll")}
            </Button>
          ) : null
        }
      />

      {actionError && (
        <p className="documents-page__error" role="alert">
          {actionError}
        </p>
      )}

      {!hasDocuments && (
        <div className="documents-page__empty">
          <FileText size={42} strokeWidth={1.8} />
          <h2>{t("empty.title")}</h2>
          <p>{t("empty.description")}</p>
        </div>
      )}

      {hasDocuments && (
        <div className="documents-page__list">
          {documents.map((document) => (
            <DocumentCard
              key={document.document_id}
              document={document}
              isBusy={
                busyDocumentId === document.document_id ||
                (isDeletingSingle &&
                  deleteOneMutation.variables === document.document_id)
              }
              onPreview={handlePreview}
              onDownload={handleDownload}
              onDelete={(document) =>
                setConfirmState({ type: "single", document })
              }
            />
          ))}
        </div>
      )}

      <ConfirmDialog
        isOpen={confirmState?.type === "single"}
        title={t("confirm.singleTitle")}
        description={t("confirm.singleDescription", {
          fileName:
            confirmState?.type === "single"
              ? confirmState.document.file_name
              : "",
        })}
        confirmLabel={t("confirm.yesDelete")}
        cancelLabel={t("confirm.cancel")}
        workingLabel={t("confirm.working")}
        isConfirming={isDeletingSingle}
        onConfirm={handleConfirmDelete}
        onCancel={() => setConfirmState(null)}
      />

      <ConfirmDialog
        isOpen={confirmState?.type === "all"}
        title={t("confirm.allTitle")}
        description={t("confirm.allDescription")}
        acknowledgementLabel={t("confirm.allAcknowledgement")}
        confirmLabel={t("confirm.yesDeleteAll")}
        cancelLabel={t("confirm.cancel")}
        workingLabel={t("confirm.working")}
        isConfirming={isDeletingAll}
        onConfirm={handleConfirmDelete}
        onCancel={() => setConfirmState(null)}
      />

      <DocumentPreviewDialog
        preview={preview}
        onClose={() => {
          if (preview?.type === "image") {
            URL.revokeObjectURL(preview.objectUrl);
          }

          setPreview(null);
        }}
      />
    </section>
  );
}
