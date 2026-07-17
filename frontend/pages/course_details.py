# frontend/pages/course_details.py
import os, requests, streamlit as st, logging
from dotenv import load_dotenv
from utils import (require_login, get_backend_app_config_library)
from pages import render_sidebar
from i18n import translate
from topbar import language_topbar
from components import render_course_experience
from http_headers import auth_headers

logger = logging.getLogger(__name__)

st.set_page_config(page_title="Course Details", page_icon="📘", layout="wide")

require_login()

load_dotenv()
BACKEND_API_URL = os.getenv("BACKEND_API_URL")

if not BACKEND_API_URL:
    st.error(translate("courseDetails.errors.envMissing"))
    st.stop()

# Always show top-right language switch
language_topbar()

token = st.session_state.token

header = {"Authorization": f"Bearer {token}"}

auth_header = auth_headers(token)

# ---------- State
course_id = st.session_state.get("view_course_id")

if not course_id:
    st.warning(translate("courseDetails.warnings.noCourseSelected"))
    st.switch_page("pages/my_courses.py")
    st.stop()

state_prefix = f"learner_course_{course_id}"

st.session_state.setdefault("confirm_enroll", False)
st.session_state.setdefault("confirm_unenroll", False)

def _clear_course_state(prefix: str) -> None:
    st.session_state.pop(f"{prefix}_progress_snapshot", None)
    st.session_state.pop(f"{prefix}_nav", None)
    st.session_state.pop(f"{prefix}_nav_radio", None)

def fetch_course_details(api_base: str, h: dict, cid: int):
    response = requests.get(f"{api_base}/api/learner/courses/{cid}", headers=h)
    if not response.ok:
        detail = None
        try:
            detail = response.json().get("detail")
        except Exception:
            detail = response.text
        raise RuntimeError(
            translate(
                "courseDetails.errors.loadFailedWithDetails", 
                cid=cid, 
                details=detail or response.status_code
            )
        )
    return response.json()

def enroll_course(api_base: str, h: dict, cid: int) -> bool:
    response = requests.post(f"{api_base}/api/learner/courses/{cid}/enroll", headers=h)
    return response.status_code in (200, 201, 204)

def unenroll_course(api_base: str, h: dict, cid: int) -> bool:
    response = requests.delete(f"{api_base}/api/learner/courses/{cid}/enrollment", headers=h)
    return response.status_code in (200, 204)

# ---------- Dialogs
@st.dialog(translate("courseDetails.dialogs.enroll.title"))
def confirm_enroll_dialog():
    st.write(translate("courseDetails.dialogs.enroll.body"))
    c1, c2 = st.columns(2)
    
    if c1.button(
        translate("courseDetails.dialogs.enroll.yes.label"), 
        type="primary", 
        key="enroll_yes", 
        width='stretch', 
        help=translate("courseDetails.dialogs.enroll.yes.help")
    ):
        ok = enroll_course(BACKEND_API_URL, header, course_id)
        if ok:
            st.toast(translate("courseDetails.toasts.enrolled"), icon="🎓")
            _clear_course_state(state_prefix)
        else:
            st.error(translate("courseDetails.errors.enrollFailed"))
        
        st.session_state.confirm_enroll = False
        st.rerun()
    
    if c2.button(
        translate("courseDetails.dialogs.enroll.no.label"),
        type="primary", 
        key="enroll_no", 
        width='stretch', 
        help=translate("courseDetails.dialogs.enroll.no.help")
    ):
        st.session_state.confirm_enroll = False
        st.rerun()

@st.dialog(translate("courseDetails.dialogs.unenroll.title"))
def confirm_unenroll_dialog():
    st.write(translate("courseDetails.dialogs.unenroll.body"))
    c1, c2 = st.columns(2)
    
    if c1.button(
        translate("courseDetails.dialogs.unenroll.yes.label"), 
        type="primary", 
        key="unenroll_yes", 
        width='stretch', 
        help=translate("courseDetails.dialogs.unenroll.yes.help")
    ):
        ok = unenroll_course(BACKEND_API_URL, header, course_id)
        if ok:
            st.toast(translate("courseDetails.toasts.unenrolled"), icon="🧹")
            _clear_course_state(state_prefix)
        else:
            st.error(translate("courseDetails.errors.unenrollFailed"))
        
        st.session_state.confirm_unenroll = False
        st.rerun()
    
    if c2.button(
        translate("courseDetails.dialogs.unenroll.no.label"), 
        type="primary", 
        key="unenroll_no", 
        width='stretch', 
        help=translate("courseDetails.dialogs.unenroll.no.help")
    ):
        st.session_state.confirm_unenroll = False
        st.rerun()

# Render the sidebar (course list, profile, etc.) 
render_sidebar()

app_config_library_data = get_backend_app_config_library(BACKEND_API_URL, header)
if not app_config_library_data:
    st.error(translate("courseGenerator.errors.emptyConfig"))
    st.stop()

app_config_data = app_config_library_data.get("app_config")

default_reasoning_model = app_config_data.get("default_reasoning_model")

# Single-line toolbar: Back | Refresh | Enroll/Unenroll
toolbar = st.columns([1, 1, 1, 5])
if toolbar[0].button(
    translate("courseDetails.toolbar.back.label"), 
    width='stretch', 
    type="primary", 
    help=translate("courseDetails.toolbar.back.help")
):
    st.switch_page("pages/my_courses.py")

if toolbar[1].button(
    translate("courseDetails.toolbar.refresh.label"), 
    width='stretch', 
    type="primary", 
    help=translate("courseDetails.toolbar.refresh.help")
):
    _clear_course_state(state_prefix)
    st.rerun()

try:
    details = fetch_course_details(BACKEND_API_URL, header, course_id)
except Exception as e:
    st.error(translate("courseDetails.errors.loadFailed", details=str(e)))
    st.stop()

course_json = details.get("course_json") or {}
enrollment = details.get("enrollment") or {}
progress_snapshot = details.get("progress_snapshot") or {}
attempt_summaries = details.get("attempt_summaries") or {}

is_enrolled = bool(
    enrollment.get("is_enrolled")
    or enrollment.get("enrolled")
    or enrollment.get("status") == "enrolled"
)

course_completion = (progress_snapshot or {}).get("course_completion") or {}
completion_percent = float((progress_snapshot or {}).get("completion_percent") or 0.0)

is_completed = bool(course_completion.get("completed")) or completion_percent >= 100.0

if not is_enrolled:
    progress_snapshot = {}
    attempt_summaries = {}

# Enroll/Unenroll on the same row as Back/Refresh
if is_completed:
    toolbar[2].button(
        translate("courseDetails.actions.completed.label"),
        type="primary",
        disabled=True,
        width="stretch",
        help=translate("courseDetails.actions.completed.help"),
    )
elif is_enrolled:
    if toolbar[2].button(
        translate("courseDetails.actions.unenroll.label"), 
        type="primary", 
        width='stretch', 
        help=translate("courseDetails.actions.unenroll.help")
    ):
        st.session_state.confirm_unenroll = True
else:
    if toolbar[2].button(
        translate("courseDetails.actions.enroll.label"), 
        type="primary", 
        width='stretch', 
        help=translate("courseDetails.actions.enroll.help")
    ):
        st.session_state.confirm_enroll = True

st.divider()

if st.session_state.confirm_enroll:
    confirm_enroll_dialog()

if st.session_state.confirm_unenroll:
    confirm_unenroll_dialog()

if not course_json:
    st.error(translate("courseDetails.errors.noCourseJson"))
    st.stop()

render_course_experience(
    course_json=course_json,
    mode="learner",
    state_prefix=state_prefix,
    show_sidebar_nav=True,
    api_base=BACKEND_API_URL,
    request_headers= header,
    auth_headers=auth_header,
    course_id=course_id,
    progress_snapshot=progress_snapshot,
    attempt_summaries=attempt_summaries,
    reasoning_model_name=default_reasoning_model,
    is_enrolled=is_enrolled
)
