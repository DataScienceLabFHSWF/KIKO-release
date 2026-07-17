# Import necessary libraries
import streamlit as st, logging
from pages import render_sidebar
from utils import require_login
from i18n import translate
from topbar import language_topbar

logger = logging.getLogger(__name__)

# set page configuration
st.set_page_config(page_title="FAQ", page_icon="❓", layout="wide")

# Check if the user is logged in
require_login()

# Always show top-right language switch
language_topbar()

# Render the sidebar
render_sidebar()

role = (st.session_state.get("role") or "").strip()
full_name = st.session_state.get("full_name", "")

def is_learner() -> bool:
    """Check if the current user is a learner."""
    return role.lower() == "learner"

def is_instructor() -> bool:
    """Check if the current user is an instructor."""
    return role.lower() == "instructor"

def show_quick_links_for_learner():
    """Display quick navigation links for learners."""
    c1, c2, c3 = st.columns(3)
    with c1:
        st.page_link("pages/learner_dashboard.py", label=translate("faq.quickLinks.learner.dashboard"))
        st.page_link("pages/chatbot.py", label=translate("faq.quickLinks.learner.chat"))
        st.page_link("pages/my_courses.py", label=translate("faq.quickLinks.learner.myCourses"))
    with c2:
        st.page_link("pages/knowledge_assessment.py", label=translate("faq.quickLinks.learner.assessment"))
        st.page_link("pages/my_documents.py", label=translate("faq.quickLinks.learner.documents"))
        st.page_link("pages/profile.py", label=translate("faq.quickLinks.learner.profile"))
    with c3:
        st.page_link("pages/evaluation_results.py", label=translate("faq.quickLinks.learner.results"))

def show_quick_links_for_instructor():
    """Display quick navigation links for instructors."""
    c1, c2, c3 = st.columns(3)
    with c1:
        st.page_link("pages/chatbot.py", label=translate("faq.quickLinks.instructor.chat"))
        st.page_link("pages/instructor_course_creation.py", label=translate("faq.quickLinks.instructor.courseSetup"))
        st.page_link("pages/instructor_courses.py", label=translate("faq.quickLinks.instructor.myCourses"))
    with c2:
        st.page_link("pages/my_documents.py", label=translate("faq.quickLinks.instructor.documents"))
        st.page_link("pages/profile.py", label=translate("faq.quickLinks.instructor.profile"))
        st.page_link("pages/evaluation_results.py", label=translate("faq.quickLinks.instructor.results"))
    with c3:
        # Keep column for symmetry / future links
        st.write("")

# ---------------------------
st.title(translate("faq.pageTitle"))
st.markdown(translate("faq.welcome", fullName=full_name))
st.divider()

# ---------------------------
# Quick Links
# ---------------------------
st.markdown(translate("faq.quickLinks.title"))

if is_learner():
    show_quick_links_for_learner()
elif is_instructor():
    show_quick_links_for_instructor()
else:
    # Unknown role: show both sets
    with st.container(border=True):
        st.subheader(translate("faq.quickLinks.unknownRole.learnerHeader"))
        show_quick_links_for_learner()
    with st.container(border=True):
        st.subheader(translate("faq.quickLinks.unknownRole.instructorHeader"))
        show_quick_links_for_instructor()

st.divider()

# ---------------------------
# Role-specific FAQs
# ---------------------------
if is_learner() or not role:
    """Display FAQs tailored for learners."""
    st.header(translate("faq.sections.learner.header"))

    with st.expander(translate("faq.sections.learner.learningDashboard.title"), expanded=is_learner()):
        st.markdown(translate("faq.sections.learner.learningDashboard.body"))

    with st.expander(translate("faq.sections.learner.chatAssistant.title")):
        st.markdown(translate("faq.sections.learner.chatAssistant.body"))

    with st.expander(translate("faq.sections.learner.myCourses.title")):
        st.markdown(translate("faq.sections.learner.myCourses.body"))

    with st.expander(translate("faq.sections.learner.assessment.title")):
        st.markdown(translate("faq.sections.learner.assessment.body"))

    with st.expander(translate("faq.sections.learner.documents.title")):
        st.markdown(translate("faq.sections.learner.documents.body"))

    with st.expander(translate("faq.sections.learner.profileResults.title")):
        st.markdown(translate("faq.sections.learner.profileResults.body"))

if is_instructor() or not role:
    st.header(translate("faq.sections.instructor.header"))

    with st.expander(translate("faq.sections.instructor.chatAssistant.title"), expanded=is_instructor()):
        st.markdown(translate("faq.sections.instructor.chatAssistant.body"))

    with st.expander(translate("faq.sections.instructor.courseSetup.title")):
        st.markdown(translate("faq.sections.instructor.courseSetup.body"))

    with st.expander(translate("faq.sections.instructor.myCourses.title")):
        st.markdown(translate("faq.sections.instructor.myCourses.body"))    

    with st.expander(translate("faq.sections.instructor.documents.title")):
        st.markdown(translate("faq.sections.instructor.documents.body"))
    
    with st.expander(translate("faq.sections.instructor.profileResults.title")):
        st.markdown(translate("faq.sections.instructor.profileResults.body"))

st.divider()

st.header(translate("faq.common.header"))

with st.expander(translate("faq.common.dialogs.title")):
    st.markdown(translate("faq.common.dialogs.body"))

with st.expander(translate("faq.common.recommendations.title")):
    st.markdown(translate("faq.common.recommendations.body"))

with st.expander(translate("faq.common.uploads.title")):
    st.markdown(translate("faq.common.uploads.body"))

st.info(translate("faq.common.contact", email="kiko.support@fh-swf.de"), icon="ℹ️")
