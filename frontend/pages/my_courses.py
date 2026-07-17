# frontend/pages/my_courses.py
import os, streamlit as st, logging, requests, textwrap, re
from dotenv import load_dotenv
from pages import render_sidebar
from utils import require_login
from i18n import translate
from topbar import language_topbar

logger = logging.getLogger(__name__)

# set page configuration
st.set_page_config(page_title="My Courses", page_icon="📚", layout="wide")

# Check if the user is logged in
require_login()

# Always show top-right language switch
language_topbar()

# Load API URL from environment variables
load_dotenv()
BACKEND_API_URL = os.getenv("BACKEND_API_URL")

# check if BACKEND_API_URL is set
if not BACKEND_API_URL:
    st.error(translate("myCourses.errors.envMissing"))
    st.stop()

# declare headers for API requests
headers = {"Authorization": f"Bearer {st.session_state.token}"}
CACHE_TTL_SECONDS = 30

# Render the sidebar
render_sidebar()

# ----- Session flags for dialogs
st.session_state.setdefault("confirm_enroll_course_id", None)
st.session_state.setdefault("confirm_unenroll_course_id", None)
st.session_state.setdefault("confirm_dismiss_reco_course_id", None)

def strip_markdown_formatting(text: str) -> str:
    text = re.sub(r"^#+\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"^>\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"\*(.+?)\*", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    return text.strip()

def _safe_percent(value) -> int:
    try:
        return max(0, min(100, int(round(float(value or 0)))))
    except Exception:
        return 0

def _clear_course_list_caches():
    fetch_enrolled.clear()
    fetch_recommended.clear()
    fetch_all_courses.clear()

# ----- API helpers
@st.cache_data(ttl=CACHE_TTL_SECONDS, show_spinner=False)
def fetch_enrolled(api_base: str, headers: dict):
    response = requests.get(f"{api_base}/api/learner/courses/enrolled", headers=headers)
    response.raise_for_status()
    return response.json()

@st.cache_data(ttl=CACHE_TTL_SECONDS, show_spinner=False)
def fetch_recommended(api_base: str, headers: dict):
    response = requests.get(f"{api_base}/api/learner/courses/recommended", headers=headers)
    response.raise_for_status()
    return response.json()

@st.cache_data(ttl=CACHE_TTL_SECONDS, show_spinner=False)
def fetch_all_courses(api_base: str, headers: dict):
    response = requests.get(f"{api_base}/api/learner/courses/all", headers=headers)
    response.raise_for_status()
    return response.json()

def enroll(course_id: int):
    response = requests.post(
        f"{BACKEND_API_URL}/api/learner/courses/{course_id}/enroll", 
        headers=headers
    )

    if response.status_code not in (200, 201, 204):
        try:
            detail = response.json().get("detail")
        except Exception:
            detail = None
        st.error(detail or translate("myCourses.errors.enrollFailed", status=response.status_code))
        return
    
    st.toast(translate("myCourses.toasts.enrolled"), icon="🎓")
    _clear_course_list_caches()

def unenroll(course_id: int):
    response = requests.delete(
        f"{BACKEND_API_URL}/api/learner/courses/{course_id}/enrollment", 
        headers=headers
    )
    
    if response.status_code not in (200, 204):
        try:
            detail = response.json().get("detail")
        except Exception:
            detail = None
        st.error(detail or translate("myCourses.errors.unenrollFailed", status=response.status_code))
        return
    
    st.toast(translate("myCourses.toasts.unenrolled"), icon="🧹")
    _clear_course_list_caches()

def dismiss_recommendation(course_id: int):
    response = requests.delete(
        f"{BACKEND_API_URL}/api/learner/courses/recommended/{course_id}", 
        headers=headers
    )
    
    if response.status_code not in (200, 204):
        try:
            detail = response.json().get("detail")
        except Exception:
            detail = None
        st.error(detail or translate("myCourses.errors.dismissFailed", status=response.status_code))
        return
    
    st.toast(translate("myCourses.toasts.dismissed"), icon="🧽")
    fetch_recommended.clear()

def go_to_details(course_id: int):
    st.session_state.view_course_id = course_id
    st.switch_page("pages/course_details.py")

# ----- Dialogs
@st.dialog(translate("myCourses.dialogs.enroll.title"))
def confirm_enroll_dialog():
    cid = st.session_state.confirm_enroll_course_id
    st.write(translate("myCourses.dialogs.enroll.body", id=cid))
    c1, c2 = st.columns(2)
    
    if c1.button(
        translate("myCourses.dialogs.enroll.yes.label"), 
        type="primary", 
        key=f"enroll_yes_{cid}", 
        width="stretch", 
        help=translate("myCourses.dialogs.enroll.yes.help")
    ):
        enroll(cid)
        st.session_state.confirm_enroll_course_id = None
        st.rerun()
    
    if c2.button(
        translate("myCourses.dialogs.enroll.no.label"), 
        type="primary", 
        key=f"enroll_no_{cid}", 
        width="stretch", 
        help=translate("myCourses.dialogs.enroll.no.help")
    ):
        st.session_state.confirm_enroll_course_id = None
        st.rerun()

@st.dialog(translate("myCourses.dialogs.unenroll.title"))
def confirm_unenroll_dialog():
    cid = st.session_state.confirm_unenroll_course_id
    st.write(translate("myCourses.dialogs.unenroll.body", id=cid))
    c1, c2 = st.columns(2)
    
    if c1.button(
        translate("myCourses.dialogs.unenroll.yes.label"), 
        type="primary", 
        key=f"unenroll_yes_{cid}", 
        width="stretch", 
        help=translate("myCourses.dialogs.unenroll.yes.help")
    ):
        unenroll(cid)
        st.session_state.confirm_unenroll_course_id = None
        st.rerun()
    
    if c2.button(
        translate("myCourses.dialogs.unenroll.no.label"), 
        type="primary", 
        key=f"unenroll_no_{cid}", 
        width="stretch", 
        help=translate("myCourses.dialogs.unenroll.no.help")
    ):
        st.session_state.confirm_unenroll_course_id = None
        st.rerun()

@st.dialog(translate("myCourses.dialogs.dismiss.title"))
def confirm_dismiss_dialog():
    cid = st.session_state.confirm_dismiss_reco_course_id
    st.write(translate("myCourses.dialogs.dismiss.body", id=cid))
    c1, c2 = st.columns(2)
    
    if c1.button(
        translate("myCourses.dialogs.dismiss.yes.label"), 
        type="primary", 
        key=f"dismiss_yes_{cid}", 
        width="stretch", 
        help=translate("myCourses.dialogs.dismiss.yes.help")
    ):
        dismiss_recommendation(cid)
        st.session_state.confirm_dismiss_reco_course_id = None
        st.rerun()
    
    if c2.button(
        translate("myCourses.dialogs.dismiss.no.label"), 
        type="primary", 
        key=f"dismiss_no_{cid}", 
        width="stretch", 
        help=translate("myCourses.dialogs.dismiss.no.help")
    ):
        st.session_state.confirm_dismiss_reco_course_id = None
        st.rerun()

def render_course_summary(course: dict):
    summary = course.get("summary", "")
    if summary:
        plain_summary = strip_markdown_formatting(summary)
        st.caption(textwrap.shorten(plain_summary, width=220, placeholder="…"))

def render_progress_block(course: dict):
    percent = _safe_percent(course.get("completion_percent"))
    completed = bool(course.get("completed"))

    st.progress(percent, text=translate("myCourses.cards.progress", percent=percent))

    if completed:
        st.caption(translate("myCourses.cards.course_completed"))
    elif course.get("status") == "eligible_for_final_quiz":
        st.caption(translate("myCourses.cards.eligible_final_quiz"))
    else:
        st.caption(translate("myCourses.cards.course_inprogress"))

def render_enrolled_card(course: dict):
    course_id = course["course_id"]
    completed = bool(course.get("completed"))

    with st.container(border=True):
        info_col, action_col = st.columns([6, 3])

        with info_col:
            st.markdown(f"**{course.get('title', 'Untitled')}**  ·  `#{course_id}`")
            render_course_summary(course)
            render_progress_block(course)

        with action_col:
            if st.button(
                translate("myCourses.actions.view.label"),
                type="primary",
                key=f"view_enrolled_{course_id}",
                width="stretch",
                help=translate("myCourses.actions.view.help"),
            ):
                go_to_details(course_id)

            if completed:
                st.button(
                    translate("myCourses.actions.completed.label"),
                    type="primary",
                    key=f"completed_{course_id}",
                    width="stretch",
                    disabled=True,
                    help=translate("myCourses.actions.completed.help"),
                )
            else:
                if st.button(
                    translate("myCourses.actions.unenroll.label"),
                    type="primary",
                    key=f"unenroll_{course_id}",
                    width="stretch",
                    help=translate("myCourses.actions.unenroll.help"),
                ):
                    st.session_state.confirm_unenroll_course_id = course_id

    if st.session_state.confirm_unenroll_course_id == course_id:
        confirm_unenroll_dialog()

def render_available_card(course: dict, is_recommendation: bool):
    course_id = course["course_id"]

    with st.container(border=True):
        info_col, action_col = st.columns([6, 3])

        with info_col:
            st.markdown(f"**{course.get('title', 'Untitled')}**  ·  `#{course_id}`")
            render_course_summary(course)

            if is_recommendation and course.get("reason"):
                st.caption(translate("myCourses.cards.why", reason=course["reason"]))

        with action_col:
            if st.button(
                translate("myCourses.actions.view.label"),
                type="primary",
                key=f"view_available_{course_id}",
                width="stretch",
                help=translate("myCourses.actions.view.help"),
            ):
                go_to_details(course_id)

            if st.button(
                translate("myCourses.actions.enroll.label"),
                type="primary",
                key=f"enroll_{course_id}",
                width="stretch",
                help=translate("myCourses.actions.enroll.help"),
            ):
                st.session_state.confirm_enroll_course_id = course_id

            if is_recommendation:
                if st.button(
                    translate("myCourses.actions.dismiss.label"),
                    type="primary",
                    key=f"dismiss_{course_id}",
                    width="stretch",
                    help=translate("myCourses.actions.dismiss.help"),
                ):
                    st.session_state.confirm_dismiss_reco_course_id = course_id

    if st.session_state.confirm_enroll_course_id == course_id:
        confirm_enroll_dialog()

    if is_recommendation and st.session_state.confirm_dismiss_reco_course_id == course_id:
        confirm_dismiss_dialog()

################################
# Course Information
################################
st.title(translate("myCourses.pageTitle"))
st.markdown(translate("myCourses.subtitle"))
st.divider()

toolbar_l, toolbar_r = st.columns([1, 6])
with toolbar_l:
    if st.button(
        translate("myCourses.toolbar.refresh.label"), 
        type="primary", 
        key="refresh", 
        width="stretch", 
        help=translate("myCourses.toolbar.refresh.help")
    ):
        _clear_course_list_caches()
        st.rerun()

st.divider()

# ----- Load data
enrolled = recommended = all_courses = []

try:
    enrolled = fetch_enrolled(BACKEND_API_URL, headers) or []
except Exception as e:
    st.error(translate("myCourses.errors.enrolledLoad", detail=str(e)))

try:
    recommended = fetch_recommended(BACKEND_API_URL, headers) or []
except Exception as e:
    st.error(translate("myCourses.errors.recommendedLoad", detail=str(e)))

if not recommended:
    try:
        all_courses = fetch_all_courses(BACKEND_API_URL, headers) or []
    except Exception as e:
        st.error(translate("myCourses.errors.allLoad", detail=str(e)))

# ----- Section: Enrolled
st.subheader(translate("myCourses.sections.enrolled.title"))
if not enrolled:
    st.info(translate("myCourses.sections.enrolled.empty"))
else:
    for course in enrolled:
        render_enrolled_card(course)

st.divider()

# ----- Section: Recommended
st.subheader(translate("myCourses.sections.recommended.title"))
courses_to_show = recommended if recommended else all_courses

if not courses_to_show:
    st.info(translate("myCourses.sections.recommended.empty"))
else:
    if not recommended and all_courses:
        st.markdown(translate("myCourses.sections.recommended.fallback"))
    
    for course in courses_to_show:
        render_available_card(course, is_recommendation=bool(recommended))
