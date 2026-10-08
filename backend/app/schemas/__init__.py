# backend/app/schemas/__init__.py
from .authentication_schema import (
    UserLoginRequest, UserLoginResponse, UserRegisterRequest, UserRegisterResponse,
    GenericSuccessResponse, ForgotPasswordRequest, ResetPasswordRequest, ChangePasswordRequest,
    ChangePasswordResponse, VerifyEmailRequest, ResendVerificationEmailRequest
)
from .document_schema import (
    DocumentResponse, DocumentProcessingFileResponse, DocumentProcessingSummaryResponse, 
    ProcessUploadedDocsResponse, BatchProcessingDataResponse, BatchProcessingResponse,
    DeleteDocumentsResponse
)
from .user_schema import UserProfileResponse, UserProfileUpdateRequest
from .learner_schema import (
    LearnerStatistics, LearnerSubmitQuizRequest, LearnerProgressUpdateRequest,
    LearnerDashboardResponse, LearnerCourseSummaryResponse, LearnerRecommendedCourseResponse,
    LearnerAvailableCourseResponse, LearnerCourseProgressResponse, LearnerCourseDetailsResponse,
    LearnerGradedAnswerResponse, LearnerQuizSubmitResponse, LearnerProgressSaveResponse,
)
from .instructor_schema import (
    InstructorStatistics, InstructorDashboardResponse, InstructorLearnerQueryResponse, 
    InstructorRecentQueriesResponse
)
from .chat_assistant_schema import (
    ChatQueryRequest, ChatAnswerResponse, ChatHistoryResponse, 
    ChatMessageResponse, ChatQueryResponse
)
from .app_config_schema import AppConfigSchema, AppConfigResponse
from .qa_structure_schema import QuestionAnswer, QuestionAnswerList
from .grade_schema import AnswerGradingRequest, AnswerGradingResponse
from .knowledge_assessment_schema import (
    AssessmentQuestion, AssessmentPayload, AssessmentResult,
    RecommendedCourse, AssessmentAdminQuestionResponse, AssessmentConfigResponse, 
    AssessmentConfigUpdateRequest, AssessmentGradedAnswerResponse
)
from .course_schema import (
    CourseUpdateRequest, ExistingDocumentResponse, CourseUploadResponse, 
    InstructorCourseSummary, InstructorCourseDetailsResponse, CourseUpdateResponse,
    CourseImageResponse, CourseImageUploadResponse,
    CourseCreateResponse, CourseUploadJobResponse, CourseUploadPdfJobRequest
)
from .file_schema import MarkdownPreviewResponse
from .common import (
    ApiError, ApiErrorResponse, COMMON_ERROR_RESPONSES,
    HealthCheckResponse
)
from .admin_schema import (
    AdminDashboardResponse, AdminStatsResponse, AdminUploadLogResponse,
    AdminUploadLogsResponse
)
from .app_config_schema import (
    AppConfigSchema,
    AppConfigResponse,
    AppConfigUpdateRequest,
    AppConfigUpdateResponse,
    AdminEditableAppConfigSchema
)

__all__ = [
    "UserLoginResponse",
    "UserLoginRequest",
    "UserProfileResponse",
    "LearnerStatistics",
    "InstructorStatistics",
    "AppConfigSchema",
    "QuestionAnswer",
    "QuestionAnswerList",
    "AnswerGradingRequest",
    "UserRegisterRequest",
    "ChatQueryRequest",
    "DocumentResponse",
    "AssessmentQuestion",
    "AssessmentPayload",
    "AssessmentResult",
    "AnswerGradingResponse",
    "LearnerSubmitQuizRequest",
    "LearnerProgressUpdateRequest",
    "CourseUpdateRequest",
    "ApiError",
    "ApiErrorResponse",
    "COMMON_ERROR_RESPONSES",
    "UserRegisterResponse",
    "AppConfigResponse",
    "ChatAnswerResponse",
    "ChatHistoryResponse",
    "ChatMessageResponse",
    "ChatQueryResponse",
    "LearnerDashboardResponse",
    "LearnerCourseSummaryResponse",
    "LearnerRecommendedCourseResponse",
    "LearnerAvailableCourseResponse",
    "LearnerCourseProgressResponse",
    "LearnerCourseDetailsResponse",
    "LearnerGradedAnswerResponse",
    "LearnerQuizSubmitResponse",
    "LearnerProgressSaveResponse",
    "ExistingDocumentResponse",
    "CourseUploadResponse",
    "CourseQuestionResponse",
    "InstructorCourseSummary",
    "InstructorCourseDetailsResponse",
    "CourseCreateResponse",
    "CourseUpdateResponse",
    "CourseImageResponse",
    "CourseImageUploadResponse",
    "DocumentProcessingFileResponse",
    "DocumentProcessingSummaryResponse",
    "ProcessUploadedDocsResponse",
    "BatchProcessingDataResponse",
    "BatchProcessingResponse",
    "DeleteDocumentsResponse",
    "MarkdownPreviewResponse",
    "InstructorDashboardResponse",
    "InstructorLearnerQueryResponse",
    "InstructorRecentQueriesResponse",
    "AssessmentAdminQuestionResponse",
    "AssessmentConfigResponse",
    "AssessmentConfigUpdateRequest",
    "RecommendedCourse",
    "AdminDashboardResponse",
    "AdminStatsResponse",
    "AdminUploadLogResponse",
    "AdminUploadLogsResponse",
    "HealthCheckResponse",
    "UserProfileUpdateRequest",
    "CourseUploadJobResponse",
    "CourseUploadPdfJobRequest",
    "AssessmentGradedAnswerResponse",
    "AppConfigUpdateRequest",
    "AppConfigUpdateResponse",
    "AdminEditableAppConfigSchema",
    "GenericSuccessResponse",
    "ForgotPasswordRequest",
    "ResetPasswordRequest",
    "ChangePasswordRequest",
    "ChangePasswordResponse",
    "VerifyEmailRequest",
    "ResendVerificationEmailRequest",
]
