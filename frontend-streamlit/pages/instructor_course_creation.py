# frontend/pages/instructor_course_creation.py
import os, io, streamlit as st, requests, json, yaml
from typing import Optional, Any
from pages.sidebar import render_sidebar
from utils import require_login, get_backend_app_config_library
from i18n import translate
from topbar import language_topbar
from http_headers import auth_headers
from copy import deepcopy
from components import render_instructor_course_editor, build_save_payload_from_course_json

GRADING_MODEL_OPTIONS = (
    "nemotron-3-super:120b",
    "deepseek-r1:70b",
)

def normalize_grading_model(model_name: Optional[str]) -> str:
    """Return a valid grading model, falling back to the first supported option."""
    if model_name in GRADING_MODEL_OPTIONS:
        return model_name
    return GRADING_MODEL_OPTIONS[0]

# Set page config
st.set_page_config(
    page_title=translate("courseGenerator.page.pageTitle"),
    page_icon="✍️",
    layout="wide"
)

# Check if the user is logged in
require_login()

# Load API URL and token
BACKEND_API_URL = os.getenv("BACKEND_API_URL")
if not BACKEND_API_URL:
    st.error(translate("courseGenerator.errors.envMissing"))
    st.stop()

# Always show top-right language switch
language_topbar()

headers = {"Authorization": f"Bearer {st.session_state.token}"}

token = st.session_state.token

# Render the sidebar
render_sidebar()

st.title(translate("courseGenerator.page.title"))
st.markdown(translate("courseGenerator.page.subtitle"))
st.divider()

SESSION_DEFAULTS = {
    "summary": None,
    "questions": None,
    "quiz": "",
    "template_markdown": None,
    "course_json": None,
    "editable_course_json": None,
    "course_metadata": None,
    "course_editor_version": 0,
    "markdown_replace_prompt": False,
    "markdown_replace_detail": None,
    "markdown_replace_metadata": {},
    "markdown_replace_existing": None,
    "last_upload_bytes": None,
    "last_upload_name": None,
    "last_upload_mime": None,
    "last_upload_embedding": None,
    "last_upload_llm": None,
    "generated_markdown": None,
    "generated_markdown_file_name": "generated-course.md",
    "qa_user_answers": {},
    "qa_summaries": {},
    "qa_grading_models": {},
    "qa_widget_version": 0,
    "save_course_clicked": False,
    "course_saved_for_upload": False,
    "course_saved_filename": None,
    "pdf_upload_job_id": None,
    "pdf_upload_job_status": None,
    "pdf_upload_job_progress": 0.0,
    "pdf_upload_job_message": None,
    "pdf_upload_job_stage_key": None,
    "upload_status_message_level": None,
    "upload_status_message_text": None,
}

for _key, _value in SESSION_DEFAULTS.items():
    if _key not in st.session_state:
        st.session_state[_key] = _value

def last_upload_is_pdf() -> bool:
    """Return True if the most recent document upload was a PDF."""
    mime = (st.session_state.get("last_upload_mime") or "").lower()
    return mime == "application/pdf"


def set_upload_status_message(level: str, text: str):
    st.session_state.upload_status_message_level = level
    st.session_state.upload_status_message_text = text


def render_upload_status_message():
    level = st.session_state.get("upload_status_message_level")
    text = st.session_state.get("upload_status_message_text")
    if not level or not text:
        return

    if level == "success":
        st.success(text)
    elif level == "warning":
        st.warning(text)
    else:
        st.error(text)

    st.session_state.upload_status_message_level = None
    st.session_state.upload_status_message_text = None


def clear_pdf_upload_job_state():
    st.session_state.pdf_upload_job_id = None
    st.session_state.pdf_upload_job_status = None
    st.session_state.pdf_upload_job_progress = 0.0
    st.session_state.pdf_upload_job_message = None
    st.session_state.pdf_upload_job_stage_key = None


def pdf_upload_job_is_active() -> bool:
    return (
        bool(st.session_state.get("pdf_upload_job_id"))
        and st.session_state.get("pdf_upload_job_status") in {None, "queued", "processing", "cancelling"}
    )


def reset_replace_prompt_state():
    st.session_state.markdown_replace_prompt = False
    st.session_state.markdown_replace_detail = None
    st.session_state.markdown_replace_metadata = {}
    st.session_state.markdown_replace_existing = None

def clear_qa_widget_state():
    """Remove stored Streamlit widget values for QA answer text areas."""
    st.session_state.qa_widget_version = (st.session_state.get("qa_widget_version", 0) + 1) % 1_000_000
    keys_to_remove = [key for key in st.session_state.keys() if key.startswith("user_ans_")]
    for key in keys_to_remove:
        del st.session_state[key]

def clear_generated_course_preview_state():
    """Clear generated course preview/editor payload so a new upload can replace it cleanly."""
    clear_qa_widget_state()
    st.session_state.qa_user_answers = {}
    st.session_state.qa_summaries = {}
    st.session_state.qa_grading_models = {}
    st.session_state.qa_page = 1
    st.session_state.qa_page_size = 5

    st.session_state.summary = None
    st.session_state.questions = None
    st.session_state.quiz = ""
    st.session_state.template_markdown = None
    st.session_state.course_json = None
    st.session_state.editable_course_json = None
    st.session_state.course_metadata = None
    st.session_state.generated_markdown = None
    st.session_state.generated_markdown_file_name = "generated-course.md"

    st.session_state.course_editor_version = (st.session_state.get("course_editor_version", 0) + 1) % 1_000_000
    editor_version_key = "course_creation_editor_editor_version"
    st.session_state[editor_version_key] = (st.session_state.get(editor_version_key, 0) + 1) % 1_000_000

def send_course_upload_request(
    api_url: Optional[str],
    headers: dict[str, str],
    file_name: str,
    file_bytes: bytes,
    mime: str,
    embedding_model: str,
    llm_model: str,
    qa_count: int,
    quiz_question_count: int,
    quiz_option_count: int,
    misconception_count: int,
    replace_existing: bool = False,
):
    if not api_url:
        raise ValueError(translate("courseGenerator.errors.apiURLRequired"))

    files = {
        "file": (file_name, io.BytesIO(file_bytes), mime),
    }
    data_payload = {
        "embedding_model_name": embedding_model,
        "llm_model_name": llm_model,
        "qa_count": str(int(qa_count)),
        "quiz_question_count": str(int(quiz_question_count)),
        "quiz_option_count": str(int(quiz_option_count)),
        "misconception_count": str(int(misconception_count)),
        "replace_existing": str(bool(replace_existing)).lower(),
    }
    return requests.post(
        f"{api_url}/api/course/upload_course_document",
        headers=headers,
        files=files,
        data=data_payload,
    )

def start_pdf_course_upload_job(
    api_url: Optional[str],
    headers: dict[str, str],
    file_name: str,
    file_bytes: bytes,
    mime: str,
    embedding_model: str,
    llm_model: str,
    qa_count: int,
    quiz_question_count: int,
    quiz_option_count: int,
    misconception_count: int,
):
    if not api_url:
        raise ValueError(translate("courseGenerator.errors.apiURLRequired"))

    files = {
        "file": (file_name, io.BytesIO(file_bytes), mime),
    }
    data_payload = {
        "embedding_model_name": embedding_model,
        "llm_model_name": llm_model,
        "qa_count": str(int(qa_count)),
        "quiz_question_count": str(int(quiz_question_count)),
        "quiz_option_count": str(int(quiz_option_count)),
        "misconception_count": str(int(misconception_count)),
    }
    return requests.post(
        f"{api_url}/api/course/upload_course_document_pdf_job",
        headers=headers,
        files=files,
        data=data_payload,
    )


def fetch_pdf_course_upload_job(
    api_url: Optional[str],
    headers: dict[str, str],
    job_id: str,
):
    if not api_url:
        raise ValueError(translate("courseGenerator.errors.apiURLRequired"))
    return requests.get(
        f"{api_url}/api/course/upload_course_document_pdf_job/{job_id}",
        headers=headers,
    )


def cancel_pdf_course_upload_job(
    api_url: Optional[str],
    headers: dict[str, str],
    job_id: str,
):
    if not api_url:
        raise ValueError(translate("courseGenerator.errors.apiURLRequired"))
    return requests.post(
        f"{api_url}/api/course/upload_course_document_pdf_job/{job_id}/cancel",
        headers=headers,
    )


def handle_course_upload_payload(
    data: dict[str, Any],
    response_status: int = 200,
    success_notice: Optional[str] = "Processing complete!",
    display_feedback: bool = True,
):
    if response_status != 200:
        if display_feedback:
            st.error(data.get("detail", translate("courseGenerator.status.error", error=response_status)))
        return "error"

    message = data.get("message")

    if message == "markdown_exists":
        st.session_state.markdown_replace_prompt = True
        st.session_state.markdown_replace_detail = data.get("detail")
        st.session_state.markdown_replace_metadata = data.get("metadata") or {}
        st.session_state.markdown_replace_existing = data.get("existing_document") or {}
        return "await_confirm"

    if message == "success":
        clear_qa_widget_state()
        st.session_state.qa_user_answers = {}
        st.session_state.qa_summaries = {}
        st.session_state.qa_grading_models = {}
        st.session_state.qa_page = 1
        st.session_state.qa_page_size = 5

        st.session_state.summary = data.get("final_summary")
        st.session_state.questions = data.get("questions")
        st.session_state.quiz = data.get("quiz") or ""
        st.session_state.template_markdown = data.get("template_markdown")
        st.session_state.course_json = data.get("course_json")
        st.session_state.editable_course_json = deepcopy(data.get("course_json") or {})
        st.session_state.course_metadata = data.get("metadata") or {}
        st.session_state.course_editor_version = (st.session_state.get("course_editor_version", 0) + 1) % 1_000_000
        editor_version_key = "course_creation_editor_editor_version"
        st.session_state[editor_version_key] = (st.session_state.get(editor_version_key, 0) + 1) % 1_000_000

        st.session_state.generated_markdown = data.get("generated_markdown")
        st.session_state.generated_markdown_file_name = data.get("generated_markdown_file_name") or "generated-course.md"
        if success_notice and display_feedback:
            st.success(success_notice)
        reset_replace_prompt_state()
        return "success"
    
    if message == "file_exists":
        if display_feedback:
            st.warning(data.get("detail", translate("courseGenerator.upload.fileExists")))
        reset_replace_prompt_state()
        return "exists"

    if display_feedback:
        st.error(data.get("detail", translate("courseGenerator.errors.unknownServerResponse")))
    return "error"


def handle_course_upload_response(response, success_notice: Optional[str] = "Processing complete!"):
    try:
        data = response.json()
    except Exception:
        st.error(translate("courseGenerator.errors.invalidServerResponse"))
        return "error"

    return handle_course_upload_payload(
        data,
        response_status=response.status_code,
        success_notice=success_notice,
        display_feedback=True,
    )


render_upload_status_message()

@st.dialog(translate("courseGenerator.replaceDialog.title"))
def confirm_replace_dialog():
    detail = st.session_state.markdown_replace_detail
    metadata = st.session_state.markdown_replace_metadata or {}
    existing = st.session_state.markdown_replace_existing or {}
    file_name = st.session_state.last_upload_name or metadata.get("title") or "this document"

    st.write(detail or translate("courseGenerator.replaceDialog.bodyDefault"))

    if metadata:
        doc_id = metadata.get("id")
        st.markdown(translate("courseGenerator.replaceDialog.markdownId", doc_id=doc_id))
        if existing:
            st.caption(translate("courseGenerator.replaceDialog.storedAs", fileName=existing.get('file_name', 'unknown'), uploadedAt=existing.get('uploaded_at', 'unknown')))

    col_yes, col_no = st.columns(2)

    with col_yes:
        if st.button(translate("courseGenerator.replaceDialog.replaceButton"), type="primary", key="replace_markdown_yes"):
            file_bytes = st.session_state.last_upload_bytes
            mime = st.session_state.last_upload_mime
            embed_model = st.session_state.last_upload_embedding
            llm_model = st.session_state.last_upload_llm
            qa_count = _session_int_or_default("last_upload_qa_count", qa_default_value)
            quiz_question_count = _session_int_or_default(
                "last_upload_quiz_question_count",
                quiz_question_default_value,
            )
            quiz_option_count = _session_int_or_default(
                "last_upload_quiz_option_count",
                quiz_option_default_value,
            )
            misconception_count = _session_int_or_default(
                "last_upload_misconception_count",
                misconception_default_value,
            )

            if not file_bytes or not file_name or not embed_model or not llm_model or not mime:
                st.error(translate("courseGenerator.errors.fileDataMissing"))
                return

            try:
                with st.spinner(translate("courseGenerator.upload.spinners.replacing")):
                    response = send_course_upload_request(
                        BACKEND_API_URL,
                        auth_headers(token),
                        file_name,
                        file_bytes,
                        mime,
                        embed_model,
                        llm_model,
                        qa_count=qa_count,
                        quiz_question_count=quiz_question_count,
                        quiz_option_count=quiz_option_count,
                        misconception_count=misconception_count,
                        replace_existing=True,
                    )
            except Exception as exc:
                st.error(translate("courseGenerator.status.error", error=exc))
                return

            result = handle_course_upload_response(response, success_notice=None)

            if result == "success":
                reset_replace_prompt_state()
                st.rerun()

    with col_no:
        if st.button(translate("courseGenerator.replaceDialog.cancelButton"), type="primary", key="replace_markdown_no"):
            reset_replace_prompt_state()
            st.rerun()

def render_generated_qa_table(
    questions_data: list[dict],
    default_reasoning_model: str,
    app_config_data: dict,
):
    st.header(translate("courseGenerator.qa.header"))
    st.markdown("---")

    if "qa_user_answers" not in st.session_state:
        st.session_state.qa_user_answers = {}
    if "qa_summaries" not in st.session_state:
        st.session_state.qa_summaries = {}
    if "qa_page" not in st.session_state:
        st.session_state.qa_page = 1
    if "qa_page_size" not in st.session_state:
        st.session_state.qa_page_size = 5

    total_questions = len(questions_data)
    page_size_options = [5, 10, 20, 50]

    control_left, control_mid, control_right = st.columns([1.2, 1.2, 2.6])

    with control_left:
        selected_page_size = st.selectbox(
            translate("courseGenerator.pagination.rows_per_page"),
            options=page_size_options,
            index=page_size_options.index(st.session_state.qa_page_size)
            if st.session_state.qa_page_size in page_size_options
            else 0,
            key="qa_page_size_selector",
        )
        if selected_page_size != st.session_state.qa_page_size:
            st.session_state.qa_page_size = selected_page_size
            st.session_state.qa_page = 1
            st.rerun()

    page_size = st.session_state.qa_page_size
    total_pages = max(1, (total_questions + page_size - 1) // page_size)

    if st.session_state.qa_page > total_pages:
        st.session_state.qa_page = total_pages
    if st.session_state.qa_page < 1:
        st.session_state.qa_page = 1

    page_options = list(range(1, total_pages + 1))
    
    with control_mid:
        selected_page = st.selectbox(
            translate("courseGenerator.pagination.mid_page_label"),
            options=page_options,
            index=page_options.index(st.session_state.qa_page) if st.session_state.qa_page in page_options else 0,
        )
        
        if selected_page != st.session_state.qa_page:
            st.session_state.qa_page = selected_page
            st.rerun()
    
    start_idx = (st.session_state.qa_page - 1) * page_size
    end_idx = min(start_idx + page_size, total_questions)
    paginated_questions = questions_data[start_idx:end_idx]

    with control_right:
        shown_count = len(paginated_questions)
        st.markdown(
            f"""
            <div style="padding-top: 1.9rem; text-align: right; color: #64748b;">
                Showing <b>{start_idx + 1 if total_questions else 0}</b>–<b>{end_idx}</b>
                of <b>{total_questions}</b> questions
            </div>
            """,
            unsafe_allow_html=True,
        )
    
    st.markdown("---")
    
    hdr = st.columns([0.5, 2.5, 2.5, 2.5, 1.8, 1.5, 2.5])
    hdr[0].markdown(translate("courseGenerator.qa.table.no"))
    hdr[1].markdown(translate("courseGenerator.qa.table.question"))
    hdr[2].markdown(translate("courseGenerator.qa.table.llmAnswer"))
    hdr[3].markdown(translate("courseGenerator.qa.table.yourAnswer"))
    hdr[4].markdown(translate("courseGenerator.qa.table.gradingModel"))
    hdr[5].markdown(translate("courseGenerator.qa.table.action"))
    hdr[6].markdown(translate("courseGenerator.qa.table.gradeSummary"))

    widget_version = st.session_state.get("qa_widget_version", 0)

    for absolute_idx, qa in enumerate(paginated_questions, start=start_idx + 1):
        with st.container():
            st.markdown(
                """
                <div style="border:1px solid #DDD; border-radius:10px; padding:10px; margin-bottom:10px;">
                """,
                unsafe_allow_html=True,
            )

            q_text = qa.get("question", "")
            ref_ans = qa.get("answer", "")

            c1, c2, c3, c4, c5, c6, c7 = st.columns([0.5, 2.5, 2.5, 2.5, 1.8, 1.5, 2.5])

            c1.write(absolute_idx)
            c2.markdown(q_text or "—")
            c3.markdown(ref_ans or "—")

            ans_key = f"user_ans_{widget_version}_{absolute_idx}"
            default_txt = st.session_state.qa_user_answers.get(absolute_idx, "")
            user_ans = c4.text_area(
                label=translate("courseGenerator.qa.rowYourAnswerLabel", row=absolute_idx),
                value=default_txt,
                key=ans_key,
                label_visibility="collapsed",
                height=120,
            )
            st.session_state.qa_user_answers[absolute_idx] = user_ans

            current_model = normalize_grading_model(
                st.session_state.qa_grading_models.get(absolute_idx, default_reasoning_model)
            )

            selected_model = c5.selectbox(
                label=translate("courseGenerator.qa.models.llmLabel", row=absolute_idx),
                options=GRADING_MODEL_OPTIONS,
                index=GRADING_MODEL_OPTIONS.index(current_model),
                key=f"grading_model_{absolute_idx}",
                label_visibility="collapsed",
                help=translate("courseGenerator.qa.models.llmHelp"),
            )
            st.session_state.qa_grading_models[absolute_idx] = selected_model

            if c6.button(
                translate("courseGenerator.qa.sendButton.label"),
                type="primary",
                key=f"grade_btn_{absolute_idx}",
                width="stretch",
                help=translate("courseGenerator.qa.sendButton.help"),
            ):
                if not user_ans.strip():
                    c6.error(translate("courseGenerator.qa.messages.enterAnswerFirst"))
                else:
                    with c6:
                        with st.spinner(translate("courseGenerator.qa.spinners.grading")):
                            try:
                                payload = {
                                    "question": q_text,
                                    "reference_answer": ref_ans,
                                    "user_answer": user_ans,
                                    "reasoning_model_name": selected_model,
                                }

                                r = requests.post(
                                    f"{BACKEND_API_URL}/api/course/answer_grading",
                                    json=payload,
                                    headers=auth_headers(token),
                                )

                                if r.status_code == 200:
                                    out = r.json()
                                    st.session_state.qa_summaries[absolute_idx] = out.get("summary", "")
                                    c6.success(translate("courseGenerator.qa.messages.graded"))
                                else:
                                    c6.error(
                                        translate(
                                            "courseGenerator.save.messages.saveError",
                                            error=r.status_code,
                                        )
                                    )
                            except Exception as e:
                                c6.error(translate("courseGenerator.status.error", error=e))

            c7.write(st.session_state.qa_summaries.get(absolute_idx, "—"))
            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")
    nav_left, nav_mid, nav_right = st.columns([1, 2, 1])

    with nav_left:
        if st.button(
            translate("courseGenerator.pagination.previous"), 
            disabled=st.session_state.qa_page <= 1, key="qa_prev_page_btn", 
            type="primary", 
            help=translate("courseGenerator.pagination.previous_help")
        ):
            st.session_state.qa_page -= 1
            st.rerun()
    
    with nav_mid:
        st.markdown(
            f"""
            <div style="text-align:center; padding-top:0.45rem; color:#64748b;">
                Page <b>{st.session_state.qa_page}</b> of <b>{total_pages}</b>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with nav_right:
        if st.button(
            translate("courseGenerator.pagination.next"), 
            disabled=st.session_state.qa_page >= total_pages, 
            key="qa_next_page_btn", 
            type="primary",
            help=translate("courseGenerator.pagination.next_help")
        ):
            st.session_state.qa_page += 1
            st.rerun()


@st.fragment(run_every="2s")
def render_pdf_upload_job_progress():
    job_id = st.session_state.get("pdf_upload_job_id")
    if not job_id:
        return

    try:
        response = fetch_pdf_course_upload_job(
            BACKEND_API_URL,
            auth_headers(token),
            job_id,
        )
        data = response.json()
    except Exception as exc:
        set_upload_status_message(
            "error",
            f"Could not refresh PDF processing status: {exc}",
        )
        clear_pdf_upload_job_state()
        st.rerun()
        return

    if response.status_code != 200:
        set_upload_status_message(
            "error",
            data.get(
                "detail",
                translate("courseGenerator.status.error", error=response.status_code),
            ),
        )
        clear_pdf_upload_job_state()
        st.rerun()
        return

    st.session_state.pdf_upload_job_status = data.get("status")
    st.session_state.pdf_upload_job_progress = float(data.get("progress") or 0.0)
    st.session_state.pdf_upload_job_message = data.get("message")
    st.session_state.pdf_upload_job_stage_key = data.get("stage_key")

    current_status = st.session_state.pdf_upload_job_status
    current_progress = st.session_state.pdf_upload_job_progress
    current_message = st.session_state.pdf_upload_job_message or "Processing PDF..."
    if current_status in {"queued", "processing", "cancelling"}:
        st.info(current_message)
        st.progress(
            min(max(current_progress, 0.0), 1.0),
            text=f"{int(min(max(current_progress, 0.0), 1.0) * 100)}% complete",
        )

        if current_status != "cancelling":
            if st.button(
                "Abort PDF processing",
                type="primary",
                key=f"abort_pdf_job_{job_id}",
                help="Cancel the current PDF processing job and discard temporary results.",
            ):
                try:
                    cancel_response = cancel_pdf_course_upload_job(
                        BACKEND_API_URL,
                        auth_headers(token),
                        job_id,
                    )
                    try:
                        cancel_data = cancel_response.json()
                    except ValueError:
                        cancel_data = None

                    if cancel_response.status_code != 200:
                        detail = (
                            cancel_data.get("detail")
                            if isinstance(cancel_data, dict)
                            else None
                        )
                        raise RuntimeError(
                            detail
                            or translate(
                                "courseGenerator.status.error",
                                error=cancel_response.status_code,
                            )
                        )

                    cancel_status = (
                        cancel_data.get("status")
                        if isinstance(cancel_data, dict)
                        else None
                    )
                    if not isinstance(cancel_status, str) or not cancel_status:
                        raise RuntimeError(
                            translate("courseGenerator.errors.invalidServerResponse")
                        )

                    st.session_state.pdf_upload_job_status = cancel_status
                    st.session_state.pdf_upload_job_message = cancel_data.get("message")
                    st.session_state.pdf_upload_job_stage_key = cancel_data.get("stage_key")
                    st.rerun()
                except Exception as exc:
                    st.error(f"Could not cancel the PDF processing job: {exc}")
        else:
            st.caption("Cancellation requested. The job will stop at the next safe checkpoint.")
        return

    if current_status == "completed":
        result = data.get("result") or {}
        job_message = result.get("message")
        handle_course_upload_payload(
            result,
            response_status=200,
            success_notice=None,
            display_feedback=False,
        )
        clear_pdf_upload_job_state()
        if job_message == "success":
            set_upload_status_message("success", "Processing complete!")
        elif job_message == "file_exists":
            set_upload_status_message(
                "warning",
                result.get("detail", translate("courseGenerator.upload.fileExists")),
            )
        st.rerun()
        return

    clear_pdf_upload_job_state()
    if current_status == "cancelled":
        set_upload_status_message(
            "warning",
            "PDF processing was cancelled. Temporary processing results were discarded.",
        )
        clear_generated_course_preview_state()
    else:
        set_upload_status_message(
            "error",
            data.get("error") or "PDF processing failed.",
        )
    st.rerun()


uploaded_file = st.file_uploader(
    translate("courseGenerator.upload.uploaderLabel"), 
    type=['pdf', 'md', 'markdown']
)
if uploaded_file is not None:
    if "last_uploaded_filename" not in st.session_state or st.session_state.last_uploaded_filename != uploaded_file.name:
        clear_generated_course_preview_state()
        st.session_state.save_course_clicked = False
        st.session_state.last_uploaded_filename = uploaded_file.name
        st.session_state.course_saved_for_upload = False
        st.session_state.course_saved_filename = uploaded_file.name

app_config_library_data = get_backend_app_config_library(BACKEND_API_URL, headers)

if not app_config_library_data:
    st.error(translate("courseGenerator.errors.emptyConfig"))
    st.stop()

app_config_data = app_config_library_data.get("app_config")

default_reasoning_model = normalize_grading_model(
    app_config_data.get("default_reasoning_model")
)


def _get_int_config(config: dict, key: str, fallback: int) -> int:
    try:
        value = config.get(key, fallback)
        return int(value)
    except (TypeError, ValueError):
        return fallback


def _session_int_or_default(key: str, default: int) -> int:
    value = st.session_state.get(key)
    if value is None:
        return int(default)
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default)

# Get backend config for embedding model (same as chatbot)
embedding_model_name = app_config_data.get('default_embedding_model')
llm_model_name = app_config_data.get('default_llm_model')

qa_min_value = _get_int_config(app_config_data, "course_generator_qa_count_min", 1)
quiz_question_min_value = _get_int_config(app_config_data, "course_generator_quiz_question_count_min", 1)
quiz_option_min_value = _get_int_config(app_config_data, "course_generator_quiz_option_count_min", 2)
misconception_min_value = _get_int_config(app_config_data, "course_generator_misconception_count_min", 1)

qa_max_value = max(
    qa_min_value,
    _get_int_config(app_config_data, "course_generator_qa_count_max", 10),
)
quiz_question_max_value = max(
    quiz_question_min_value,
    _get_int_config(app_config_data, "course_generator_quiz_question_count_max", 4),
)
quiz_option_max_value = max(
    quiz_option_min_value,
    _get_int_config(app_config_data, "course_generator_quiz_option_count_max", 4),
)
misconception_max_value = max(
    misconception_min_value,
    _get_int_config(app_config_data, "course_generator_misconception_count_max", 4),
)

qa_default_value = _get_int_config(app_config_data, "course_generator_qa_count_default", 5)
qa_default_value = min(max(qa_default_value, qa_min_value), qa_max_value)

quiz_question_default_value = _get_int_config(
    app_config_data,
    "course_generator_quiz_question_count_default",
    3,
)
quiz_question_default_value = min(
    max(quiz_question_default_value, quiz_question_min_value),
    quiz_question_max_value,
)

quiz_option_default_value = _get_int_config(
    app_config_data,
    "course_generator_quiz_option_count_default",
    3,
)
quiz_option_default_value = min(
    max(quiz_option_default_value, quiz_option_min_value),
    quiz_option_max_value,
)

misconception_default_value = _get_int_config(
    app_config_data,
    "course_generator_misconception_count_default",
    2,
)
misconception_default_value = min(
    max(misconception_default_value, misconception_min_value),
    misconception_max_value,
)

current_file_name = (uploaded_file.name if uploaded_file is not None else "")
current_is_pdf = current_file_name.lower().endswith('.pdf')
show_pdf_options = current_is_pdf or (uploaded_file is None and last_upload_is_pdf() and st.session_state.questions is not None)

qa_count = _session_int_or_default("last_upload_qa_count", qa_default_value)
quiz_question_count = _session_int_or_default(
    "last_upload_quiz_question_count",
    quiz_question_default_value,
)
quiz_option_count = _session_int_or_default(
    "last_upload_quiz_option_count",
    quiz_option_default_value,
)
misconception_count = _session_int_or_default(
    "last_upload_misconception_count",
    misconception_default_value,
)

qa_count = min(max(qa_count, qa_min_value), qa_max_value)
quiz_question_count = min(max(quiz_question_count, quiz_question_min_value), quiz_question_max_value)
quiz_option_count = min(max(quiz_option_count, quiz_option_min_value), quiz_option_max_value)
misconception_count = min(max(misconception_count, misconception_min_value), misconception_max_value)

if show_pdf_options:
    conf_col_qa, conf_col_q, conf_col_o, conf_col_m = st.columns(4)
    qa_count = int(conf_col_qa.number_input(
        translate("courseGenerator.upload.pdfOptions.qaCountLabel"),
        min_value=qa_min_value,
        max_value=qa_max_value,
        value=qa_count,
        step=1,
        key="pdf_upload_qa_count",
    ))
    quiz_question_count = int(conf_col_q.number_input(
        translate("courseGenerator.upload.pdfOptions.quizQuestionCountLabel"),
        min_value=quiz_question_min_value,
        max_value=quiz_question_max_value,
        value=quiz_question_count,
        step=1,
        key="pdf_upload_quiz_question_count",
    ))
    quiz_option_count = int(conf_col_o.number_input(
        translate("courseGenerator.upload.pdfOptions.quizOptionCountLabel"),
        min_value=quiz_option_min_value,
        max_value=quiz_option_max_value,
        value=quiz_option_count,
        step=1,
        key="pdf_upload_quiz_option_count",
    ))
    misconception_count = int(conf_col_m.number_input(
        translate("courseGenerator.upload.pdfOptions.misconceptionCountLabel"),
        min_value=misconception_min_value,
        max_value=misconception_max_value,
        value=misconception_count,
        step=1,
        key="pdf_upload_misconception_count",
    ))
    st.caption(
        translate(
            "courseGenerator.upload.pdfOptions.caption",
            qa_max=qa_max_value,
            quiz_question_max=quiz_question_max_value,
            quiz_option_max=quiz_option_max_value,
            misconception_max=misconception_max_value,
        )
    )

    st.session_state.last_upload_qa_count = qa_count
    st.session_state.last_upload_quiz_question_count = quiz_question_count
    st.session_state.last_upload_quiz_option_count = quiz_option_count
    st.session_state.last_upload_misconception_count = misconception_count

process_clicked = st.button(
    translate("courseGenerator.upload.processButton.label"),
    type="primary",
    help=translate("courseGenerator.upload.processButton.help"),
    disabled=uploaded_file is None or pdf_upload_job_is_active(),
)

if process_clicked and uploaded_file is not None:
    try:
        if not embedding_model_name or not llm_model_name:
            raise ValueError(translate("courseGenerator.errors.missingModelConfig"))

        embedding_model = embedding_model_name
        llm_model = llm_model_name

        name_lower = uploaded_file.name.lower()
        if name_lower.endswith('.pdf'):
            mime = "application/pdf"
        elif name_lower.endswith('.md') or name_lower.endswith('.markdown'):
            mime = "text/markdown"
        else:
            mime = "application/octet-stream"

        clear_generated_course_preview_state()

        file_bytes = uploaded_file.getvalue()
        st.session_state.last_upload_bytes = file_bytes
        st.session_state.last_upload_name = uploaded_file.name
        st.session_state.last_upload_mime = mime
        st.session_state.last_upload_embedding = embedding_model
        st.session_state.last_upload_llm = llm_model
        st.session_state.last_upload_qa_count = int(qa_count)
        st.session_state.last_upload_quiz_question_count = int(quiz_question_count)
        st.session_state.last_upload_quiz_option_count = int(quiz_option_count)
        st.session_state.last_upload_misconception_count = int(misconception_count)

        if name_lower.endswith('.pdf'):
            clear_pdf_upload_job_state()
            response = start_pdf_course_upload_job(
                BACKEND_API_URL,
                auth_headers(token),
                uploaded_file.name,
                file_bytes,
                mime,
                embedding_model,
                llm_model,
                qa_count=int(qa_count),
                quiz_question_count=int(quiz_question_count),
                quiz_option_count=int(quiz_option_count),
                misconception_count=int(misconception_count),
            )
            try:
                data = response.json()
            except Exception:
                data = {}

            if response.status_code != 202:
                st.error(
                    data.get(
                        "detail",
                        translate("courseGenerator.status.error", error=response.status_code),
                    )
                )
            else:
                st.session_state.pdf_upload_job_id = data.get("job_id")
                st.session_state.pdf_upload_job_status = data.get("status")
                st.session_state.pdf_upload_job_progress = float(data.get("progress") or 0.0)
                st.session_state.pdf_upload_job_message = data.get("message")
                st.session_state.pdf_upload_job_stage_key = data.get("stage_key")
                st.session_state.save_course_clicked = False
                st.session_state.course_saved_for_upload = False
                st.session_state.course_saved_filename = uploaded_file.name
                st.rerun()
        else:
            with st.spinner(translate("courseGenerator.upload.spinners.processing")):
                response = send_course_upload_request(
                    BACKEND_API_URL,
                    auth_headers(token),
                    uploaded_file.name,
                    file_bytes,
                    mime,
                    embedding_model,
                    llm_model,
                    qa_count=int(qa_count),
                    quiz_question_count=int(quiz_question_count),
                    quiz_option_count=int(quiz_option_count),
                    misconception_count=int(misconception_count),
                    replace_existing=False,
                )

            handle_course_upload_response(response)
            st.session_state.save_course_clicked = False
            st.session_state.course_saved_for_upload = False
            st.session_state.course_saved_filename = uploaded_file.name
    except Exception as e:
        st.error(translate("courseGenerator.errors.processingError", error=str(e)))

if st.session_state.get("pdf_upload_job_id"):
    render_pdf_upload_job_progress()

editor_validation_errors = []

if st.session_state.editable_course_json:

    edited_course_json, editor_validation_errors, synced_questions_dict = render_instructor_course_editor(
        st.session_state.editable_course_json,
        state_prefix="course_creation_editor",
        request_headers=headers,
    )
    
    st.session_state.editable_course_json = edited_course_json
    st.session_state.questions = synced_questions_dict
    
    total_questions = len((st.session_state.questions or {}).get("qa_list", []))
    page_size = st.session_state.get("qa_page_size", 5)
    max_page = max(1, (total_questions + page_size - 1) // page_size)
    st.session_state.qa_page = min(st.session_state.get("qa_page", 1), max_page)

if st.session_state.questions is not None:
    try:
        questions_data = (st.session_state.questions or {}).get("qa_list", [])
        
        render_generated_qa_table(
            questions_data=questions_data,
            default_reasoning_model=default_reasoning_model,
            app_config_data=app_config_data,
        )
    except Exception as e:
        st.error(translate("courseGenerator.errors.questionsLoadFailed", error=e))

    st.markdown("---")
    st.header(translate("courseGenerator.save.header"))
    st.markdown("---")

    current_course_json = st.session_state.editable_course_json or st.session_state.course_json or {}
    default_course_title = ((current_course_json.get("course") or {}).get("title") or "").strip()

    course_title = st.text_input(
        translate("courseGenerator.save.titleLabel"),
        value=default_course_title,
    )

    save_disabled = st.session_state.save_course_clicked or bool(editor_validation_errors)

    if editor_validation_errors:
        st.info(translate("courseGenerator.pagination.editor_validation_errors"))

    save_btn = st.button(
        translate("courseGenerator.save.saveButton.label"),
        disabled=save_disabled,
        type="primary",
        help=translate("courseGenerator.save.saveButton.help"),
    )

    if save_btn:
        if st.session_state.course_saved_for_upload:
            st.warning(translate("courseGenerator.save.messages.alreadySaved"))
        elif not st.session_state.save_course_clicked:
            st.session_state.save_course_clicked = True
            try:
                if current_course_json:
                    built = build_save_payload_from_course_json(
                        current_course_json,
                        title_override=course_title,
                    )

                    st.session_state.summary = built["summary"]
                    st.session_state.template_markdown = built["template_markdown"]
                    st.session_state.course_json = built["course_json"]
                    st.session_state.questions = built["questions_dict"]
                    st.session_state.quiz = built["quiz"]

                    payload = {
                        "title": built["title"],
                        "summary": built["summary"],
                        "questions": json.dumps(built["questions"], ensure_ascii=False),
                        "template_markdown": built["template_markdown"],
                        "course_json": json.dumps(built["course_json"], ensure_ascii=False),
                        "quiz": built["quiz"],
                    }
                else:
                    questions_data = (st.session_state.questions or {}).get("qa_list", [])
                    payload = {
                        "title": course_title,
                        "summary": st.session_state.summary or "",
                        "questions": json.dumps(
                            [
                                {"text": q.get("question", ""), "answer_text": q.get("answer", "")}
                                for q in questions_data
                            ],
                            ensure_ascii=False,
                        ),
                        "template_markdown": st.session_state.template_markdown or "",
                        "course_json": json.dumps(st.session_state.course_json or {}, ensure_ascii=False),
                        "quiz": st.session_state.quiz or "",
                    }

                response = requests.post(
                    f"{BACKEND_API_URL}/api/course/create_course_with_summary_and_qas",
                    headers=auth_headers(token),
                    data=payload,
                )

                if response.status_code == 200:
                    st.session_state.course_saved_for_upload = True
                    st.success(translate("courseGenerator.save.messages.savedSuccess"))
                else:
                    try:
                        detail = response.json().get("detail")
                    except Exception:
                        detail = response.text
                    st.error(detail or translate("courseGenerator.save.messages.saveFailed"))
            except Exception as e:
                st.error(translate("courseGenerator.status.error", error=e))
            finally:
                st.session_state.save_course_clicked = False

if st.session_state.markdown_replace_prompt:
    confirm_replace_dialog()
