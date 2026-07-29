# 🤝 Contributing to KIKO

Thank you for your interest in contributing to KIKO.

KIKO is an AI-powered knowledge and learning platform for nuclear decommissioning. The project combines a Streamlit frontend, FastAPI backend, PostgreSQL/pgvector, Docker, Ollama, and optional Hugging Face model integrations.

The current stable frontend is Streamlit. A ReactJS migration is under active development and is not yet the default public frontend.

## 📑 Table of contents

- [Development workflow](#development-workflow)
- [Branch naming](#branch-naming)
- [Commit style](#commit-style)
- [Pull request checklist](#pull-request-checklist)
- [Backend contribution guide](#backend-contribution-guide)
- [Frontend contribution guide](#frontend-contribution-guide)
- [ReactJS migration work](#reactjs-migration-work)
- [Testing](#testing)
- [Code style](#code-style)
- [Documentation changes](#documentation-changes)
- [Security](#security)
- [Review expectations](#review-expectations)

## 🛠️ Development workflow

1. Fork or clone the repository.

   ```bash
   git clone https://github.com/DataScienceLabFHSWF/KIKO-release.git
   ```

   ```bash
   cd KIKO-release
   ```

2. Create a local environment file.

   ```bash
   cp .env.example .env
   ```

3. Start the stack.

   ```bash
   docker compose --project-name <YOUR_PROJECT_NAME> up --build
   ```

4. Create a feature branch.

   ```bash
   git checkout -b feature/short-description
   ```

5. Make a focused change.

6. Run tests and basic checks.

7. Open a pull request against `main`.

## 🔀 Branch naming

Use short, descriptive branch names.

Recommended format:

```text
feature/<short-description>
fix/<short-description>
docs/<short-description>
chore/<short-description>
refactor/<short-description>
test/<short-description>
```

Examples:

```text
feature/course-progress-api
fix/chat-history-pagination
docs/update-quickstart
chore/add-pages-workflow
```

Use `feature/` for new functionality, `fix/` for bug fixes, `docs/` for documentation-only changes, and `chore/` for maintenance work.

## ✍️ Commit style

Use clear imperative commit messages.

Good examples:

```text
Add course progress endpoint
Fix document upload validation
Update Docker quickstart
Refactor chat service error handling
```

Avoid vague commits such as:

```text
changes
fix stuff
update
final
```

For larger changes, prefer multiple small commits over one large unclear commit.

## 📋 Pull request checklist

Before opening a pull request, check:

- [ ] The change is focused and easy to review.
- [ ] The PR title clearly describes the change.
- [ ] The PR description explains what changed and why.
- [ ] No `.env` file or secrets are committed.
- [ ] No private documents, uploaded files, logs, database dumps, or model caches are committed.
- [ ] Documentation is updated if behavior changed.
- [ ] Tests are added or updated where appropriate.
- [ ] Relevant tests pass locally.
- [ ] Docker Compose still starts successfully if deployment behavior changed.
- [ ] Screenshots are included for visible UI changes.
- [ ] Breaking changes are clearly documented.

## ⚙️ Backend contribution guide

Backend code lives in `backend/`.

Typical backend change flow:

1. Add or update the API route in:

   ```text
   backend/app/api/routes/
   ```

2. Add service logic in:

   ```text
   backend/app/services/
   ```

3. Add or update data schemas in:

   ```text
   backend/app/schemas/
   ```

4. Add or update ORM models in:

   ```text
   backend/app/models/
   ```

5. Register new routes where required.

6. Add or update tests in:

   ```text
   tests/backend/
   ```

Backend principles:

- Keep route handlers thin.
- Keep business logic in services.
- Validate input explicitly.
- Use clear response models.
- Use consistent error handling.
- Keep role checks explicit.
- Avoid hardcoded paths, hostnames, credentials, and model names where configuration is more appropriate.
- Do not expose raw internal errors to end users.
- Prefer structured logging over `print()` in production paths.

## 🖥️ Frontend contribution guide

The current stable frontend is Streamlit and lives in:

```text
frontend/
```

When adding Streamlit pages:

1. Add pages under:

   ```text
   frontend/pages/
   ```

2. Reuse existing sidebar/session utilities.

3. Respect role-based visibility.

4. Keep UI text clear and concise.

Frontend principles:

- Keep pages readable and modular.
- Avoid large files with mixed concerns.
- Keep role-specific behavior explicit.
- Prefer shared helper functions for repeated API calls.
- Keep user-facing text consistent.
- Do not show internal stack traces or raw backend errors to users.

The ReactJS frontend migration is under active development and is not yet the default public frontend. React changes should stay focused, documented, and clearly marked as migration work.

## 🧪 Testing

Run backend tests with:

```bash
docker compose exec kiko-backend-service pytest tests/backend/
```

For local backend-only testing, use the backend environment documented in the backend setup notes.

Testing expectations:

- Bug fixes should include a regression test where practical.
- New API routes should include at least one success-path test and one failure-path test.
- Role-protected features should test unauthorized or forbidden access.
- Model-dependent behavior should be tested with mocks where possible.
- Avoid tests that require large model downloads unless clearly marked as integration tests.

## 🧹 Code style

General rules:

- Prefer simple code over clever code.
- Use descriptive names.
- Keep functions small.
- Keep modules focused.
- Avoid hidden global state.
- Avoid committing generated files.
- Avoid committing local caches, logs, volumes, and temporary files.
- Keep configuration in environment variables.
- Document non-obvious decisions.

Python/backend:

- Use type hints where useful.
- Keep API schemas explicit.
- Keep async code consistent.
- Avoid blocking calls in async routes.
- Prefer dependency injection for database sessions and authenticated users.
- Use clear exceptions and error messages.
- Keep database access inside service/repository layers where possible.

Frontend:

- Keep components small.
- Keep user-facing text clear.
- Reuse shared UI patterns.
- Keep API calls centralized.
- Keep role-based UI logic explicit.
- Avoid duplicating state management logic.

Docker/configuration:

- Keep `.env` local.
- Keep `.env.example` safe and complete.
- Do not hardcode machine-specific GPU UUIDs in public defaults.
- Do not expose database or model runtime ports publicly unless explicitly needed for development.
- Prefer documented override files for local or GPU-specific settings.

## 📝 Documentation changes

Documentation should be simple, direct, and easy to navigate.

Use the README as the front door only. Detailed guides should live in:

```text
docs/
docs/development/
docs/deployment/
```

Recommended documentation locations:

```text
docs/architecture.md              Architecture overview
docs/models.md                    Model configuration and usage
docs/development/database.md      Database development notes
docs/development/notebooks.md     Notebook setup
docs/deployment/ngrok.md          Optional demo tunneling
docs/development/react-status.md  React migration status
```

Update documentation when:

- setup steps change
- environment variables change
- API behavior changes
- ports or Docker services change
- model names or providers change
- user workflows change
- security-relevant behavior changes

Avoid putting long operational guides directly in the README.

## 🛡️ Security

Never commit:

- `.env`
- API tokens
- Hugging Face tokens
- ngrok tokens
- database passwords
- JWT secrets
- private documents
- uploaded user files
- database dumps
- logs containing user data
- local model caches
- internal server IPs or credentials

Use safe placeholders in `.env.example`.

Bad:

```env
SECRET_KEY=supersecretkey
POSTGRES_PASSWORD=kiko
HUGGINGFACE_HUB_TOKEN=hf_real_token
```

Good:

```env
SECRET_KEY=change-me
POSTGRES_PASSWORD=change-me
HUGGINGFACE_HUB_TOKEN=
```

If you accidentally commit a secret:

1. Rotate the secret immediately.
2. Remove it from the repository.
3. Notify a maintainer.
4. Do not rely only on deleting it in a later commit if it was already pushed.

Security issues should not be reported in public issues. Follow the process in `SECURITY.md`.

## 👀 Review expectations

Maintainers review pull requests for correctness, maintainability, security, and clarity.

A maintainer may ask you to:

- reduce the scope of a PR
- add tests
- update documentation
- simplify implementation
- improve naming
- avoid committing generated files
- split one large PR into smaller PRs

This is normal. The goal is to keep KIKO stable, understandable, and easy to contribute to.

## 💬 Questions

For questions, open a GitHub issue or discussion if enabled.

For security concerns, use the process in `SECURITY.md`.
