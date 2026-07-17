#  Auth Utility functions for the KIKO platform frontend.
#  These functions handle user authentication, token management, and session validation.
#  They ensure that users are logged in and that their session tokens are valid.
#  They also provide a way to store and retrieve user tokens securely.
#  The functions are used across the frontend to manage user sessions and access protected resources.
#  They are essential for maintaining a secure and user-friendly experience on the platform.

import os, streamlit as st, logging, requests, json
from dotenv import load_dotenv
from time import sleep

logger = logging.getLogger(__name__)

# Load API URL from environment variables
load_dotenv()
BACKEND_API_URL = os.getenv("BACKEND_API_URL")

def is_token_valid(token: str) -> bool:
    """Check if the provided token is valid by making a request to the backend."""

    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BACKEND_API_URL}/api/profile/user_info", headers=headers)
        print(f"ℹ️ Token validation response: {response.status_code}")
        return response.status_code == 200
    except Exception:
        print("❌ Error validating token.")
        return False

def require_login():
    """Ensure the user is logged in by checking the session state and token validity."""

    if "token" not in st.session_state:
        print("❌ No token found in session state or file. Redirecting to login page.")
        st.error("🔐 Login required. Redirecting to login page.")
        sleep(0.5)
        st.switch_page("pages/login.py")
        st.stop()
    
    if not is_token_valid(st.session_state.token):
        print("❌ Invalid or expired token.")
        st.error("🔐 Invalid or expired session. Please log in again. Redirecting to login page.")
        st.session_state.clear()
        sleep(0.5)
        st.switch_page("pages/login.py")
        st.stop()
