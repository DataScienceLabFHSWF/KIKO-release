# API endpoint matrix

| Endpoint | Used by React route | Current risk | Required response model |
|---|---|---|---|
| `POST /api/authentication/login` | `/login` | Must confirm token shape | `LoginResponse` |
| `POST /api/authentication/register` | `/register` | Needs default-course provisioning report | `RegisterResponse` |
| `GET /api/app_configurations/app_config` | many pages | Loose schema | `AppConfigResponse` |
| `POST /api/chatbot/query` | `/chat` | Loose schema | `ChatQueryResponse` |
| `GET /api/chatbot/chat/history` | `/chat` | Loose schema | `ChatHistoryResponse` |
| `GET /api/learner/statistics` | `/learner/dashboard` | Already typed if OpenAPI shows `LearnerStatistics` | keep |
| `GET /api/learner/courses/enrolled` | `/learner/my-courses` | `List[Dict]` | `list[LearnerCourseSummary]` |
| `GET /api/learner/courses/recommended` | `/learner/my-courses` | `List[Dict]` | `list[RecommendedCourseSummary]` |
| `GET /api/learner/courses/all` | `/learner/my-courses` | `List[Dict]` | `list[CourseSummary]` |
| `GET /api/learner/courses/:courseId` | `/learner/courses/:courseId` | Loose schema | `LearnerCourseDetailsResponse` |
| `PUT /api/learner/courses/:courseId/progress` | course renderer | Must confirm shape | `ProgressSaveResponse` |
| `POST /api/learner/courses/:courseId/module-quizzes/:moduleId/submit` | course renderer | Must confirm shape | `QuizSubmitResponse` |
| `POST /api/learner/courses/:courseId/final-quiz/submit` | course renderer | Must confirm shape | `QuizSubmitResponse` |
| `GET /api/course/my_courses` | `/instructor/courses`, `/instructor/media-manager` | Loose schema | `list[InstructorCourseSummary]` |
| `POST /api/course/upload_course_document` | `/instructor/courses/create` | Loose schema | `CourseUploadResponse` |
| `GET /api/course/:courseId` | instructor course details/editor | Loose schema | `InstructorCourseDetailsResponse` |
| `GET /api/course/:courseId/images` | `/instructor/media-manager` | Loose schema | `list[CourseImageResponse]` |