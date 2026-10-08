# 🛡️ Security Policy

## 🧩 Supported versions

Security fixes are normally applied to the latest supported release and the
current `main` branch.

| Version              | Supported                   |
| -------------------- | --------------------------- |
| Latest `1.x` release | ✅                          |
| `main`               | ✅ Development              |
| Older releases       | ❌ unless explicitly stated |

## 🔐 Reporting a vulnerability

Please do not report security vulnerabilities through public GitHub issues.

Use GitHub's **Private Vulnerability Reporting** feature for this repository
whenever possible.

Include:

- a clear description of the vulnerability;
- the affected component or version;
- steps to reproduce;
- potential impact;
- proof-of-concept information where appropriate;
- suggested remediation, if known.

Maintainers will review the report and coordinate remediation and disclosure.

## 🔑 Secrets and credentials

- Never commit passwords, tokens, API keys, private documents, or production configuration.
- Keep `.env.stage`, and `.env.production` outside version control.
- Use different secrets for development, staging, and production.
- Do not expose PostgreSQL or Ollama directly to the public internet.
- Use HTTPS for public deployments.
- Do not enable destructive database initialization in staging or production.
- Report vulnerabilities according to [`SECURITY.md`](SECURITY.md).

## ⚠️ Deployment warning

Do not expose PostgreSQL or Ollama directly to the public internet. Only the frontend and, where necessary, the backend API should be reachable externally.
