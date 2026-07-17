# Always-visible language switch (top-right)
import streamlit as st
from i18n import translate

def language_topbar():
    # Provide a default BEFORE rendering anything else
    st.session_state.setdefault("lang", "en")
    current = st.session_state["lang"]

    # simple right-aligned control
    cols = st.columns([1,1,1,1,1,1,1,1,1,1,1,2])
    
    with cols[-1]:
        label = translate("topbar.language")
        
        options = {
            "en": translate("topbar.lang.en"),
            "de": translate("topbar.lang.de"),
        }
        
        # show labels, keep code mapping
        display = {options[k]: k for k in options}
        chosen_label = st.selectbox(label, list(display.keys()), index=0 if current=="en" else 1)
        chosen_code = display[chosen_label]
        if chosen_code != current:
            st.session_state["lang"] = chosen_code
            st.rerun()
