# frontend/pages/login.py
import os, streamlit as st, requests, logging, re
from dotenv import load_dotenv
from time import sleep
from utils import get_user_profile
from i18n import translate
from topbar import language_topbar
from http_headers import auth_headers

logger = logging.getLogger(__name__)

# Set page configuration
st.set_page_config(page_title="Login", page_icon="🔐", layout="wide")

# Load API URL from environment variables
load_dotenv()
BACKEND_API_URL = os.getenv("BACKEND_API_URL")
DEFAULT_EMB_MODEL = os.getenv("EMBEDDING_MODEL_NAME")
DEFAULT_LLM_MODEL = os.getenv("LLAMA_LLM_GENERATION_MODEL_NAME")
EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")

# check if BACKEND_API_URL is set
if not BACKEND_API_URL or not DEFAULT_EMB_MODEL or not DEFAULT_LLM_MODEL:
    st.error(translate("error.env"))
    st.stop()

# Always show top-right language switch
language_topbar()

# Function to handle login
def _login(email, password):
    """Attempt to login and return token if successful."""
    
    payload = {
        "email": email, 
        "password": password
    }

    response = requests.post(
        f"{BACKEND_API_URL}/api/authentication/authenticate",
        json= payload
    )
    
    if response.status_code == 200:
        return response.json()["access_token"]
    
    return None

def _is_valid_email(s: str) -> bool:
    return bool(EMAIL_RE.match((s or "").strip()))

##################################
# Login page
##################################
st.image("./assets/images/KIKO-Logo.png", width=250)
st.divider()

# Check if user is already logged in
if "token" not in st.session_state:
    
    st.title(translate("login.pageTitle"))
    st.markdown(translate("login.subtitle"))
    
    with st.form("login_form", clear_on_submit=False):
        email = st.text_input(
            translate("login.form.email.label"), 
            max_chars=128, 
            help=translate("login.form.email.help")
        )
        password = st.text_input(
            translate("login.form.password.label"), 
            type="password", 
            help=translate("login.form.password.help")
        )
        
        submitted = st.form_submit_button(
            translate("login.form.submit.label"), 
            type="primary", 
            width="stretch", 
            help=translate("login.form.submit.help")
        )
    
    st.page_link("pages/register.py", label=translate("login.linkToRegister"))
    
    if submitted:
        # simple validations
        if not email or not password:
            st.warning(translate("login.validations.required"))
            st.stop()
        
        if not _is_valid_email(email):
            st.warning(translate("login.validations.emailInvalid"))
            st.stop()
        
        if len(password) < 8:
            st.warning(translate("login.validations.passwordLen"))
            st.stop()

        with st.spinner(translate("login.status.loading")):
            # Attempt to login
            
            token = _login(email=email, password=password)
            
            # If login is successful, fetch user profile
            if token:
                profile = get_user_profile(token)
                
                if profile:
                    st.session_state.token = token
                    # st.session_state.username = profile["username"]
                    st.session_state.email = profile["email"]
                    st.session_state.role = profile["role"]
                    st.session_state.full_name = profile.get("full_name", "")
                    
                    profile["token"] = token
                    st.success(translate("login.status.success"))
                    sleep(0.8)
                    # ✅ Navigate after login
                    st.switch_page("main.py")
                else:
                    st.error(translate("login.status.profileFailed"))
                    st.stop()
            else:
                st.error(translate("login.status.invalid"))
                st.stop()
else:
    # Already logged in
    st.success(f"✅ Logged in as {st.session_state.full_name} ({st.session_state.role})")
    st.button(
        translate("login.dashboard.goto"), 
        type="primary", 
        on_click=lambda: st.switch_page("main.py"), 
        help=translate("login.dashboard.help")
    )
