# i18n is the process of designing and building software or a product so it can be easily adapted 
# for different languages and cultures without requiring engineering changes.
# The term is a numeronym for "internationalization," where the number 18 represents the letters between the "i" and the "n".
import json, streamlit as st
from pathlib import Path
from typing import Any, Dict

# Where your JSON files live:
# e.g. frontend/assets/locales/en.json & de.json
_LOCALES_DIR = Path(__file__).resolve().parent / "assets" / "locales"

print(f"Locales directory: {_LOCALES_DIR}")

def _safe_lang(lang: str | None) -> str:
    if not lang:
        return "en"
    return "de" if lang.lower().startswith("de") else "en"

@st.cache_data(show_spinner=False)
def _load_locale(lang: str) -> Dict[str, Any]:
    lang = _safe_lang(lang)
    fname = _LOCALES_DIR / f"{lang}.json"
    if not fname.exists():
        # hard fallback to English
        fallback = _LOCALES_DIR / "en.json"
        if fallback.exists():
            return json.loads(fallback.read_text(encoding="utf-8"))
        return {}  # last resort
    return json.loads(fname.read_text(encoding="utf-8"))

def _deep_get(d: Dict[str, Any], dotted: str) -> Any:
    cur = d
    for part in dotted.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return None
        cur = cur[part]
    return cur

def translate(key: str, **fmt) -> str:
    """
    Translate a dotted key using the current session language.
    Falls back to English, then to the key itself.
    """
    # Ensure a default language is set even on the login page (no sidebar yet)
    st.session_state.setdefault("lang", "en")
    cur_lang = _safe_lang(st.session_state.get("lang", "en"))

    cur = _load_locale(cur_lang)
    val = _deep_get(cur, key)

    if val is None and cur_lang != "en":
        # fallback to English if missing in the selected lang
        fallback = _load_locale("en")
        val = _deep_get(fallback, key)

    if val is None:
        # final fallback: show the key (what you currently see)
        val = key

    if isinstance(val, str) and fmt:
        try:
            return val.format(**fmt)
        except Exception:
            return val
    return val if isinstance(val, str) else str(val)
