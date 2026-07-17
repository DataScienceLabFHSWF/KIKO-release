# frontend/pages/sidebar.py
import streamlit as st, logging
from .logout import logout
from i18n import translate

logger = logging.getLogger(__name__)

# function to render the sidebar
def render_sidebar():
    if "token" not in st.session_state:
        return
    
    with st.sidebar:

        st.image("./assets/images/KIKO-Logo.png", width=250)
        st.divider()

        role = st.session_state["role"]
        full_name = st.session_state["full_name"]  

        st.markdown(translate("sidebar.welcome", fullName=full_name, role=role))
        st.divider()   

        if role == "Learner":
            logger.info("Rendering learner sidebar for %s", full_name)
            st.page_link("pages/learner_dashboard.py", label=translate("sidebar.menus.learner.dashboard"), icon="📊")
            st.page_link("pages/my_courses.py", label=translate("sidebar.menus.learner.myCourses"), icon="📚")
            st.page_link("pages/chatbot.py", label=translate("sidebar.menus.learner.chat"), icon="🤖")
            st.page_link("pages/knowledge_assessment.py", label=translate("sidebar.menus.learner.assessment"), icon="🧠")
        elif role == "Instructor":
            logger.info("Rendering instructor sidebar for %s", full_name)
            # st.page_link("pages/instructor_dashboard.py", label="Instructor Dashboard", icon="🧑‍🏫")
            st.page_link("pages/instructor_courses.py", label=translate("sidebar.menus.instructor.myCourses"), icon="📚")
            st.page_link("pages/media_manager.py", label=translate("sidebar.menus.instructor.mediaManager"), icon="🖼️")
            st.page_link("pages/instructor_course_creation.py", label=translate("sidebar.menus.instructor.courseSetup"), icon="✍️")
            st.page_link("pages/chatbot.py", label=translate("sidebar.menus.instructor.chat"), icon="🤖")
        elif role == "Admin":
            logger.info("Rendering admin sidebar for %s", full_name)
            st.page_link("pages/admin_dashboard.py", label=translate("sidebar.menus.admin.dashboard"), icon="🛠️")
            st.page_link("pages/admin_knowledge_config.py", label=translate("sidebar.menus.admin.knowledgeConfig"), icon="🧠")
            st.page_link("pages/admin_panel.py", label=translate("sidebar.menus.admin.console"), icon="🧩")
        
        st.page_link("pages/my_documents.py", label=translate("sidebar.menus.common.documents"), icon="📄")
        st.page_link("pages/profile.py", label=translate("sidebar.menus.common.profile"), icon="👤")
        st.page_link("pages/faq.py", label=translate("sidebar.menus.common.faq"), icon="❓")
        st.page_link("pages/evaluation_results.py", label=translate("sidebar.menus.common.results"), icon="🔍")
        # st.page_link("pages/settings.py", label="Account Settings", icon="⚙️")
        st.divider()
        st.button(translate("sidebar.menus.common.logout.label"), on_click=logout, type="primary", help=translate("sidebar.menus.common.logout.help"))
