import os, streamlit as st, requests, logging
from dotenv import load_dotenv
from pages import render_sidebar
from utils import format_date, require_login
from i18n import translate
from topbar import language_topbar

logger = logging.getLogger(__name__)

# set page configuration
st.set_page_config(page_title="Profile", page_icon="👤", layout="wide")

# Check if the user is logged in
require_login()

# Load API URL from environment variables
load_dotenv()
BACKEND_API_URL = os.getenv("BACKEND_API_URL")

# check if BACKEND_API_URL is set
if not BACKEND_API_URL:
    st.error(translate("error.env"))
    st.stop()

# Always show top-right language switch
language_topbar()

# declare headers for API requests
headers={"Authorization": f"Bearer {st.session_state.token}"}

# Render the sidebar
render_sidebar()

################################
# User Profile
################################
st.title(translate("profile.pageTitle"))
st.markdown(translate("profile.subtitle"))
st.divider()

# Fetch user profile information
response = requests.get(f"{BACKEND_API_URL}/api/profile/user_info", headers=headers)

if response.status_code != 200:
    st.error(translate("profile.errors.loadFailed"))
    st.session_state.clear()
    st.stop()

profile = response.json()
print(f"ℹ️ FE User profile:{profile}")

# 🔳 Left: Avatar + Basic Info
# col1, col2 = st.columns([1, 3])

# with col1:
st.image(profile.get("avatar", ""), width=150)
st.markdown(f"👤 {translate('profile.leftCard.fullName')}: {profile['full_name']}")
# st.markdown(f"@ {translate('profile.leftCard.username')}: **{profile['username']}**")
st.markdown(f"📧 {translate('profile.leftCard.email')}: {profile['email']}")
# st.markdown(f"🎂 {translate('profile.leftCard.dob')}: {profile['date_of_birth']}")
st.markdown(f"🧑‍🎓 {translate('profile.leftCard.role')}: **{profile['role']}**")
st.markdown(f"📅 {translate('profile.leftCard.joined')}: {format_date(profile['joined'])}")
st.markdown(f"📅 {translate('profile.leftCard.lastLogin')}: {format_date(profile['last_login'])}")

# with col2:
#     st.subheader(translate('profile.bio.title'))
#     st.write(profile.get("bio", translate('profile.bio.empty')))
