# Page-to-route matrix

| Streamlit file | React route | Role | Main React components | Required states |
|---|---|---|---|---|
| `login.py` | `/login` | Public | `LoginPage`, `AuthForm` | loading, invalid credentials, network error |
| `register.py` | `/register` | Public | `RegisterPage`, `RegisterForm` | loading, validation error, default-course provisioning result |
| `faq.py` | `/faq` | Authenticated | `FaqPage`, `FaqList` | empty FAQ, loading, error |
| `chatbot.py` | `/chat` | Authenticated | `ChatPage`, `ChatInput`, `MessageList`, `SourcePanel`, `ModelSelector` | empty history, loading answer, no context, API error |
| `learner_dashboard.py` | `/learner/dashboard` | Learner | `LearnerDashboardPage`, `StatsCards` | loading, empty stats, error |
| `my_courses.py` | `/learner/my-courses` | Learner | `LearnerCoursesPage`, `CourseCard`, `ProgressBadge` | no enrolled courses, no recommendations, loading, error |
| `course_details.py` | `/learner/courses/:courseId` | Learner | `CourseDetailsPage`, `CourseRenderer`, `QuizPanel`, `ProgressTracker` | not enrolled, completed, loading, no course JSON, error |
| `knowledge_assessment.py` | `/learner/knowledge-assessment` | Learner | `KnowledgeAssessmentPage` | loading, no assessment, submitted, error |
| `instructor_dashboard.py` | `/instructor/dashboard` | Instructor | `InstructorDashboardPage`, `StatsCards` | loading, empty stats, error |
| `instructor_courses.py` | `/instructor/courses` | Instructor | `InstructorCoursesPage`, `CourseTable`, `CourseActions` | no courses, loading, error |
| `instructor_course_creation.py` | `/instructor/courses/create` | Instructor | `CourseCreationPage`, `UploadCourseForm`, `GeneratedCoursePreview` | uploading, processing, markdown exists, file exists, error |
| `instructor_course_editor.py` | `/instructor/courses/:courseId/edit` | Instructor | `CourseEditorPage`, `CourseEditor`, `QuizEditor`, `QuestionEditor` | loading, save success, validation error |
| `media_manager.py` | `/instructor/media-manager` | Instructor | `MediaManagerPage`, `ImageUploader`, `ImageGallery` | no courses, no images, upload error, delete confirmation |
| `my_documents.py` | `/documents` | Authenticated | `DocumentsPage`, `DocumentTable`, `UploadDocumentForm` | no documents, processing, failed processing, error |
| `profile.py` | `/profile` | Authenticated | `ProfilePage`, `ProfileForm` | loading, save success, validation error |
| `settings.py` | `/settings` | Authenticated | `SettingsPage`, `LanguageSelector`, `ModelSettings` | loading, save success, error |
| `evaluation_results.py` | `/evaluation-results` | Authenticated | `EvaluationResultsPage`, `ResultsTable` | no results, loading, error |
| `admin_dashboard.py` | `/admin/dashboard` | Admin | `AdminDashboardPage`, `StatsCards` | loading, empty stats, error |
| `admin_panel.py` | `/admin/panel` | Admin | `AdminPanelPage`, `UserManagementTable` | loading, no users, error |
| `admin_knowledge_config.py` | `/admin/knowledge-config` | Admin | `KnowledgeConfigPage`, `PromptConfigEditor`, `ModelConfigEditor` | loading, save success, validation error |
| `logout.py` | `/logout` | Authenticated | `LogoutPage` | token clear, redirect |
| `sidebar.py` | layout component | Authenticated | `AppSidebar` | collapsed, active route |