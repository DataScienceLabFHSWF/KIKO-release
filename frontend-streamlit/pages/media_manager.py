import streamlit as st
import os
import requests
from pages.sidebar import render_sidebar
from utils import require_login
from i18n import translate
from topbar import language_topbar
from datetime import datetime

st.set_page_config(page_title="Media Manager", page_icon="🖼️", layout="wide")

require_login()
render_sidebar()

BACKEND_API_URL = os.getenv("BACKEND_API_URL")

# Check if BACKEND_API_URL is set
if not BACKEND_API_URL:
    st.error(translate("error.env"))
    st.stop()

# Always show top-right language switch
language_topbar()

# Custom CSS to make the copy button more visible
st.markdown("""
<style>
    /* Make the code block copy button more visible - try multiple selectors */
    div[data-testid="stCodeBlock"] button,
    .stCodeBlock button,
    button[kind="icon"],
    button[title="Copy to clipboard"] {
        opacity: 1 !important;
        background-color: #0066cc !important;
        color: white !important;
        border: 2px solid #0052a3 !important;
        font-weight: bold !important;
        padding: 4px 8px !important;
    }
    div[data-testid="stCodeBlock"] button:hover,
    .stCodeBlock button:hover,
    button[kind="icon"]:hover,
    button[title="Copy to clipboard"]:hover {
        background-color: #0052a3 !important;
        transform: scale(1.1) !important;
    }
    
    /* Uniform image container styling */
    .image-gallery-container {
        aspect-ratio: 1 / 1;
        overflow: hidden;
        display: flex;
        align-items: center;
        justify-content: center;
        background-color: #f0f2f6;
        border-radius: 4px;
        margin-bottom: 8px;
    }
    
    .image-gallery-container img {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }
</style>
""", unsafe_allow_html=True)

headers = {"Authorization": f"Bearer {st.session_state.token}"}

# Session state for dialogs
if "confirm_delete_image_id" not in st.session_state:
    st.session_state.confirm_delete_image_id = None
if "confirm_delete_image_course" not in st.session_state:
    st.session_state.confirm_delete_image_course = None
if "selected_course_id" not in st.session_state:
    st.session_state.selected_course_id = None


@st.cache_data(ttl=5, show_spinner=False)
def fetch_courses(_headers):
    """Fetch instructor's courses."""
    try:
        url = f"{BACKEND_API_URL}/api/course/my_courses"
        response = requests.get(url, headers=_headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return data if isinstance(data, list) else []
        elif response.status_code == 404:
            st.warning(translate("mediaManager.warnings.endpointNotFound", url=url))
            return []
        else:
            st.warning(translate("mediaManager.warnings.badStatus", status=response.status_code, text=response.text[:200]))
            return []
    except requests.exceptions.RequestException as e:
        st.error(translate("mediaManager.errors.fetchCoursesNetwork", error=str(e)))
        return []
    except Exception as e:
        st.error(translate("mediaManager.errors.fetchCoursesGeneric", error=str(e)))
        return []


def fetch_course_images(course_id: int):
    """Fetch images for a specific course."""
    try:
        response = requests.get(
            f"{BACKEND_API_URL}/api/course/{course_id}/images",
            headers=headers,
            timeout=10
        )
        if response.status_code == 200:
            return response.json()
        return []
    except Exception as e:
        st.error(translate("mediaManager.errors.fetchImages", error=str(e)))
        return []


def upload_image(course_id: int, uploaded_file):
    """Upload an image to a course."""
    try:
        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
        response = requests.post(
            f"{BACKEND_API_URL}/api/course/{course_id}/images",
            headers=headers,
            files=files,
            timeout=30
        )
        
        if response.status_code == 200:
            st.success(translate("mediaManager.toast.uploadSuccess", filename=uploaded_file.name))
            st.cache_data.clear()  # Clear cache to show new image
            st.rerun()
        else:
            error_detail = response.json().get("detail", "Unknown error")
            st.error(translate("mediaManager.errors.uploadFailed", detail=error_detail))
    except Exception as e:
        st.error(translate("mediaManager.errors.uploadException", error=str(e)))


def delete_image(course_id: int, stored_filename: str):
    """Delete an image from a course."""
    try:
        response = requests.delete(
            f"{BACKEND_API_URL}/api/course/{course_id}/images/{stored_filename}",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            st.success(translate("mediaManager.toast.deleteSuccess"))
            st.cache_data.clear()
            st.rerun()
        else:
            error_detail = response.json().get("detail", "Unknown error")
            st.error(translate("mediaManager.errors.deleteFailed", detail=error_detail))
    except Exception as e:
        st.error(translate("mediaManager.errors.deleteException", error=str(e)))


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"


def format_date(date_str: str) -> str:
    """Format ISO date string to readable format."""
    try:
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return dt.strftime("%Y-%m-%d %H:%M")
    except:
        return date_str


# ---------- Dialogs ----------
@st.dialog(translate("mediaManager.dialog.delete.title"))
def confirm_delete_dialog():
    st.write(translate("mediaManager.dialog.delete.body"))
    st.warning(translate("mediaManager.dialog.delete.warning"))
    
    col1, col2 = st.columns(2)
    if col1.button(translate("mediaManager.dialog.delete.yes.label"), type="primary", width='stretch', help=translate("mediaManager.dialog.delete.yes.help")):
        # Store values before clearing session state
        course_id = st.session_state.confirm_delete_image_course
        image_id = st.session_state.confirm_delete_image_id
        
        # Clear session state immediately to close dialog
        st.session_state.confirm_delete_image_id = None
        st.session_state.confirm_delete_image_course = None
        
        # Now perform the delete
        delete_image(course_id, image_id)
    
    if col2.button(translate("mediaManager.dialog.delete.no.label"), type="primary", width='stretch', help=translate("mediaManager.dialog.delete.no.help")):
        st.session_state.confirm_delete_image_id = None
        st.session_state.confirm_delete_image_course = None
        st.rerun()


# ============================================================
# Main UI
# ============================================================

st.title(translate("mediaManager.title"))
st.markdown(translate("mediaManager.subtitle"))
st.divider()

# Help section
with st.expander(translate("mediaManager.help.expanderTitle")):
    st.markdown(
        "\n\n".join(
            [
                translate("mediaManager.help.workflowTitle"),
                translate("mediaManager.help.steps.one"),
                translate("mediaManager.help.steps.two"),
                translate("mediaManager.help.steps.three"),
                translate("mediaManager.help.steps.four"),
                translate("mediaManager.help.steps.five"),
                translate("mediaManager.help.steps.six"),
                translate("mediaManager.help.exampleTitle"),
                translate("mediaManager.help.exampleMarkdownBlock"),
                translate("mediaManager.help.tipsTitle"),
                translate("mediaManager.help.tips.edit"),
                translate("mediaManager.help.tips.linked"),
                translate("mediaManager.help.tips.formats"),
                translate("mediaManager.help.tips.maxSize"),
                translate("mediaManager.help.tips.copyPaste"),
            ]
        )
    )

st.divider()

# Fetch courses with a single refresh button
if st.button(translate("mediaManager.actions.refreshCourses.label"), type="primary", help=translate("mediaManager.actions.refreshCourses.help")):
    st.cache_data.clear()
    st.rerun()

with st.spinner(translate("mediaManager.loading.courses")):
    courses = fetch_courses(headers)

st.write(translate("mediaManager.status.foundCourses", count=len(courses)))  # Debug info

if not courses:
    st.info(translate("mediaManager.empty.noCourses.title"))
    st.caption(translate("mediaManager.empty.noCourses.tip"))
    with st.expander(translate("mediaManager.empty.noCourses.troubleshooting")):
        st.write(translate("mediaManager.empty.noCourses.apiUrl", url=BACKEND_API_URL + "/api/course/my_courses"))
        st.write(translate("mediaManager.empty.noCourses.tokenPresent", value="Yes" if st.session_state.get('token') else "No"))
        st.write(translate("mediaManager.empty.noCourses.userRole", role=st.session_state.get('role', 'Unknown')))
    st.stop()

# Course selector
st.subheader(translate("mediaManager.courseSelector.header"))
course_titles = {c["course_id"]: c["title"] for c in courses}
selected_course_id = st.selectbox(
    translate("mediaManager.courseSelector.label"),
    options=list(course_titles.keys()),
    format_func=lambda x: course_titles[x],
    key="course_selector",
    help=translate("mediaManager.courseSelector.help")
)

st.session_state.selected_course_id = selected_course_id

st.divider()

# Upload section
st.subheader(translate("mediaManager.upload.header"))
uploaded_file = st.file_uploader(
    translate("mediaManager.upload.uploaderLabel"),
    type=["png", "jpg", "jpeg", "gif", "webp", "svg"],
    help=translate("mediaManager.upload.uploaderHelp")
)

if uploaded_file is not None:
    col1, col2 = st.columns([3, 1])
    with col1:
        st.image(uploaded_file, caption=translate("mediaManager.upload.previewCaption", filename=uploaded_file.name), width='stretch')
    with col2:
        st.write(translate("mediaManager.upload.sizeLabel", size=format_file_size(len(uploaded_file.getvalue()))))
        if st.button(translate("mediaManager.actions.uploadImage.label"), type="primary", width='stretch', help=translate("mediaManager.actions.uploadImage.help")):
            upload_image(selected_course_id, uploaded_file)

st.divider()

# Images gallery
st.subheader(translate("mediaManager.gallery.header"))

images = fetch_course_images(selected_course_id)

if not images:
    st.info(translate("mediaManager.empty.noImages"))
else:
    st.write(translate("mediaManager.gallery.total", count=len(images)))
    
    # Display images in a grid
    cols_per_row = 3
    for idx in range(0, len(images), cols_per_row):
        cols = st.columns(cols_per_row)
        
        for col_idx, col in enumerate(cols):
            img_idx = idx + col_idx
            if img_idx < len(images):
                img = images[img_idx]
                
                with col:
                    with st.container(border=True):
                        # Display image with uniform size
                        image_url = f"{BACKEND_API_URL}{img['url']}"
                        try:
                            response = requests.get(image_url, headers=headers, timeout=10)
                            if response.status_code == 200:
                                # Use HTML container for uniform aspect ratio
                                st.markdown(
                                    f'<div class="image-gallery-container">'
                                    f'<img src="data:image/{img["content_type"].split("/")[-1]};base64,{__import__("base64").b64encode(response.content).decode()}" />'
                                    f'</div>',
                                    unsafe_allow_html=True
                                )
                        except:
                            st.error(translate("mediaManager.gallery.loadFailed"))
                        
                        # Image info
                        st.caption(f"**{img['filename']}**")
                        st.caption(translate("mediaManager.gallery.meta.size", size=format_file_size(img['file_size'])))
                        st.caption(translate("mediaManager.gallery.meta.uploadedAt", date=format_date(img['uploaded_at'])))
                        
                        # Show the markdown reference to copy
                        st.caption(translate("mediaManager.gallery.copyHint"))
                        markdown_ref = f"![{img['filename']}]({img['url']})"
                        st.code(markdown_ref, language="markdown")
                        
                        # Delete button
                        if st.button(
                            translate("mediaManager.gallery.delete.label"),
                            key=f"delete_{img['image_id']}",
                            width='stretch',
                            type="primary",
                            help=translate("mediaManager.gallery.delete.help")
                        ):
                            st.session_state.confirm_delete_image_id = img['stored_filename']
                            st.session_state.confirm_delete_image_course = selected_course_id
                            st.rerun()

# Show delete confirmation dialog
if st.session_state.confirm_delete_image_id is not None:
    confirm_delete_dialog()
