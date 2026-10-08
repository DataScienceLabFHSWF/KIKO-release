// frontend/src/features/chat/components/ChatSystemInfoPanel.tsx

import { Brain, Cpu, Eye, Flame, Monitor, Puzzle, X, Zap } from "lucide-react";
import { useEffect } from "react";
import { useTranslation } from "node_modules/react-i18next";
import { IconButton } from "@/components";
import { DEFAULT_EMBEDDING_MODEL } from "../types/Chat";
import "./ChatSystemInfoPanel.css";

type ChatSystemInfoPanelProps = {
  selectedModel: string;
  onClose: () => void;
};

export function ChatSystemInfoPanel({
  selectedModel,
  onClose,
}: ChatSystemInfoPanelProps) {
  const { t } = useTranslation("chatAssistant");

  useEffect(() => {
    function handleKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape") {
        onClose();
      }
    }

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [onClose]);

  return (
    <div className="chat-system-info-backdrop" role="presentation">
      <aside
        className="chat-system-info"
        role="dialog"
        aria-modal="true"
        aria-label={t("system.title")}
      >
        <header>
          <strong>{t("system.title")}</strong>

          <IconButton
            variant="plain"
            label={t("actions.close")}
            icon={<X size={16} strokeWidth={2.4} />}
            onClick={onClose}
          />
        </header>

        <div className="chat-system-info__content">
          <section className="chat-system-info__section">
            <p>{t("system.aiModels")}</p>

            <div className="chat-system-info__card">
              <Eye size={16} />
              {t("system.advancedVlm")}
            </div>

            <div className="chat-system-info__card">
              <Puzzle size={16} />
              {t("system.trocr")}
            </div>

            <div className="chat-system-info__card">
              <Monitor size={16} />
              {t("system.opencv")}
            </div>
          </section>

          <section className="chat-system-info__section">
            <p>{t("system.embeddingAndLlm")}</p>

            <div className="chat-system-info__card">
              <Zap size={16} />
              {t("system.embeddingModel")}: {DEFAULT_EMBEDDING_MODEL}
            </div>

            <div className="chat-system-info__card">
              <Brain size={16} />
              {t("system.largeLanguageModel")}: {selectedModel}
            </div>
          </section>

          <section className="chat-system-info__section">
            <p>{t("system.runtime")}</p>

            <div className="chat-system-info__card">
              <Cpu size={16} />
              Python / PyTorch / CUDA
            </div>

            <div className="chat-system-info__card">
              <Flame size={16} />
              NVIDIA H200 NVL
            </div>
          </section>
        </div>
      </aside>
    </div>
  );
}
