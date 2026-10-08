import os, streamlit as st, requests, logging, pandas as pd, plotly.express as px
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

# Declare headers for API requests
headers = {"Authorization": f"Bearer {st.session_state.token}"}

# Render the sidebar
render_sidebar()

################################
# Instructor dashboard
################################
st.title("🧑‍🏫 Instructor Dashboard")
st.markdown("Welcome to your personalized instructor dashboard.")
st.divider()

################################
# Analytics section
################################
st.subheader("📈 Instructor Statistics")
st.markdown("Here you can monitor your performance and student engagement.")

# Fetch instructor statistics
response = requests.get(
        f"{BACKEND_API_URL}/api/instructor/statistics",
        headers=headers,
)
if response.status_code == 200:
    stats = response.json()
    col1, col2, col3 = st.columns(3)
    col1.metric("👩‍🎓 Students Enrolled", stats["students"])
    col2.metric("📘 Courses Created", stats["courses_created"])
    col3.metric("❓ Questions Asked to chat assistant", stats["questions_asked"])

    col4, col5 = st.columns(2)
    col4.metric("❓ Learner Questions", stats["learner_questions"])
    col5.metric("🕒 Last time login", format_date(stats["last_activity"]))
else:
    st.error("❌ Access denied or error fetching statistics.")

st.divider()
################################
# Learner activity section
################################
st.subheader("📊 Learner Activity")
st.markdown("View the activity of your learners.")

# Fetch learner activity logs
response = requests.get(
        f"{BACKEND_API_URL}/api/instructor/queries",
        headers=headers,
)
if response.status_code == 200:
    data = response.json()
    df = pd.DataFrame(data)
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    fig = px.histogram(df, x="timestamp", color="username", title="Questions Asked Over Time")
    st.plotly_chart(fig)
else:
    st.error("❌ Failed to load query logs.")
