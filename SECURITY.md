# 🛡️ Security Policy

## 🧩 Supported versions

Security fixes are applied to the current `main` branch.

| Version / branch | Supported |
| ---------------- | --------- |
| `main`           | Yes       |
| Feature branches | No        |

## 🔐 Reporting a vulnerability

Please do not report security vulnerabilities through public GitHub issues.

Instead, contact the maintainers privately through the project maintainers listed in the repository README.

When reporting a vulnerability, include:

- a short description of the issue
- affected component, if known
- steps to reproduce, if possible
- potential impact
- suggested fix, if available

We will acknowledge valid reports as soon as possible and coordinate a fix before public disclosure.

## 🔑 Secrets and credentials

Never commit:

- `.env` files
- Hugging Face tokens
- ngrok tokens
- database passwords
- JWT secrets
- private documents
- uploaded user files
- logs containing user data

Use `.env.example` for safe placeholders only.

## ⚠️ Deployment warning

Do not expose PostgreSQL or Ollama directly to the public internet. Only the frontend and, where necessary, the backend API should be reachable externally.
