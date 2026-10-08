// frontend/src/features/chat/pages/ChatAssistantPage.tsx

import { useEffect, useMemo, useState } from "react";
import { useTranslation } from "node_modules/react-i18next";
import { usePageMeta } from "@/app/hooks/usePageMeta";
import type { ChatLlmModel, ChatMessage } from "../types/Chat";
import {
  getChatHistory,
  processUploadedPdfDocuments,
  submitChatQuery,
} from "../api/ChatApi";
import { ChatComposer } from "../components/ChatComposer";
import { ChatMessageList } from "../components/ChatMessageList";
import { ChatModelBar } from "../components/ChatModelBar";
import { ChatSystemInfoPanel } from "../components/ChatSystemInfoPanel";
import "./ChatAssistantPage.css";

function mapHistoryMessages(
  messages: Awaited<ReturnType<typeof getChatHistory>>["messages"],
): ChatMessage[] {
  return messages.map((message, index) => ({
    id: `${message.role}-${message.timestamp ?? "no-time"}-${index}`,
    role: message.role,
    content: message.content,
    sources: message.sources ?? [],
    timestamp: message.timestamp ?? null,
  }));
}

export function ChatAssistantPage() {
  const { t } = useTranslation("chatAssistant");

  usePageMeta({
    title: t("metaTitle"),
  });

  const [query, setQuery] = useState("");
  const [selectedModel, setSelectedModel] =
    useState<ChatLlmModel>("llama3.3:70b");
  const [files, setFiles] = useState<File[]>([]);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isHistoryLoading, setIsHistoryLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isSystemInfoOpen, setIsSystemInfoOpen] = useState(false);

  useEffect(() => {
    let isCancelled = false;

    async function loadHistory() {
      setIsHistoryLoading(true);
      setError(null);

      try {
        const history = await getChatHistory();

        if (!isCancelled) {
          setMessages(mapHistoryMessages(history.messages));
        }
      } catch (error) {
        if (!isCancelled) {
          setError(
            error instanceof Error ? error.message : t("history.loadFailed"),
          );
        }
      } finally {
        if (!isCancelled) {
          setIsHistoryLoading(false);
        }
      }
    }

    void loadHistory();

    return () => {
      isCancelled = true;
    };
  }, [t]);

  const hasConversation = messages.length > 0;

  const statusMessage = useMemo(() => {
    if (isHistoryLoading) return t("history.loading");
    if (isUploading) return t("status.uploading");
    if (isSubmitting) return t("status.thinking");
    if (files.length > 0)
      return t("status.filesReady", { count: files.length });
    return null;
  }, [files.length, isHistoryLoading, isSubmitting, isUploading, t]);

  async function handleSubmit() {
    const trimmedQuery = query.trim();
    if (!trimmedQuery || isSubmitting || isUploading) return;

    setError(null);

    const userMessage: ChatMessage = {
      id: crypto.randomUUID(),
      role: "user",
      content: trimmedQuery,
      timestamp: new Date().toISOString(),
    };

    setMessages((current) => [...current, userMessage]);
    setQuery("");

    try {
      if (files.length > 0) {
        setIsUploading(true);
        await processUploadedPdfDocuments(files);
        setFiles([]);
      }

      setIsUploading(false);
      setIsSubmitting(true);

      const response = await submitChatQuery(trimmedQuery, selectedModel);

      const assistantMessage: ChatMessage = {
        id: crypto.randomUUID(),
        role: "assistant",
        content: response.data.answer,
        sources: response.data.source_docs ?? [],
        timestamp: new Date().toISOString(),
      };

      setMessages((current) => [...current, assistantMessage]);
    } catch (error) {
      setError(error instanceof Error ? error.message : t("status.failed"));

      setMessages((current) => [
        ...current,
        {
          id: crypto.randomUUID(),
          role: "system",
          content: t("status.failed"),
          timestamp: new Date().toISOString(),
        },
      ]);
    } finally {
      setIsUploading(false);
      setIsSubmitting(false);
    }
  }

  const activityMessage = (
    <>
      {statusMessage && (
        <p className="chat-page__status" role="status">
          {statusMessage}
        </p>
      )}

      {error && (
        <p className="chat-page__error" role="alert">
          {error}
        </p>
      )}
    </>
  );

  const composer = (
    <ChatComposer
      value={query}
      files={files}
      isSubmitting={isSubmitting}
      isUploading={isUploading}
      onChange={setQuery}
      onFilesChange={setFiles}
      onSubmit={handleSubmit}
    />
  );

  const modelBar = (
    <ChatModelBar
      selectedModel={selectedModel}
      onModelChange={setSelectedModel}
      onToggleSystemInfo={() => setIsSystemInfoOpen(true)}
    />
  );

  return (
    <section
      className={
        hasConversation
          ? "chat-page chat-page--conversation"
          : "chat-page chat-page--empty"
      }
    >
      {!hasConversation && (
        <>
          <div className="chat-page__empty-main">
            <h1>{t("heading")}</h1>

            <div className="chat-page__empty-composer">
              {activityMessage}
              {composer}
            </div>
          </div>

          <div className="chat-page__model-dock">{modelBar}</div>
        </>
      )}

      {hasConversation && (
        <>
          <div className="chat-page__messages">
            <ChatMessageList messages={messages} />
          </div>

          <div className="chat-page__bottom-dock">
            <div className="chat-page__bottom-inner">
              {activityMessage}
              {composer}
              {modelBar}
            </div>
          </div>
        </>
      )}

      {isSystemInfoOpen && (
        <ChatSystemInfoPanel
          selectedModel={selectedModel}
          onClose={() => setIsSystemInfoOpen(false)}
        />
      )}
    </section>
  );
}
