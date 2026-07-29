# ![KIKO Logo](./frontend/assets/images/KIKO-Logo.png)

KIKO is an AI-powered knowledge and learning platform for nuclear decommissioning. It combines document processing, retrieval-augmented generation (RAG), role-based learning workflows, and open-source language models to make expert knowledge easier to preserve, search, teach, and reuse.

<!-- Tech stack start -->
<p>
    <a href="https://www.python.org/" target="_blank" style="margin: 2px;">
        <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white&style=flat-square" alt="Python 3.10+" />
    </a>
    <a href="https://streamlit.io/" target="_blank" style="margin: 2px;">
        <img src="https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit&logoColor=white&style=flat-square" alt="Streamlit" />
    </a>
    <a href="https://fastapi.tiangolo.com/" target="_blank" style="margin: 2px;">
        <img src="https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white&style=flat-square" alt="FastAPI" />
    </a>
    <a href="https://www.postgresql.org/" target="_blank" style="margin: 2px;">
        <img src="https://img.shields.io/badge/PostgreSQL-336791?logo=postgresql&logoColor=white&style=flat-square" alt="PostgreSQL" />
    </a>
    <a href="https://github.com/pgvector/pgvector" target="_blank" style="margin: 2px;">
        <img src="https://img.shields.io/badge/pgvector-336791?logo=postgresql&logoColor=white&style=flat-square" alt="pgvector" />
    </a>
    <a href="https://ollama.com/" target="_blank" style="margin: 2px;">
        <img src="https://img.shields.io/badge/Ollama-000000?logo=ollama&logoColor=white&style=flat-square" alt="Ollama" />
    </a>
    <a href="https://www.langchain.com/" target="_blank" style="margin: 2px;">
        <img src="https://img.shields.io/badge/LangChain-7FC8FF?logo=langchain&logoColor=000000&style=flat-square" alt="LangChain" />
    </a>
    <a href="https://huggingface.co/" target="_blank" style="margin: 2px;">
        <img src="https://img.shields.io/badge/Hugging%20Face-FFD21E?logo=huggingface&logoColor=000000&style=flat-square" alt="Hugging Face" />
    </a>
    <a href="https://www.docker.com/" target="_blank" style="margin: 2px;">
        <img src="https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white&style=flat-square" alt="Docker" />
    </a>
    <a href="https://python-poetry.org/" target="_blank" style="margin: 2px;">
        <img src="https://img.shields.io/badge/Poetry-60A5FA?logo=poetry&logoColor=white&style=flat-square" alt="Poetry" />
    </a>
    <a href="https://developer.nvidia.com/cuda-zone" target="_blank" style="margin: 2px;">
        <img src="https://img.shields.io/badge/NVIDIA%20CUDA-76B900?logo=nvidia&logoColor=000000&style=flat-square" alt="NVIDIA CUDA" />
    </a>
</p>
<!-- Tech stack end -->

<!-- Models stack start -->
<p>
  <!-- Embeddings -->
  <a href="https://ollama.com/library/nomic-embed-text" target="_blank" style="margin: 2px;">
    <img src="https://img.shields.io/badge/Embeddings-nomic--embed--text%20v1.5-111827?style=flat-square" alt="nomic-embed-text:v1.5" />
  </a>
  <!-- VLM -->
  <a href="https://ollama.com/library/qwen2.5vl" target="_blank" style="margin: 2px;">
    <img src="https://img.shields.io/badge/VLM-Qwen2.5--VL%207B-FF6A00?logo=alibabacloud&logoColor=white&style=flat-square" alt="qwen2.5vl:7b" />
  </a>
  
  <!-- LLMs (generation) start -->
  <a href="https://ollama.com/library/llama3.3" target="_blank" style="margin: 2px;">
    <img src="https://img.shields.io/badge/LLM-Meta%20Llama%203.3%2070B-0467DF?logo=meta&logoColor=white&style=flat-square" alt="llama3.3:70b" />
  </a>
  <!-- <a href="https://ollama.com/library/gemma4" target="_blank" style="margin: 2px;">
    <img src="https://img.shields.io/badge/LLM-Google%20Gemma%204-4285F4?logo=google&logoColor=white&style=flat-square" alt="gemma4" />
  </a> -->
  <a href="https://ollama.com/library/nemotron" target="_blank" style="margin: 2px;">
    <img src="https://img.shields.io/badge/LLM-NVIDIA%20Nemotron%2070B-76B900?logo=nvidia&logoColor=000000&style=flat-square" alt="nemotron:70b" />
  </a>
  <!-- HF models -->
  <a href="https://huggingface.co/" target="_blank" style="margin: 2px;">
    <img src="https://img.shields.io/badge/HF-Apertus%208B%20%2F%2070B-FFD21E?logo=huggingface&logoColor=000000&style=flat-square" alt="Apertus (HF)" />
  </a>
  <!-- LLMs (generation) end -->
  
  <!-- LLMs (grading / inference) start -->
  <a href="https://ollama.com/library/deepseek-r1" target="_blank" style="margin: 2px;">
    <img src="https://img.shields.io/badge/Grader-DeepSeek%20R1%2070B-111827?style=flat-square" alt="deepseek-r1:70b" />
  </a>
  <a href="https://ollama.com/library/nemotron-3-super" target="_blank" style="margin: 2px;">
    <img src="https://img.shields.io/badge/Grader-Nemotron--3%20Super%20120B-76B900?logo=nvidia&logoColor=000000&style=flat-square" alt="nemotron-3-super:120b" />
  </a>
  <!-- LLMs (grading / inference) end -->
</p>
<!-- Models stack end -->

# 🌱 Why KIKO?

Nuclear decommissioning depends on specialized expert knowledge (Nuclear Engineering, Mechanical/Civil Engineering, and Health Physics) that is often distributed across documents, training material, and experienced practitioners. KIKO supports this knowledge lifecycle by helping users upload documents, retrieve relevant information, ask grounded questions, and support learning workflows for different roles.

# ✨ Features

- AI-assisted chat over uploaded documents.
- Retrieval-augmented generation using PostgreSQL and pgvector.
- FastAPI backend with role-based access control.
- Streamlit frontend for the current stable user interface.
- Ollama and Hugging Face model integration.
- Document processing with OCR/VLM support.
- Learner, instructor, and admin roles.
- Docker Compose deployment for local and server use.

# 🏗️ Architecture

```bash
User
  └── Streamlit Frontend
        └── FastAPI Backend
              ├── PostgreSQL + pgvector
              ├── Ollama models
              ├── Hugging Face models
              └── Document processing pipeline
```

See [docs/architecture.md](docs/architecture.md) for details.

# 🚦 Current status

The current stable frontend is implemented with Streamlit.

A ReactJS frontend migration is under active development. It is not yet the default public frontend. Until the migration is completed, the `main` branch focuses on the stable Streamlit, FastAPI, PostgreSQL/pgvector, Docker, Ollama, and Hugging Face stack.

# 🚀 Quick Start

## ✅ Prerequisites

- Git
- Docker and Docker Compose
- Python 3.10+
- NVIDIA GPU + NVIDIA Container Toolkit for local model acceleration
- Hugging Face token for gated/private models

## ▶️ Run locally

1. Clone the repository:
   ```bash
   git clone https://github.com/DataScienceLabFHSWF/KIKO-release.git
   ```
   ```bash
   cd KIKO-release
   ```
   ```bash
   cp .env.example .env
   ```
2. Launch the app:
   ```bash
   docker compose --project-name <YOUR_PROJECT_NAME> up --build
   ```

## ▶️ Open:

- Streamlit Frontend -> http://localhost:8003
- Fast API Backend (API) -> http://localhost:8004
- Fast API Backend (docs) -> http://localhost:8004/docs
- PostgreSQL -> Docker Host port is 8005 and database port is **5432**.
- Ollama -> Docker Host port is 8006 and Ollama port is **11434**.

**Note**:

- If multiple people are running the `docker-compose` on same server then it would be better to change the all service name in both `.env.example` and `docker-compose.yml` to avoid conflicts. e.g.- kiko-frontend-service => kiko-frontend-service-**username**.
- If you get port issue? Then change the respective **docker host port number** of service in file `.env.example` to different unused port.

## 🛑 Stop the app:

```bash
docker compose --project-name <YOUR_PROJECT_NAME> down --remove-orphans
```

# ⚙️ Configuration

KIKO is configured through environment variables.

Start from the example file:

```bash
cp .env.example .env
```

Never commit your real `.env` file.

Important variables:

| Variable              | Purpose                            |
| --------------------- | ---------------------------------- |
| SECRET_KEY            | JWT/application secret             |
| DATABASE_URL          | Backend database connection        |
| HUGGINGFACE_HUB_TOKEN | Optional Hugging Face access token |
| DOCKER_OLLAMA_URL     | Backend-to-Ollama service URL      |
| FRONTEND_PORT         | Host port for the frontend         |
| BACKEND_PORT          | Host port for the backend          |

See [.env.example](.env.example) for the full list.

# 📁 Project Structure

| Folder         | Purpose                                       |
| -------------- | --------------------------------------------- |
| backend/       | FastAPI backend                               |
| frontend/      | Current stable Streamlit frontend             |
| docker/ollama/ | Ollama container setup                        |
| shared/        | Shared utilities and configuration            |
| notebooks/     | Research and evaluation notebooks             |
| tests/backend/ | Backend tests                                 |
| docs/          | Public documentation and GitHub Pages content |
| .github/       | GitHub workflows and contribution templates   |

# 📚 Documentation

- Architecture
- Models
- Database development
- Notebook setup
- React migration status
- Optional ngrok deployment

The public project page is published with GitHub Pages from the [`docs/`](docs) directory.

# 🤝 Contributing

Contributions are welcome. Please read [`CONTRIBUTING.md`](CONTRIBUTING.md) before opening an issue or pull request.

For small changes, open a focused pull request. For larger changes, open an issue first so the design can be discussed.

# 📄 License

This project is released under the license specified in [`LICENSE`](LICENSE).

# 📌 Citation

If you use KIKO in academic work, please cite it using [`CITATION.cff`](CITATION.cff).

# 👨‍🔧 Maintainers

- [Amir](https://github.com/Amirkz80) – Data Engineering (DE), Fullstack.
- [Ole](https://github.com/hennkar) – DE, Ontology, Fullstack.
- [Ferdinand](https://github.com/f-schreiber) - Ontology, Fullstack.
- [Sanjay Gupta](https://github.com/sanjaycg486) – Fullstack, Architecture and LLMs.

**Automated dependency updates are handled by Dependabot.**

# 💬 Questions or Feedback?

Open an [issue](https://github.com/DataScienceLabFHSWF/KIKO-release/issues) for bugs, feature requests, or documentation improvements.
