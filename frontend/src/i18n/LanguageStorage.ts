// frontend/src/i18n/LanguageStorage.ts

import type { SupportedLanguage } from "@/i18n/i18n";

const LANGUAGE_KEY = "kiko.lang";

export function getStoredLanguage(): SupportedLanguage {
  const stored = localStorage.getItem(LANGUAGE_KEY);

  if (stored === "de" || stored === "en") {
    return stored;
  }

  return "en";
}

export function storeLanguage(language: SupportedLanguage): void {
  localStorage.setItem(LANGUAGE_KEY, language);
}
