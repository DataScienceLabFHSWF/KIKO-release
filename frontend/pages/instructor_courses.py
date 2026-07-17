# frontend/pages/instructor_courses.py
import os, streamlit as st, requests
from pages.sidebar import render_sidebar
from utils import require_login
from utils.helper_utils import format_date
from i18n import translate
from topbar import language_topbar
from components import render_course_experience, render_instructor_course_editor, build_save_payload_from_course_json

st.set_page_config(page_title="My Courses", page_icon="📚", layout="wide")

require_login()
render_sidebar()

BACKEND_API_URL = os.getenv("BACKEND_API_URL")

# check if BACKEND_API_URL is set
if not BACKEND_API_URL:
    st.error(translate("error.env"))
    st.stop()

# Always show top-right language switch
language_topbar()

headers = {"Authorization": f"Bearer {st.session_state.token}"}

# ---- Delete confirmation state + dialog ----
if "confirm_delete_course_id" not in st.session_state:
    st.session_state.confirm_delete_course_id = None
if "view_course_id" not in st.session_state:
    st.session_state.view_course_id = None
if "course_view_mode" not in st.session_state:
    st.session_state.course_view_mode = {}
if "course_edit_cache" not in st.session_state:
    st.session_state.course_edit_cache = {}

def fetch_courses(_api, _headers):
    r = requests.get(f"{_api}/api/course/my_courses", headers=_headers)
    if r.status_code != 200:
        try:
            detail = r.json().get("detail")
        except Exception:
            detail = r.text
        raise RuntimeError(detail or translate("instructorCourses.errors.fetch", code=r.status_code))
    return r.json()

def fetch_course_detail(_api, _headers, course_id: int):
    r = requests.get(f"{_api}/api/course/{course_id}", headers=_headers)
    if r.status_code != 200:
        try:
            detail = r.json().get("detail")
        except Exception:
            detail = r.text
        raise RuntimeError(detail or translate("instructorCourses.errors.details"))
    return r.json()

# ---------- Dialogs ----------
@st.dialog(translate("instructorCourses.confirmDelete.title"))
def confirm_delete_course_dialog():
    course_id = st.session_state.confirm_delete_course_id
    st.write(translate("instructorCourses.confirmDelete.message", courseId=course_id))
    c_yes, c_no = st.columns(2)
    
    with c_yes:
        if st.button(
            translate("instructorCourses.confirmDelete.yes.label"), 
            type="primary", 
            key=f"dlg_yes_{course_id}", 
            help=translate("instructorCourses.confirmDelete.yes.help")
        ):
            r = requests.delete(
                f"{BACKEND_API_URL}/api/course/{course_id}",
                headers=headers
            )
            if r.status_code == 200 or r.status_code == 204:
                st.toast(translate("instructorCourses.confirmDelete.toast"), icon="🧹")
                st.session_state.confirm_delete_course_id = None
                st.rerun()
            else:
                try:
                    detail = r.json().get("detail")
                except Exception:
                    detail = r.text
                st.error(translate("instructorCourses.errors.delete", code=r.status_code, detail=detail))
                st.session_state.confirm_delete_course_id = None
                st.rerun()
    with c_no:
        if st.button(
            translate("instructorCourses.confirmDelete.no.label"), 
            type="primary", 
            key=f"dlg_no_{course_id}", 
            help=translate("instructorCourses.confirmDelete.no.help")
        ):
            st.session_state.confirm_delete_course_id = None
            st.rerun()

st.title(translate("instructorCourses.pageTitle"))
st.markdown(translate("instructorCourses.subtitle"))
st.divider()

courses = []
try:
    courses = fetch_courses(BACKEND_API_URL, headers)
except Exception as e:
    st.error(f"❌ {e}")

# Toolbar
c1, c2 = st.columns([1, 5])
if c1.button(
    translate("instructorCourses.toolbar.create"), 
    type="primary", 
    help=translate("instructorCourses.toolbar.help")
):
    st.switch_page("pages/instructor_course_creation.py")

st.divider()

if not courses:
    st.info(translate("instructorCourses.no_available_courses"))
else:
    # Add column headers
    h1, h2, h3, h4, h5 = st.columns([1, 4, 3, 2, 3])
    h1.markdown(translate("instructorCourses.table.headers.courseId"))
    h2.markdown(translate("instructorCourses.table.headers.title"))
    h3.markdown(translate("instructorCourses.table.headers.dateCreated"))
    h4.markdown(translate("instructorCourses.table.headers.view"))
    h5.markdown(translate("instructorCourses.table.headers.delete"))
    
    for row in courses:
        course_id = row["course_id"]

        with st.container():
            c1, c2, c3, c4, c5 = st.columns([1, 4, 3, 2, 3])
            c1.markdown(f"<b>{course_id}</b>", unsafe_allow_html=True)
            c2.markdown(f"<b>{row.get('title') or '—'}</b>", unsafe_allow_html=True)
            c3.markdown(f"{format_date(row.get('created_at') or '')}")
            
            view_btn = c4.button(
                translate("instructorCourses.table.row.view.label"),
                type="primary",
                key=f"view_{course_id}", 
                help=translate("instructorCourses.table.row.view.help")
            )
            
            if view_btn:
                st.session_state.view_course_id = course_id
            
            del_btn = c5.button(
                translate("instructorCourses.table.row.delete.label"),
                type="primary",
                key=f"del_{course_id}",
                help=translate("instructorCourses.table.row.delete.help"),
            )
            
            if del_btn:
                st.session_state.confirm_delete_course_id = course_id
                confirm_delete_course_dialog()  # open the dialog
            
        # Dropdown for course details
        if st.session_state.get("view_course_id") == course_id:
            with st.expander(
                translate("instructorCourses.expander.id", id=course_id, title=row.get('title','')), 
                expanded=True
            ):
                try:
                    data = fetch_course_detail(BACKEND_API_URL, headers, course_id)
                except Exception as e:
                    st.error(str(e))
                    continue

                course = data.get("course", {})
                course_json = data.get("course_json") or {}
                template_markdown = data.get("template_markdown") or ""

                if not course_json:
                    st.error(translate("instructorCourses.course_json_error"))
                    continue

                cache_key = f"course_{course_id}"
                if cache_key not in st.session_state.course_edit_cache:
                    st.session_state.course_edit_cache[cache_key] = course_json

                current_mode = st.session_state.course_view_mode.get(course_id, "preview")

                label_preview = translate("instructorCourses.expander.viewMode.preview")
                label_edit = translate("instructorCourses.expander.viewMode.edit")
                help_preview = translate("instructorCourses.expander.viewMode.previewHelp")
                help_edit = translate("instructorCourses.expander.viewMode.editHelp")

                col_spacer, col_preview, col_edit = st.columns([6, 1.5, 1.5])

                if col_preview.button(
                    label_preview,
                    key=f"mode_preview_{course_id}",
                    type="primary",
                    width='stretch',
                    disabled=(current_mode == "preview"),
                    help=help_preview,
                ):
                    st.session_state.course_view_mode[course_id] = "preview"
                    st.rerun()

                if col_edit.button(
                    label_edit,
                    key=f"mode_edit_{course_id}",
                    type="primary",
                    width='stretch',
                    disabled=(current_mode == "edit"),
                    help=help_edit,
                ):
                    st.session_state.course_view_mode[course_id] = "edit"
                    st.rerun()

                st.divider()

                if current_mode == "preview":
                    render_course_experience(
                        st.session_state.course_edit_cache[cache_key],
                        mode="instructor_preview",
                        state_prefix=f"instructor_course_preview_{course_id}",
                        show_sidebar_nav=True,
                        request_headers=headers,
                    )

                    with st.expander(translate("instructorCourses.raw_markdown.expander"), expanded=False):
                        st.code(template_markdown or translate("instructorCourses.raw_markdown.no_stored"), language="markdown")

                else:
                    top_left, top_right = st.columns([1, 6])
                    if top_left.button(
                        translate("instructorCourses.reset_changes.label"),
                        key=f"reset_course_editor_{course_id}",
                        type="primary",
                        width='stretch',
                        help=translate("instructorCourses.reset_changes.help")
                    ):
                        st.session_state.course_edit_cache[cache_key] = course_json
                        st.rerun()

                    edited_course_json, editor_validation_errors, _ = render_instructor_course_editor(
                        st.session_state.course_edit_cache[cache_key],
                        state_prefix=f"instructor_course_editor_{course_id}",
                        request_headers=headers,
                    )
                    st.session_state.course_edit_cache[cache_key] = edited_course_json

                    if editor_validation_errors:
                        st.info(translate("courseGenerator.pagination.editor_validation_errors"))

                    st.markdown("---")
                    save_btn = st.button(
                        translate("instructorCourses.save.label"),
                        type="primary",
                        key=f"save_md_course_{course_id}",
                        help=translate("instructorCourses.save.help"),
                        disabled=bool(editor_validation_errors),
                    )

                    if save_btn:
                        try:
                            built = build_save_payload_from_course_json(
                                edited_course_json,
                                title_override=((edited_course_json.get("course") or {}).get("title") or course.get("title") or ""),
                            )

                            payload = {
                                "title": built["title"],
                                "summary": built["summary"],
                                "questions": built["questions"],
                                "quiz": built["quiz"],
                                "template_markdown": built["template_markdown"],
                                "course_json": built["course_json"],
                            }

                            r = requests.put(
                                f"{BACKEND_API_URL}/api/course/{course_id}",
                                json=payload,
                                headers=headers,
                            )

                            if r.status_code == 200:
                                st.session_state.course_edit_cache[cache_key] = built["course_json"]
                                st.success(translate("instructorCourses.save.success"))
                                st.rerun()
                            else:
                                try:
                                    detail = r.json().get("detail")
                                except Exception:
                                    detail = r.text
                                st.error(detail or translate("instructorCourses.errors.update", code=r.status_code))
                        except Exception as e:
                            st.error(str(e))
