# Utility helpers functions for the KIKO platform frontend.
import os, streamlit as st, logging, requests, re
from datetime import datetime
from dotenv import load_dotenv
from i18n import translate

logger = logging.getLogger(__name__)

# Load API URL from environment variables
load_dotenv()
BACKEND_API_URL = os.getenv("BACKEND_API_URL")

STATUS_BADGE = {
    "processed": translate("helper.status.processed"),
    "exists": translate("helper.status.exists"),
    "error": translate("helper.status.error"),
}

FILE_EMOJI = {
    ".pdf": "📕",
    ".md": "📝",
    ".markdown": "📝",
    ".txt": "📄",
    ".docx": "🗎",
    ".pptx": "🖥️",
    ".xlsx": "📊",
}

def grade_label(grade: int | None) -> str:
    mapping = {
        1: translate("helper.grade.very_good"),
        2: translate("helper.grade.good"),
        3: translate("helper.grade.satisfactory"),
        4: translate("helper.grade.sufficient"),
        5: translate("helper.grade.insufficient"),
    }
    return mapping.get(grade, "—")

def grade_status_variant(grade: int | None) -> str:
    if grade is None:
        return "info"
    if grade in (1, 2):
        return "success"
    if grade == 3:
        return "warning"
    return "error"

def format_date(iso_timestamp: str) -> str:
    """
    Converts ISO datetime string to a human-readable format.
    Example output: "June 23, 2025 - 09:50 AM"
    """
    try:
        dt = datetime.fromisoformat(iso_timestamp.replace("Z", "+00:00"))
        return dt.strftime("%B %d, %Y - %I:%M %p")
    except Exception:
        return translate("helper.date.invalid")

# Helper to get backend config
def get_backend_app_config_library(api_url, headers):
    try:
        resp = requests.get(f"{api_url}/api/app_configurations/app_config", headers=headers)
        if resp.status_code == 200:
            response = resp.json()
            return response
    except Exception:
        pass
    return {}

# Helper to get user profile
def get_user_profile(token):
    """Fetch user profile from backend using the provided token."""

    response = requests.get(
        f"{BACKEND_API_URL}/api/profile/user_info",
        headers={"Authorization": f"Bearer {token}"},
    )
    if response.status_code == 200:
        return response.json()
    return None

def initialize_session_state():
    """Initialize enhanced session state variables."""
    
    print("ℹ️ Initializing defaults session state variables...")    
    defaults = {
        'messages': [],
        'vector_store': None,
        'chain': None,
        'processed_files': set(),
        'document_map': {},
        'show_sources': {},
        'temp_input': "",
        'processed_file_hashes': set(),
        'processed_folders': {},
        'folder_input': "",
        'folder_path': None,
        'processing_stats': {
            'documents': 0,
            'total_time': 0,
            'avg_time': 0,
            'accuracy': 0
        },
        'usage_stats': {
            'total_queries': 0,
            'total_time': 0,
            'avg_confidence': 0
        }
    }
        
    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value
    print("✅ Successfully initialized session state variables.")

def format_time(seconds: float) -> str:
    """Format time in seconds to a human-readable string."""

    if seconds < 0.001:
        return f"{seconds * 1000000:.2f} μs"
    elif seconds < 1:
        return f"{seconds * 1000:.2f} ms"
    else:
        return f"{seconds:.2f} s"

def status_text(s: str) -> str:
    """Map status code to human-readable text with emoji."""

    s = (s or "").lower()
    return STATUS_BADGE.get(s, translate("helper.status.unknown"))

def show_file_status_list(payload: dict):
    """Display a list of file upload results in the Streamlit app."""
    
    files = payload.get("files", []) or []
    if not files:
        st.info(translate("helper.fileStatus.noResults"))
        return

    st.subheader(translate("helper.fileStatus.uploadResults"))
    # Simple, compact list
    for item in files:
        name = item.get("file_name", "—")
        st.markdown(f"- **{name}** — {status_text(item.get('status'))}")

def extension_of(name: str) -> str:
    name = name.lower()
    for ext in FILE_EMOJI.keys():
        if name.endswith(ext):
            return ext
    return os.path.splitext(name)[1].lower()

def file_emoji(name: str) -> str:
    return FILE_EMOJI.get(extension_of(name), "📦")

def fetch_bytes(url: str, headers: dict) -> bytes | None:
    try:
        r = requests.get(url, headers=headers)
        r.raise_for_status()
        return r.content
    except Exception as e:
        st.toast(translate("helper.download.failed", error=str(e)), icon="❌")
        return None

def render_markdown_with_images(markdown_text: str, headers: dict = None):
    """
    Render markdown content with support for authenticated course images.

    Supports markdown image syntax:
      ![alt text](url)

    Behavior:
    - /api/course/... URLs are fetched from the backend using auth headers
    - http/https URLs are shown directly
    - all non-image markdown text is still rendered normally
    """

    if not markdown_text:
        return
    
    # Pattern to match markdown images: ![alt](url)
    image_pattern = r'!\[([^\]]*)\]\(([^)]+)\)'
    
    # Find all images in the markdown text
    images = list(re.finditer(image_pattern, markdown_text))

    if not images:
        # No images found, just render as markdown
        st.markdown(markdown_text, unsafe_allow_html=True)
        return
    
    # Process text with images in sequence
    last_end = 0

    for match in images:
        # Render text before the image
        text_before = markdown_text[last_end:match.start()]
        if text_before.strip():
            st.markdown(text_before, unsafe_allow_html=True)
        
        # Extract image info
        alt_text = (match.group(1) or "").strip()
        image_url = (match.group(2) or "").strip()

        if image_url.startswith("/api/course/"):
            if not BACKEND_API_URL:
                st.warning(f"⚠️ Backend API URL is not configured, cannot load image: {image_url}")
            else:
                full_url = f"{BACKEND_API_URL}{image_url}"
                try:
                    response = requests.get(
                        full_url,
                        headers=headers or {},
                        timeout=15,
                    )

                    if response.status_code == 200:
                        content_type = (response.headers.get("content-type") or "").lower()

                        if content_type.startswith("image/"):
                            col1, col2, col3 = st.columns([1, 3, 1])
                            with col2:
                                st.image(
                                    response.content,
                                    caption=alt_text or None,
                                    width='stretch',
                                )
                        else:
                            st.warning(translate("helper.image.notFound", status=response.status_code, url=image_url))
                    else:
                        st.warning(translate("helper.image.noAuth", url=image_url))
                except Exception as e:
                    st.error(translate("helper.image.loadError", url=image_url, error=str(e)))
        elif image_url.startswith(("http://", "https://")):
            col1, col2, col3 = st.columns([1, 3, 1])
            with col2:
                st.image(
                    image_url,
                    caption=alt_text or None,
                    width='stretch',
                )
        else:
            st.warning(translate("helper.image.unsupportedPath", url=image_url))
        
        last_end = match.end()
    
    # Render any remaining text after the last image
    remaining_text = markdown_text[last_end:]
    if remaining_text.strip():
        st.markdown(remaining_text, unsafe_allow_html=True)
