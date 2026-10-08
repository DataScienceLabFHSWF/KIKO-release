import os, streamlit as st, requests, logging
from dotenv import load_dotenv
from pages import render_sidebar
from utils import format_date, require_login
from i18n import translate
from topbar import language_topbar

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
    st.error(translate("learnerDashboard.errors.envMissing"))
    st.stop()

# Always show top-right language switch
language_topbar()

# Declare headers for API requests
headers = {"Authorization": f"Bearer {st.session_state.token}"}

# Render the sidebar
render_sidebar()

################################
# Learner dashboard
################################
st.title(translate("learnerDashboard.pageTitle"))
st.markdown(translate("learnerDashboard.subtitle"))
st.divider()

################################
# Analytics section
################################
st.subheader(translate("learnerDashboard.sections.stats.title"))
st.markdown(translate("learnerDashboard.sections.stats.desc"))

# Fetch learner statistics
response = requests.get(
        f"{BACKEND_API_URL}/api/learner/statistics",
        headers=headers,
)
if response.status_code == 200:
    stats = response.json()
    
    col1, col2, col3 = st.columns(3)
    col1.metric(translate("learnerDashboard.metrics.coursesEnrolled"), stats["courses_enroll"])
    col2.metric(translate("learnerDashboard.metrics.coursesInProgress"),stats['courses_inprogress'])
    col3.metric(translate("learnerDashboard.metrics.coursesCompleted"), stats["courses_completed"])
    st.progress(stats['courses_progress_percent'] / 100)

    col4, col5, col6 = st.columns(3)
    col4.metric(translate("learnerDashboard.metrics.examsPassed"), stats["exams_passed"])
    col5.metric(translate("learnerDashboard.metrics.examsFailed"), stats["exams_failed"])
    col6.metric(translate("learnerDashboard.metrics.examsInProgress"), stats["exams_inprogress"])

    col7, col8 = st.columns(2)
    col7.metric(translate("learnerDashboard.metrics.questionsAsked"), stats["questions_asked"])
    col8.metric(translate("learnerDashboard.metrics.lastLogin"), format_date(stats["last_activity"]))
else:
    st.error(translate("learnerDashboard.errors.statsFetch", detail=response.json().get('detail')))
