// frontend/src/components/molecules/LanguageSwitch/LanguageSwitch.tsx

import { useTranslation } from "node_modules/react-i18next";
import { Button } from "@/components";
import { storeLanguage } from "@/i18n/LanguageStorage";
import type { SupportedLanguage } from "@/i18n/i18n";
import "./LanguageSwitch.css";

export function LanguageSwitch() {
  const { i18n } = useTranslation();

  const currentLanguage: SupportedLanguage = i18n.language.startsWith("de")
    ? "de"
    : "en";

  const nextLanguage: SupportedLanguage =
    currentLanguage === "en" ? "de" : "en";

  async function handleSwitchLanguage() {
    await i18n.changeLanguage(nextLanguage);
    storeLanguage(nextLanguage);
  }

  return (
    <Button
      type="button"
      variant="plain"
      size="sm"
      className="language-switch"
      onClick={handleSwitchLanguage}
    >
      {currentLanguage === "en" ? "English" : "Deutsch"}
    </Button>
  );
}
