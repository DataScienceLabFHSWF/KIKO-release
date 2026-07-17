# Main frontend app file (Streamlit)
import streamlit as st, logging
from utils import require_login
from i18n import translate
from topbar import language_topbar

logger = logging.getLogger(__name__)

# set page configuration
st.set_page_config(page_title="KIKO Platform", page_icon="🧠", layout="wide")

# Check if the user is logged in
require_login()

# keep language control visible on dashboard redirect page
language_topbar()

user_role = st.session_state.get("role", "")

# Redirect to correct dashboard based on role
if user_role == "Learner":
    st.switch_page("pages/learner_dashboard.py")
elif user_role == "Instructor":
    st.switch_page("pages/instructor_courses.py")
elif user_role == "Admin":
    st.switch_page("pages/admin_dashboard.py")
else:
    st.error(translate("main.role.invalid"))
    st.stop()
