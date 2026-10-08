# Role-to-route matrix

| Role | React routes | Access rule |
|---|---|---|
| Public | `/login`, `/register` | No JWT required |
| Shared authenticated | `/chat`, `/documents`, `/profile`, `/settings`, `/logout`, `/evaluation-results`,  `/faq` | JWT required; roles: Learner, Instructor, Admin |
| Learner | `/learner/dashboard`, `/learner/my-courses`, `/learner/courses/:courseId`, `/learner/knowledge-assessment` | JWT required; role: Learner |
| Instructor | `/instructor/dashboard`, `/instructor/courses`, `/instructor/courses/create`, `/instructor/courses/:courseId/edit`, `/instructor/media-manager` | JWT required; role: Instructor |
| Admin | `/admin/dashboard`, `/admin/panel`, `/admin/knowledge-config` | JWT required; role: Admin |