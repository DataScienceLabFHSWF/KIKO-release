import os, streamlit as st, logging
from dotenv import load_dotenv
from pages import render_sidebar
from utils import require_login

logger = logging.getLogger(__name__)

# set page configuration
st.set_page_config(page_title="Admin Panel", page_icon="🧩", layout="wide")

# Check if the user is logged in
require_login()

# Load API URL from environment variables
load_dotenv()
BACKEND_API_URL = os.getenv("BACKEND_API_URL")

# check if BACKEND_API_URL is set
if not BACKEND_API_URL:
    st.error("❌ BACKEND_API_URL not set in environment.")
    st.stop()

# declare headers for API requests
headers = {"Authorization": f"Bearer {st.session_state.token}"}

# Render the sidebar
render_sidebar()

################################
# Admin actions section
################################
st.title("🧩 Admin Panel")
st.markdown("Manage users, monitor system health, and perform administrative tasks.")
st.divider()
