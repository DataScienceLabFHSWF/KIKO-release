import os, streamlit as st, requests
from dotenv import load_dotenv
from utils import require_login
from pages import render_sidebar

st.set_page_config(page_title="Knowledge Check Config", page_icon="🧠", layout="wide")

# ---- Auth
require_login()
if st.session_state.get("role") != "Admin":
    st.error("❌ Only Admins can access this page.")
    st.stop()

render_sidebar()

# ---- Env / headers
load_dotenv()
BACKEND_API_URL = os.getenv("BACKEND_API_URL")
if not BACKEND_API_URL:
    st.error("❌ BACKEND_API_URL not set.")
    st.stop()

HEADERS = {"Authorization": f"Bearer {st.session_state.token}"}

# ---- State
st.session_state.setdefault("kc_selected_ids", set())
st.session_state.setdefault("kc_confirm_delete_qid", None)

# ---- Helper
def fetch_questions(api, headers):
    r = requests.get(f"{api}/api/knowledge_assessment/questions", headers=headers)
    r.raise_for_status()
    return r.json()  # [{question_id, topic, question, type, created_at, created_by}, ...]

def fetch_config(api, headers):
    r = requests.get(f"{api}/api/knowledge_assessment/config", headers=headers)
    r.raise_for_status()
    data = r.json() or {}
    # default shape if empty
    data.setdefault("enabled", True)
    data.setdefault("size", 5)
    data.setdefault("question_ids", [])
    return data

def save_config(api, headers, payload: dict):
    r = requests.put(f"{api}/api/knowledge_assessment/config", json=payload, headers=headers)
    if not r.ok:
        try:
            st.error(r.json().get("detail", f"Save failed ({r.status_code})"))
        except Exception:
            st.error(f"❌ Save failed ({r.status_code})")
        return False
    return True

def delete_question(api, headers, qid: int) -> bool:
    r = requests.delete(f"{api}/api/knowledge_assessment/questions/{qid}", headers=headers)
    return r.status_code in (200, 204)

# ----- Dialogs
@st.dialog("Delete question?")
def confirm_delete_dialog():
    qid = st.session_state.kc_confirm_delete_qid
    st.write(f"ℹ️ This will permanently delete question **{qid}**.")
    c1, c2 = st.columns(2)
    if c1.button("✅ Yes, delete", type="primary", key=f"del_yes_{qid}", width="stretch", help="Delete question."):
        ok = delete_question(BACKEND_API_URL, HEADERS, qid)
        if ok:
            st.toast("🗑️ Deleted", icon="🧹")
            # Clear caches + selection
            fetch_questions.clear()
            # remove from selected set if present
            st.session_state.kc_selected_ids.discard(qid)
        else:
            st.error("Delete failed.")
        st.session_state.kc_confirm_delete_qid = None
        st.rerun()
    if c2.button("❌ Cancel", type="primary", key=f"del_no_{qid}", width="stretch", help="Close the window."):
        st.session_state.kc_confirm_delete_qid = None
        st.rerun()

# ---- Header + toolbar
st.title("🧠 Knowledge Check — Configuration")
st.markdown("Choose which questions can appear and how many to serve per assessment.")
st.divider()

t1, t2, t3 = st.columns([1,1,6])
if t1.button("🔄 Refresh", type="primary", width="stretch", help="Fetch questions."):
    fetch_questions.clear(); fetch_config.clear()
    st.session_state.kc_selected_ids = set()
    st.rerun()
if t2.button("💾 Save", type="primary", width="stretch", help="Save configuration."):
    # Build payload from UI state
    enabled = st.session_state.get("kc_enabled", True)
    size = st.session_state.get("kc_size", 5)
    selected_ids = sorted(list(st.session_state.kc_selected_ids))
    if not selected_ids:
        st.error("❌ Select at least one question before saving.")
    elif size < 1:
        st.error("❌ Quiz size must be at least 1.")
    elif size > len(selected_ids):
        st.error(f"❌ Quiz size ({size}) cannot exceed selected questions ({len(selected_ids)}).")
    else:
        ok = save_config(BACKEND_API_URL, HEADERS, {"enabled": enabled, "size": size, "question_ids": selected_ids})
        if ok:
            st.toast("✅ Configuration saved", icon="💾")
            fetch_config.clear()
            st.rerun()

st.divider()

# ---- Load data
try:
    all_questions = fetch_questions(BACKEND_API_URL, HEADERS) or []
    cfg = fetch_config(BACKEND_API_URL, HEADERS)
except requests.HTTPError as e:
    st.error(f"❌ Failed to load data: {e}")
    st.stop()
except Exception as e:
    st.error(f"❌ Unexpected error: {e}")
    st.stop()

# Initialize selection from config on first load
if not st.session_state.kc_selected_ids and cfg.get("question_ids"):
    st.session_state.kc_selected_ids = set(cfg["question_ids"])

# ---- Controls (left) + Filters (right)
left, right = st.columns([1,2], gap="large")

with left:
    st.subheader("Settings")
    st.session_state.kc_enabled = st.toggle("Enable Knowledge Check", value=cfg.get("enabled", True))
    st.session_state.kc_size = st.number_input(
        "Questions per assessment",
        min_value=1, max_value=100,
        value=int(cfg.get("size", 5))
    )
    st.caption(f"Selected: **{len(st.session_state.kc_selected_ids)}** questions")

with right:
    st.subheader("Filters")
    # Build filter options
    topics = sorted({q.get("topic") for q in all_questions if q.get("topic")})
    types = sorted({q.get("type") for q in all_questions if q.get("type")})
    f1, f2, f3 = st.columns([2,2,2])
    with f1:
        topic_filter = st.multiselect("Topic", topics)
    with f2:
        type_filter = st.multiselect("Type", types)
    with f3:
        search = st.text_input("Search text", placeholder="Search in question text...")

    # Bulk buttons
    b1, b2, _ = st.columns([1,1,4])
    if b1.button("Select all (filtered)", type="primary", help="Select all."):
        for q in all_questions:
            if topic_filter and q.get("topic") not in topic_filter: continue
            if type_filter and q.get("type") not in type_filter: continue
            if search and (search.lower() not in (q.get("question","").lower())): continue
            st.session_state.kc_selected_ids.add(q["question_id"])
    if b2.button("Clear all (filtered)", type="primary", help="Delete all."):
        ids_to_clear = set()
        for q in all_questions:
            if topic_filter and q.get("topic") not in topic_filter: continue
            if type_filter and q.get("type") not in type_filter: continue
            if search and (search.lower() not in (q.get("question","").lower())): continue
            ids_to_clear.add(q["question_id"])
        st.session_state.kc_selected_ids -= ids_to_clear

st.divider()

# ---- Question list with checkboxes
st.subheader("Question Pool")
if not all_questions:
    st.info("ℹ️ No questions found.")
else:
    for q in all_questions:
        # apply filters
        if topic_filter and q.get("topic") not in topic_filter: continue
        if type_filter and q.get("type") not in type_filter: continue
        if search and (search.lower() not in (q.get("question","").lower())): continue

        qid = q["question_id"]
        with st.container(border=True):
            row1, row2 = st.columns([6,2])
            with row1:
                st.markdown(f"**[{qid}] {q.get('topic','—')}** · *{q.get('type','—')}*")
                st.write(q.get("question",""))
            
            with row2:
                checked = qid in st.session_state.kc_selected_ids
                
                if st.checkbox("Include", value=checked, key=f"include_{qid}"):
                    st.session_state.kc_selected_ids.add(qid)
                else:
                    st.session_state.kc_selected_ids.discard(qid)
                
                # Delete button (admin)
                if st.button("🗑️ Delete", type="primary", key=f"btn_del_{qid}", help="Delete question."):
                    st.session_state.kc_confirm_delete_qid = qid
        
        # outside the container, auto-open dialog if flagged
        if st.session_state.kc_confirm_delete_qid == qid:
            confirm_delete_dialog()

# ---- Footer validation
st.divider()
sel = len(st.session_state.kc_selected_ids)
size = int(st.session_state.get("kc_size", 5))
if sel == 0:
    st.warning("⚠️ Select at least one question to enable the assessment.")
elif size > sel:
    st.warning(f"⚠️ Quiz size ({size}) exceeds selected questions ({sel}). Reduce the size or select more questions.")
