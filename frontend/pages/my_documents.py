# frontend/pages/my_documents.py
import os, streamlit as st, requests, logging, mimetypes
from dotenv import load_dotenv
from pages import render_sidebar
from utils import format_date, require_login, extension_of, fetch_bytes, file_emoji
from io import BytesIO
from i18n import translate
from topbar import language_topbar

logger = logging.getLogger(__name__)

# set page configuration
st.set_page_config(page_title="My Documents", page_icon="📄", layout="wide")

# Check if the user is logged in
require_login()

# Always show top-right language switch
language_topbar()

# Render the sidebar
render_sidebar()

# Load API URL from environment variables
load_dotenv()
BACKEND_API_URL = os.getenv("BACKEND_API_URL")

# check if BACKEND_API_URL is set
if not BACKEND_API_URL:
    st.error(translate("docs.errors.envMissing"))
    st.stop()

# declare headers for API requests
headers={"Authorization": f"Bearer {st.session_state.token}"}

# --- Session flags for confirmation modals
if "confirm_delete_id" not in st.session_state:
    st.session_state.confirm_delete_id = None
if "confirm_delete_all" not in st.session_state:
    st.session_state.confirm_delete_all = False
if "preview_hash" not in st.session_state:
    st.session_state.preview_hash = None
if "preview_doc" not in st.session_state:
    st.session_state.preview_doc = None

@st.cache_data(ttl=30, show_spinner=False)
def fetch_my_docs():
    url = f"{BACKEND_API_URL}/api/document/my_docs"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()
    return data

def delete_one(document_id: int):
    url = f"{BACKEND_API_URL}/api/document/delete_doc/{document_id}"
    response = requests.delete(url, headers=headers)
    
    if response.status_code not in (200, 204):
        try:
            st.toast(translate("docs.toasts.deleteOneFailed", detail=response.json().get('detail')), icon="❌")
        except Exception:
            st.toast(translate("docs.toasts.deleteOneFailed", detail=response.status_code), icon="❌")
    else:
        st.toast(translate("docs.toasts.deleteOneSuccess"), icon="🗑️")
        fetch_my_docs.clear()  # invalidate cache

def delete_all():
    url = f"{BACKEND_API_URL}/api/document/delete_all_doc"
    response = requests.delete(url, headers=headers)
    
    if response.status_code not in (200, 204):
        try:
            st.toast(translate("docs.toasts.deleteAllFailed", detail=response.json().get('detail')), icon="❌")
        except Exception:
            st.toast(translate("docs.toasts.deleteAllFailed", detail=response.status_code), icon="❌")
    else:
        st.toast(translate("docs.toasts.deleteAllSuccess"), icon="🧹")
        fetch_my_docs.clear()

# stable unique key per doc + button role
def key_pair(doc, base):
    return f"{base}_{doc['document_id']}_{doc['content_hash'][:8]}"

# ---------- Dialogs ----------
@st.dialog(translate("docs.dialogs.single.title"))
def confirm_single_dialog():
    st.write(translate("docs.dialogs.single.body"))
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button(translate("docs.dialogs.single.confirm.label"), key="confirm_del_yes", type="primary", help=translate("docs.dialogs.single.confirm.help")):
            delete_one(st.session_state.confirm_delete_id)
            st.session_state.confirm_delete_id = None
            st.rerun()
    with col_b:
        if st.button(translate("docs.dialogs.single.cancel.label"), type="primary", key="confirm_del_no", help=translate("docs.dialogs.single.cancel.help")):
            st.session_state.confirm_delete_id = None
            st.rerun()

@st.dialog(translate("docs.dialogs.all.title"))
def confirm_all_dialog():
    st.write(translate("docs.dialogs.all.body"))
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button(translate("docs.dialogs.all.confirm.label"), key="confirm_all_yes", type="primary", help=translate("docs.dialogs.all.confirm.help")):
            delete_all()
            st.session_state.confirm_delete_all = False
            st.rerun()
    with col_b:
        if st.button(translate("docs.dialogs.all.cancel.label"), type="primary",  key="confirm_all_no", help=translate("docs.dialogs.all.cancel.help")):
            st.session_state.confirm_delete_all = False
            st.rerun()

@st.dialog(translate("docs.dialogs.preview.title"))
def preview_dialog():
    doc = st.session_state.preview_doc

    if not doc:
        st.info(translate("docs.dialogs.preview.noPreview"))
        return

    file_name = doc.get("file_name", "Document")
    st.subheader(file_name)

    ext = extension_of(file_name).lower()

    if ext in (".md", ".markdown"):
        url = f"{BACKEND_API_URL}/api/files/{doc['content_hash']}/markdown"

        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            payload = response.json()
        except requests.RequestException as exc:
            logger.warning("Failed to fetch markdown preview for %s: %s", file_name, exc)
            st.warning(translate("docs.warnings.markdownPreviewFail"))
        else:
            metadata = payload.get("metadata") or {}
            title = metadata.get("title")
            subtitle = metadata.get("category") or metadata.get("level")

            if title and title != file_name:
                st.markdown(f"### {title}")
            if subtitle:
                st.caption(translate("docs.dialogs.preview.categoryPrefix", subtitle=subtitle))

            objectives = metadata.get("learning_objectives")
            if isinstance(objectives, list) and objectives:
                st.markdown(translate("docs.dialogs.preview.learningObjectivesTitle"))
                for objective in objectives[:6]:
                    st.write(f"- {objective}")
            elif isinstance(objectives, str) and objectives.strip():
                st.markdown(translate("docs.dialogs.preview.learningObjectivesTitle"))
                st.write(objectives.strip())

            content = payload.get("content") or ""
            if content:
                st.markdown(content)
            else:
                st.info(translate("docs.dialogs.preview.noMarkdownPreview"))
    else:
        if not st.session_state.preview_hash:
            st.warning(translate("docs.warnings.previewImageMissing"))
        else:
            url = f"{BACKEND_API_URL}/api/files/{st.session_state.preview_hash}/preview.png"
            img_bytes = fetch_bytes(url, headers)

            if img_bytes:
                st.image(img_bytes, caption=translate("docs.dialogs.preview.fullPreviewCaption"), width="stretch")
            else:
                st.warning(translate("docs.warnings.previewImageMissing"))
    
    if st.button(translate("docs.dialogs.preview.close"), key="preview_close", type="primary", help=translate("docs.dialogs.preview.closeHelp")):
        st.session_state.preview_hash = None
        st.session_state.preview_doc = None
        st.rerun()

################################
# My Documents
################################
st.title(translate("docs.pageTitle"))
st.markdown(translate("docs.subtitle"))
st.divider()

# Toolbar
left, mid, right = st.columns([1, 4, 2])
with left:
    if st.button(translate("docs.toolbar.refresh.label"), width="stretch", type="primary", help=translate("docs.toolbar.refresh.help")):
        fetch_my_docs.clear()
with right:
    if st.button(translate("docs.toolbar.deleteAll.label"), width="stretch", type="primary", help=translate("docs.toolbar.deleteAll.help")):
        st.session_state.confirm_delete_all = True

docs = fetch_my_docs()

if not docs and len(docs) == 0:
    st.info(translate("docs.list.empty"))
    st.stop()

# Grid of document cards
for doc in docs:
    with st.container(border=True):
        c1, c2, c3, c4, c5 = st.columns([2, 4, 2, 2, 2])
        
        with c1:
            st.markdown(f"<div style='font-size:64px'>{file_emoji(doc['file_name'])}</div>", unsafe_allow_html=True)
        
        with c2:
            st.subheader(doc["file_name"])
            uploaded_at = doc.get("uploaded_at")
            dt = None
            if uploaded_at:
                try:
                    dt = format_date(uploaded_at)
                except Exception:
                    pass
            
            st.caption(translate("docs.list.uploadedPrefix", date=dt))
            st.caption(translate("docs.list.statusPrefix", status=doc.get('status', '—')))
        
        with c3:
            # Enable preview button for all file types. The preview dialog will gracefully
            # handle missing preview images (it will show a warning if no preview available).
            if st.button(
                translate("docs.list.preview.label"), 
                type="primary", 
                width="stretch", 
                key=key_pair(doc, "preview"), 
                help=translate("docs.list.preview.help")
            ):
                st.session_state.preview_hash = doc["content_hash"]
                st.session_state.preview_doc = doc
                preview_dialog()  # open the dialog
        
        with c4:
            dl_url = f"{BACKEND_API_URL}/api/files/{doc['content_hash']}/download"
            
            # fetch bytes now and offer a proper download button
            pdf_bytes = fetch_bytes(dl_url, headers)
            
            if pdf_bytes:
                # guess MIME from filename
                mime, _ = mimetypes.guess_type(doc["file_name"])
                mime = mime or "application/octet-stream"
                
                st.download_button(
                    translate("docs.list.download.label"),
                    type="primary",
                    data=BytesIO(pdf_bytes),
                    file_name=doc["file_name"],
                    mime=mime,
                    width="stretch",
                    key=key_pair(doc, "download"),
                    help=translate("docs.list.download.help")
                )
            else:
                st.button(
                    translate("docs.list.downloadDisabled"), 
                    type="primary", 
                    width="stretch", 
                    disabled=True, 
                    key=key_pair(doc, "download_dis")
                )
        
        with c5:
            # Delete (opens confirmation modal)
            if st.button(
                translate("docs.list.delete.label"), 
                width="stretch", 
                type="primary", 
                key=key_pair(doc, "delete"), 
                help=translate("docs.list.delete.help")
            ):
                st.session_state.confirm_delete_id = doc["document_id"]

# --- Open dialogs when flags are set ---
if st.session_state.confirm_delete_id is not None:
    confirm_single_dialog()  # opens the dialog

if st.session_state.confirm_delete_all:
    confirm_all_dialog()     # opens the dialog
