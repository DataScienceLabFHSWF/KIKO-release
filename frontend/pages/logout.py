import streamlit as st, logging
from time import sleep
from i18n import translate

logger = logging.getLogger(__name__)

# Function to handle logout
def logout():
    for key in ["email", "role", "token", "full_name", "loaded_history", "messages"]:
        # Clear session state variables
        st.session_state.pop(key, None)
    
    st.success(translate("logout.success"))
    sleep(0.10)
    # Redirect to login page
    st.switch_page("pages/login.py")
    st.stop()
