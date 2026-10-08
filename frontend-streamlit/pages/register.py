# frontend/pages/register.py
import os, requests, logging, datetime, streamlit as st, re
from dotenv import load_dotenv
from i18n import translate
from topbar import language_topbar

logger = logging.getLogger(__name__)

# Set page configuration
st.set_page_config(page_title="Register", page_icon="📝", layout="wide")

# Load API URL from environment variables
load_dotenv()
BACKEND_API_URL = os.getenv("BACKEND_API_URL")

if not BACKEND_API_URL:
    st.error(translate("error.env"))
    st.stop()

# Always show top-right language switch
language_topbar()

##################################
# Registration page
##################################
# Check if user is already logged in
st.image("./assets/images/KIKO-Logo.png", width=250)
st.divider()
role_values = ["Instructor", "Learner"]
EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")

def _is_valid_email(s: str) -> bool:
    return bool(EMAIL_RE.match((s or "").strip()))

def _as_list(value):
    return value if isinstance(value, list) else []

def _item_label(item) -> str:
    if isinstance(item, dict):
        return (
            item.get("title")
            or item.get("file_name")
            or item.get("filename")
            or item.get("name")
            or str(item)
        )
    return str(item)

def render_default_course_report(report: dict | None):
    if not isinstance(report, dict) or not report:
        return

    created_courses = _as_list(
        report.get("created_courses")
        or report.get("courses_created")
        or report.get("courses")
    )

    created_documents = _as_list(
        report.get("created_documents")
        or report.get("documents_created")
        or report.get("documents")
    )

    skipped = _as_list(report.get("skipped") or report.get("skipped_files"))
    errors = _as_list(report.get("errors") or report.get("failed"))

    if created_courses or created_documents:
        st.success("Default instructor content was prepared successfully.")

    if created_courses:
        with st.expander("Default courses created", expanded=True):
            for item in created_courses:
                st.markdown(f"- {_item_label(item)}")

    if created_documents:
        with st.expander("Default documents added", expanded=True):
            for item in created_documents:
                st.markdown(f"- {_item_label(item)}")

    if skipped:
        with st.expander("Skipped default content"):
            for item in skipped:
                st.markdown(f"- {_item_label(item)}")

    if errors:
        with st.expander("Default content warnings", expanded=True):
            for item in errors:
                st.warning(_item_label(item))

if "token" not in st.session_state:
    
    st.title(translate("register.pageTitle"))
    st.markdown(translate("register.subtitle"))
    
    with st.form("register_form", clear_on_submit=False):
        col1, col2 = st.columns(2)
        with col1:
            # username = st.text_input(
            #     translate("register.form.username.label"), 
            #     max_chars=64, 
            #     help=translate("register.form.username.help")
            # )
            full_name = st.text_input(
                translate("register.form.fullName.label"), 
                max_chars=128, 
                help=translate("register.form.fullName.help")
            )
            role = st.selectbox(
                translate("register.form.role.label"), 
                role_values, 
                index=0, 
                help=translate("register.form.role.help"),
                format_func=lambda v: translate(
                    f"register.form.role.options.{ 'instructor' if v=='Instructor' else 'learner' }"
                )
            )
        with col2:
            email = st.text_input(
                translate("register.form.email.label"), 
                max_chars=128, 
                help=translate("register.form.email.help")
            )
            # dob = st.date_input(
            #     translate("register.form.dob.label"), 
            #     value=None, 
            #     min_value=datetime.date(1945, 1, 1), 
            #     max_value=datetime.date.today(), 
            #     help=translate("register.form.dob.help")
            # )
            password = st.text_input(
                translate("register.form.password.label"), 
                type="password", 
                help=translate("register.form.password.help")
            )

        # bio = st.text_area(
        #     translate("register.form.bio.label"), 
        #     value=translate("register.form.bio.default"), 
        #     height=80, 
        #     max_chars=512, 
        #     help=translate("register.form.bio.help")
        # )
        
        submitted = st.form_submit_button(
            translate("register.form.submit.label"), 
            type="primary", 
            width="stretch", 
            help=translate("register.form.submit.help")
        )
    
    st.page_link("pages/login.py", label=translate("register.linkToLogin"))
    
    if submitted:
        # simple validations
        if not full_name or not email or not password:
            st.warning(translate("register.validations.required"))
            st.stop()
        
        if not _is_valid_email(email):
            st.warning(translate("register.validations.emailInvalid"))
            st.stop()
        
        if len(password) < 8:
            st.warning(translate("register.validations.passwordLen"))
            st.stop()
        
        payload = {
            # "username": username.strip(),
            "email": email.strip(),
            # "date_of_birth": str(dob) if dob else None,
            "password": password,
            "role": role,
            "full_name": full_name.strip(),
            # "bio": bio,
        }
        
        with st.spinner(translate("register.status.creating")):
            try:
                resp = requests.post(
                    f"{BACKEND_API_URL}/api/authentication/register", 
                    json=payload
                )
                try:
                    data = resp.json()
                except Exception:
                    data = {}
                
                if resp.status_code == 201:
                    st.success(translate("register.status.success"))
                    default_course_report = data.get("default_course_report")
                    
                    render_default_course_report(default_course_report)
                else:
                    detail = data.get("detail") if isinstance(data, dict) else None
                    st.error(detail or translate("register.status.failed"))
            except requests.Timeout:
                st.error("❌ Registration request timed out. The account may have been created, but default course setup took too long.")
            except requests.RequestException as e:
                st.error(f"❌ Network error: {e}")
else:
    st.info(translate("register.alreadyLoggedIn.info"))
    
    if st.button(
        translate("register.alreadyLoggedIn.goToLogin"),
        type="primary",
        help=translate("register.alreadyLoggedIn.help"),
    ):
        st.switch_page("pages/login.py")
    
    st.stop()
