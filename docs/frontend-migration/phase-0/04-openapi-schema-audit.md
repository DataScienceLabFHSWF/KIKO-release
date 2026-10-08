# Missing backend schema list

## P0: must fix before React type generation

| Endpoint | Current OpenAPI problem | Required model |
|---|---|---|
| `GET /api/learner/courses/{course_id}` | `{}` / loose object | `LearnerCourseDetailsResponse` |
| `POST /api/chatbot/query` | `{}` / loose object | `ChatQueryResponse` |
| `GET /api/chatbot/chat/history` | `{}` / loose object | `ChatHistoryResponse` |
| `GET /api/course/my_courses` | `{}` or `List[Dict]` | `list[InstructorCourseSummary]` |
| `POST /api/course/upload_course_document` | `{}` / loose object | `CourseUploadResponse` |
| `GET /api/course/{course_id}` | `{}` / loose object | `InstructorCourseDetailsResponse` |
| `GET /api/course/{course_id}/images` | `{}` or loose list | `list[CourseImageResponse]` |
| `GET /api/app_configurations/app_config` | `{}` / loose object | `AppConfigResponse` |

## P1: fix after P0

| Endpoint group | Required cleanup |
|---|---|
| Admin dashboard/config APIs | Replace `Dict` responses with dashboard/config models |
| Document APIs | Add `DocumentSummary`, `DocumentUploadResponse`, `DocumentDeleteResponse` |
| Course editor APIs | Add explicit request/response schemas |
| Media/image APIs | Add explicit image metadata model |


# Shared API error format

## Use one response shape everywhere.
```
# backend/app/schemas/common.py
from pydantic import BaseModel, Field
from typing import Any

class ApiErrorResponse(BaseModel):
    error: str = Field(..., examples=["course_not_found"])
    message: str = Field(..., examples=["Course not found."])
    status_code: int = Field(..., examples=[404])
    details: dict[str, Any] | None = None
    request_id: str | None = None
```
## Standardize backend errors like this:
```
{
  "error": "course_not_found",
  "message": "Course not found.",
  "status_code": 404,
  "details": {
    "course_id": 12
  },
  "request_id": "optional-correlation-id"
}
```
## Avoid returning mixed formats such as:
```
{"detail": "something failed"}
```
or
```
{"message": "failed"}
```
