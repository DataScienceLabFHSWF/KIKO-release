// frontend/src/features/chat/components/ChatMessageList.tsx

import { Bot, BookOpen, Download, FileText, UserRound } from "lucide-react";
import { useMemo, useState } from "react";
import { useTranslation } from "node_modules/react-i18next";
import { Button, MarkdownView } from "@/components";
import type { ChatMessage, ChatSourceDocument } from "../types/Chat";
import {
  downloadAssistantMessageAsMarkdown,
  downloadSourceSnippetAsMarkdown,
} from "../utils/chatDownload";
import "./ChatMessageList.css";

type ChatMessageListProps = {
  messages: ChatMessage[];
};

function getSourceTitle(source: ChatSourceDocument) {
  return source.source ?? source.title ?? "Unknown source";
}

function getSourceKey(source: ChatSourceDocument, index: number) {
  const textKey = source.retrieved_chunks?.trim().slice(0, 300) ?? "";
  return [
    source.content_hash,
    source.document_id,
    source.module_id,
    source.module_title,
    textKey,
    index,
  ]
    .filter(Boolean)
    .join("-");
}

function dedupeSources(sources: ChatSourceDocument[]) {
  const seen = new Set<string>();

  return sources.filter((source) => {
    const duplicateKey = [
      source.content_hash ?? "",
      source.document_id ?? "",
      source.module_id ?? "",
      source.retrieved_chunks?.trim() ?? "",
    ].join("::");

    if (seen.has(duplicateKey)) return false;

    seen.add(duplicateKey);
    return true;
  });
}

function SourceList({ sources }: { sources: ChatSourceDocument[] }) {
  const { t } = useTranslation("chatAssistant");

  const uniqueSources = useMemo(() => dedupeSources(sources), [sources]);

  return (
    <div className="chat-message__sources">
      {uniqueSources.map((source, index) => (
        <section
          key={getSourceKey(source, index)}
          className="chat-message__source-card"
        >
          <div className="chat-message__source-header">
            <div>
              <strong>{getSourceTitle(source)}</strong>

              {source.module_title && <span>{source.module_title}</span>}
            </div>

            {source.retrieved_chunks && (
              <Button
                type="button"
                variant="ghost"
                size="sm"
                onClick={() => downloadSourceSnippetAsMarkdown(source)}
              >
                <Download size={14} strokeWidth={2.3} aria-hidden="true" />
                {t("actions.download")}
              </Button>
            )}
          </div>

          {source.retrieved_chunks && (
            <div className="chat-message__source-content">
              <MarkdownView content={source.retrieved_chunks} />
            </div>
          )}
        </section>
      ))}
    </div>
  );
}

export function ChatMessageList({ messages }: ChatMessageListProps) {
  const { t } = useTranslation("chatAssistant");
  const [openMessageId, setOpenMessageId] = useState<string | null>(null);

  if (messages.length === 0) return null;

  return (
    <div className="chat-message-list">
      {messages.map((message) => {
        const sources = message.sources ?? [];
        const hasSources = sources.length > 0;
        const isOpen = openMessageId === message.id;
        const isAssistant = message.role === "assistant";
        const isUser = message.role === "user";

        return (
          <article
            key={message.id}
            className={`chat-message chat-message--${message.role}`}
          >
            <div className="chat-message__icon" aria-hidden="true">
              {isUser ? (
                <UserRound size={17} strokeWidth={2.2} />
              ) : (
                <Bot size={17} strokeWidth={2.2} />
              )}
            </div>

            <div className="chat-message__body">
              <div className="chat-message__content">
                {isAssistant ? (
                  <MarkdownView content={message.content} />
                ) : (
                  <p>{message.content}</p>
                )}
              </div>

              {isAssistant && (
                <div className="chat-message__actions">
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    onClick={() =>
                      downloadAssistantMessageAsMarkdown(message.content)
                    }
                  >
                    <Download size={14} strokeWidth={2.3} aria-hidden="true" />
                    {t("actions.download")}
                  </Button>

                  {hasSources && (
                    <Button
                      type="button"
                      variant={isOpen ? "primary" : "ghost"}
                      size="sm"
                      aria-expanded={isOpen}
                      onClick={() =>
                        setOpenMessageId(isOpen ? null : message.id)
                      }
                    >
                      <BookOpen
                        size={14}
                        strokeWidth={2.3}
                        aria-hidden="true"
                      />
                      {isOpen
                        ? t("sources.hide", { count: sources.length })
                        : t("sources.show", { count: sources.length })}
                    </Button>
                  )}
                </div>
              )}

              {isAssistant && hasSources && isOpen && (
                <SourceList sources={sources} />
              )}

              {message.role === "system" && (
                <div className="chat-message__actions">
                  <FileText size={14} strokeWidth={2.3} aria-hidden="true" />
                  <span>{t("status.systemMessage")}</span>
                </div>
              )}
            </div>
          </article>
        );
      })}
    </div>
  );
}
