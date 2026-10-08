# Shared headers helper with Accept-Language
import streamlit as st

def auth_headers(token: str | None = None) -> dict:
    
    headers = {
        "Accept-Language": st.session_state.get("lang", "en")
    }
    
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    print(f"✅ HTTP Headers: {headers}")
    
    return headers
