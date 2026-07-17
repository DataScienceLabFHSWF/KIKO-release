from .user_service import (
    get_user_profile_by_email, update_user_profile_by_email, check_for_duplicates, 
    create_user, get_system_user_id
)
from .learner_service import (
    get_learner_statistics, list_enrolled_courses, list_recommended_courses,
    enroll_user_in_course, unenroll_user_from_course, dismiss_recommendation,
    fetch_course_details, list_all_courses_excluding_enrolled, require_active_course_enrollment
)
from .instructor_service import get_instructor_statistics
from .security_service import require_role, create_access_token, get_request_lang
from .documents_service import (
    process_pdf, process_markdown, get_doc_by_hash_name, 
    process_folder_with_embeddings, list_user_documents, delete_user_document,
    delete_all_user_documents, parse_structured_markdown, get_existing_doc_by_source_id,
    get_doc_by_derivation, save_doc_to_db,
    MarkdownStructureError
)
from .configuration_service import get_app_config_and_libary_available
from .embedding_service import (
    store_embeddings_to_db, get_embeddings_from_db,
    generate_document_embeddings, generate_query_embedding 
)
from .vector_store_service import similarity_search
from .chatbot_service import run_query, save_chat_turn, fetch_chat_history, clear_chat_history
from .course_creator_manager import (
    AsyncBatchProcessor,
    create_course_with_summary_and_qas_for_instructor,
    list_courses_for_instructor,
    get_course_detail_for_instructor,
    update_course_for_instructor,
    delete_course_for_instructor,
)
from .answer_grading_service import grade_user_answer
from .assessment_service import (
    get_assessment_quiz_for_user, submit_assessment_quiz_for_user, list_all_questions,
    fetch_config, update_config, remove_question
)
from .course_service import (
    list_user_courses, get_course_detail_by_id, update_course_by_id,
    delete_course_by_id
)
from .course_image_service import (
    upload_course_image, list_course_images, get_course_image_path,
    delete_course_image, delete_all_course_images
)
from .course_template_manager import create_template_courses_for_instructor
from .course_markdown_parser_service import parse_course_markdown, CourseMarkdownStructureError
from .learner_course_progress_service import (
    submit_module_quiz_attempt_for_learner, update_progress_snapshot, submit_final_quiz_attempt_for_learner
)

__all__ = [
    "require_role",
    "create_access_token",
    "get_user_profile_by_email",
    "update_user_profile_by_email",
    "get_learner_statistics",
    "get_instructor_statistics",
    "process_pdf",
    "process_markdown",
    "get_doc_by_hash_name",
    "get_app_config_and_libary_available",
    "store_embeddings_to_db",
    "get_embeddings_from_db",
    "similarity_search",
    "run_query",
    "AsyncBatchProcessor",
    "create_course_with_summary_and_qas_for_instructor",
    "list_courses_for_instructor",
    "get_course_detail_for_instructor",
    "update_course_for_instructor",
    "delete_course_for_instructor",
    "process_folder_with_embeddings",
    "grade_user_answer",
    "check_for_duplicates",
    "create_user",
    "save_chat_turn",
    "fetch_chat_history",
    "list_user_documents",
    "delete_user_document",
    "delete_all_user_documents",
    "clear_chat_history",
    "get_assessment_quiz_for_user",
    "submit_assessment_quiz_for_user",
    "list_enrolled_courses",
    "list_recommended_courses",
    "enroll_user_in_course",
    "unenroll_user_from_course",
    "dismiss_recommendation",
    "fetch_course_details",
    "list_all_courses_excluding_enrolled",
    "list_all_questions",
    "fetch_config",
    "update_config",
    "remove_question",
    "list_user_courses",
    "get_course_detail_by_id",
    "update_course_by_id",
    "delete_course_by_id",
    "upload_course_image",
    "list_course_images",
    "get_course_image_path",
    "delete_course_image",
    "delete_all_course_images",
    "parse_structured_markdown",
    "get_existing_doc_by_source_id",
    "get_doc_by_derivation",
    "save_doc_to_db",
    "MarkdownStructureError",
    "get_request_lang",
    "create_template_courses_for_instructor",
    "get_system_user_id",
    "process_uploaded_docs",
    "delete_embeddings_for_doc_model",
    "upload_course_docs",
    "parse_course_markdown",
    "CourseMarkdownStructureError",
    "submit_module_quiz_attempt_for_learner",
    "update_progress_snapshot",
    "submit_final_quiz_attempt_for_learner",
    "require_active_course_enrollment",
    "generate_document_embeddings",
    "generate_query_embedding",  
]