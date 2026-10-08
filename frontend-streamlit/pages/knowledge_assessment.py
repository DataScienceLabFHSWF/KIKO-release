import os, streamlit as st, requests, logging
from dotenv import load_dotenv
from pages import render_sidebar
from utils import require_login
from i18n import translate
from topbar import language_topbar
from http_headers import auth_headers

logger = logging.getLogger(__name__)

# set page configuration
st.set_page_config(page_title="Knowledge Assessment", page_icon="🧠", layout="wide")

# Check if the user is logged in
require_login()

# Render the sidebar
render_sidebar()

# Load API URL from environment variables
load_dotenv()
BACKEND_API_URL = os.getenv("BACKEND_API_URL")

# check if BACKEND_API_URL is set
if not BACKEND_API_URL:
    st.error(translate("knowledgeAssessment.errors.envMissing"))
    st.stop()

# Always show top-right language switch
language_topbar()

# declare headers for API requests
headers = {"Authorization": f"Bearer {st.session_state.token}"}

token = st.session_state.token

def fetch_quiz():
    try:
        response = requests.get(
            f"{BACKEND_API_URL}/api/knowledge_assessment/assessment_quiz",
            headers=headers
        )

        if response.ok:
            return response.json()
        else:
            if "application/json" in response.headers.get("Content-Type",""):
                st.warning(response.json().get("detail", translate("knowledgeAssessment.errors.quizFetch")))
            else:
                st.warning(translate("knowledgeAssessment.errors.quizFetch"))
            return []
    except Exception as e:
        st.warning(translate("knowledgeAssessment.errors.quizFetchWithDetail", detail=e))
        return []

def submit_quiz(answers):
    try:
        response = requests.post(
            f"{BACKEND_API_URL}/api/knowledge_assessment/assessment_submit",
            json={"answers": answers},
            headers=auth_headers(token)
        )
        
        if response.ok:
            return True, response.json()
        else:
            try:
                return False, response.json()
            except Exception:
                return False, {"detail": translate("knowledgeAssessment.errors.submitFailed"), "code": "quiz_submit_failed"}
    except Exception as e:
        return False, {
            "detail": translate("knowledgeAssessment.errors.submitFailedWithDetail", detail=e), 
            "code": "quiz_submit_failed"
            }

################################
# Knowledge Assessment
################################
st.title(translate("knowledgeAssessment.pageTitle"))
st.markdown(translate("knowledgeAssessment.subtitle"))
st.divider()

questions = fetch_quiz()

if not questions:
    st.info(translate("knowledgeAssessment.empty.noQuestions"))
    st.stop()
else:
    answers_payload = []
    
    with st.form("quiz_form", clear_on_submit=False):
        for q in questions:
            st.markdown(translate("knowledgeAssessment.form.questionLine", topic=q.get('topic',''), question=q.get('question','')))
            ans = st.text_input(
                translate("knowledgeAssessment.form.answerLabel"), 
                key=f"ans_{q['question_id']}", 
                help=translate("knowledgeAssessment.form.answerHelp")
            )

            answers_payload.append({
                "question_id": q["question_id"],
                "user_answer": (ans or "").strip()
            })
            
            st.divider()
        
        submitted = st.form_submit_button(
            translate("knowledgeAssessment.form.submitLabel"), 
            type="primary", 
            help=translate("knowledgeAssessment.form.submitHelp"), 
            width="stretch"
        )
    
    # Handle actions after form, no callbacks (avoids fragment rerun warnings)
    if submitted:
        # Validate all answers are filled
        empty = [a for a in answers_payload if not a["user_answer"]]
        
        if empty:
            st.warning(translate("knowledgeAssessment.form.validateAllRequired"))
            st.stop()

        with st.spinner(translate("knowledgeAssessment.status.evaluating")):

            ok, data = submit_quiz(answers_payload)
            
            print(f"✅ Quiz submission response: {data}")
            
            if ok:
                recs = data.get("recommended_courses", [])
                
                if not recs:
                    st.info(translate("knowledgeAssessment.empty.noRecommendations"))
                else:
                    # Keep them in session for the destination page
                    st.session_state["knowledge_check_recommendations"] = recs
                    st.switch_page("pages/my_courses.py")
            else:
                st.error(data.get("detail", translate("knowledgeAssessment.errors.submitFailed")))
