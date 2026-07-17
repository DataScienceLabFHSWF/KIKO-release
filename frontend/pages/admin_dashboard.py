import os, streamlit as st, requests, pandas as pd, logging
from dotenv import load_dotenv
from pages import render_sidebar
from utils import format_date, require_login

logger = logging.getLogger(__name__)

# Set page configuration
st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")

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
# Admin dashboard
################################
st.title("📊 Admin Dashboard")
st.markdown("Welcome to your personalized admin dashboard.")
st.divider()

################################
# Analytics section
################################
st.subheader("📈 System Statistics")
st.markdown("Here you can monitor the system's performance and user engagement.")

# Fetch system statistics
response = requests.get(
        f"{BACKEND_API_URL}/api/admin/stats",
        headers=headers,
)
if response.status_code == 200:
    stats = response.json()

    col1, col2, col3 = st.columns(3)
    col1.metric("Documents Uploaded", stats["documents_uploaded"])
    col2.metric("Users Registered", stats["users_registered"])
    col3.metric("Pipelines Status", stats["pipelines_status"])

    col4, col5 = st.columns(2)
    col4.metric("System Uptime", stats["system_uptime"])
    col5.metric("Last Activity", format_date(stats["last_activity"]))
else:
    st.error("❌ Access denied or error fetching stats")

st.divider()
################################
# Upload documents logs
################################
st.subheader("📂 Document Uploaded Logs")
st.markdown("View the logs of document uploads and user activities.")

# Fetch document upload logs
response = requests.get(
        f"{BACKEND_API_URL}/api/admin/logs",
        headers=headers,
)
if response.status_code == 200:
    df = pd.DataFrame(response.json())
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    st.dataframe(df)
else:
    st.error("❌ Failed to load document logs")
