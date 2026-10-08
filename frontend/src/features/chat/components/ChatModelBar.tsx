// frontend/src/features/chat/components/ChatModelBar.tsx

import { Info } from "lucide-react";
import { useTranslation } from "node_modules/react-i18next";
import { Button } from "@/components";
import { CHAT_LLM_OPTIONS, type ChatLlmModel } from "../types/Chat";
import "./ChatModelBar.css";

type ChatModelBarProps = {
  selectedModel: ChatLlmModel;
  onModelChange: (model: ChatLlmModel) => void;
  onToggleSystemInfo: () => void;
};

export function ChatModelBar({
  selectedModel,
  onModelChange,
  onToggleSystemInfo,
}: ChatModelBarProps) {
  const { t } = useTranslation("chatAssistant");

  return (
    <footer className="chat-model-bar">
      <label className="chat-model-bar__group">
        <span>{t("footer.llm")}</span>
        <select
          value={selectedModel}
          onChange={(event) =>
            onModelChange(event.currentTarget.value as ChatLlmModel)
          }
        >
          {CHAT_LLM_OPTIONS.map((model) => (
            <option key={model} value={model}>
              {model}
            </option>
          ))}
        </select>
      </label>

      <Button
        type="button"
        variant="ghost"
        size="sm"
        className="chat-model-bar__system-button"
        onClick={onToggleSystemInfo}
      >
        <Info size={15} strokeWidth={2.2} />
        {t("footer.sysInformation")}
      </Button>
    </footer>
  );
}
