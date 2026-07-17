# ![KIKO Logo](./frontend/assets/images/KIKO-Logo.png)

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

The platform for AI-supported competence and young talent development for the decommissioning of nuclear facilities. This project leverages cutting-edge AI technologies such as document processing, natural language models, OCR, vector stores, and more to automate the extraction of information and improve decision-making processes in the field of nuclear decommissioning.

## 🚀 Getting Started

### ✅ Prerequisites

- Python 3.10+
- Docker 20.10+
- Git
- Poetry 2.1.4
- Ollama
- Hugging Face

### ▶️ Run the Full Stack on server or local machine

1. Clone the repository:
   ```bash
   git clone git@github.com:DataScienceLabFHSWF/kiko-platform.git
   ```
   ```bash
   cd kiko-platform
   ```
2. Launch the app:
   ```bash
   docker compose --project-name <YOUR_PROJECT_NAME> up --build
   ```
3. Shut Down the app:
   `bash
docker compose --project-name <YOUR_PROJECT_NAME> down --remove-orphans
`
   💡 **Best Practice**:
   Always specify a unique `--project-name` flag when running Docker Compose on a shared server to prevent conflicts with other team members running similar or identical projects.

▶️ **Where to check API running?**

- Streamlit Frontend -> http://localhost:8003
- Fast API Backend (API) -> http://localhost:8004
- Fast API Backend (docs) -> http://localhost:8004/docs
- PostgreSQL -> Docker Host port is 8005 and database port is **5432**.
- Ollama -> Docker Host port is 8006 and Ollama port is **11434**.

**Note**:

- If multiple people are running the `docker-compose` on same server then it would be better to change the all service name in both `.env` and `docker-compose.yml` to avoid conflicts. e.g.- kiko-frontend-service => kiko-frontend-service-**username**.
- If you get port issue? Then change the respective **docker host port number** of service in file `.env` to different unused port.

User Ports:
| User | FRONTEND_PORT | BACKEND_PORT | DATABASE_HOST_PORT | OLLAMA_HOST_PORT |
|--------|---------------|--------------|--------------------|------------------|
| stage-test | 8003 | 8004 | 8005 | 8006 |
| amir | 8011 | 8012 | 8013 | 8014 |
| sanjay | 8021 | 8022 | 8023 | 8024 |
| ole | 8031 | 8032 | 8033 | 8034 |

### ▶️ Running jupyter notebooks (notebooks/)

1. Check the poetry version should be >2.0
   ```
   poetry --version
   ```
2. If poetry is missing
   ```
   curl -sSL https://install.python-poetry.org | python3 -
   ```
3. Add to PATH for current shell
   ```
   export PATH="/home/<user_name>/.local/bin/poetry"
   ```
4. Install exact versions from poetry.lock
   ```
   poetry install
   ```
5. If need to add another library
   ```
   poetry add <package-name> <package-name>
   ```
6. If added the library then Update all within constraints otherwise skip it.
   ```
   poetry update
   ```
7. Register a Jupyter kernel for this env
   ```
   poetry run python -m ipykernel install --user --name=kiko-notebooks --display-name "KIKO Notebooks"
   ```
   This lets you select **KIKO Notebooks** as the kernel inside Jupyter.
8. Launch Jupyter in the notebooks folder
   ```
   poetry run jupyter lab
   ```
   Open your .ipynb (e.g., kiko_eval_notebook.ipynb) and choose the **KIKO Notebooks** kernel.
9. Launch MLflow UI
   ```
   poetry run mlflow ui --host 0.0.0.0 --port 5050
   ```

### ▶️ Provide the running application as URL to external users

1. Follow above "▶️ Run the Full Stack on server" section until Launch app.
2. Open new terminal and Check if ngrok config file exists?
   ```
   ngrok config check
   ```
3. If no ngrok config file exists, create it manually:
   ```
   mkdir -p /home/<user_name>/snap/ngrok/current/.config/ngrok
   ```
   ```
   nano /home/<user_name>/snap/ngrok/current/.config/ngrok/ngrok.yml
   ```
4. Paste/update the following contents and save it:

   ```
   version: "1"
   agent:
       authtoken: <YOUR_NGROK_AUTH_TOKEN> # Copy from ngrok account

   tunnels:
       frontend:
           proto: http
           addr: 8003
       backend:
           proto: http
           addr: 8004
   ```

5. Verify config:
   ```
   ngrok config check
   ```
   If it’s valid, you’ll see no error.
6. Authenticate your ngrok agent. You only have to do this once. The Authtoken is saved in the default configuration file.
   ```
   ngrok config add-authtoken $YOUR_AUTHTOKEN
   ```
7. Screen mirror
   - Check if any screen is running:
     ```
     screen -list
     ```
   - Kill a screen session if you want to deploy application again:
     ```
     screen -XS <session-id> quit
     ```
   - Start new screen with tunnel:
     ```
     screen -S <tunnel-name>
     ```
   - Run application in tunnel:
     ```
     ngrok start --all
     ```
   - You should see two forwarding URLs, e.g.:
     ```
     Forwarding  https://abc123.ngrok-free.app -> http://localhost:8003
     Forwarding  https://xyz789.ngrok-free.app -> http://localhost:8004
     ```
   - Detach (leave it running in background):
     ```
     Ctrl+A then D
     ```
   - Later you can re-attach:
     ```
     screen -r <tunnel-name>
     ```
8. Share created URL with stakeholders.
   - 👉 Share only the frontend (8003) URL with stakeholders.
   - 👉 Keep backend (8004) private unless they need direct API access.
   - ⚠️ Important: Don’t expose DB (8005) or Ollama (8006) — they’re internal services.
9. Optional: Create tunnel between your local machine and server to see the ngrok-dashboard on localhost:4040.
   ```
   ssh -L 4040:localhost:4040 <username>@172.18.43.161
   ```

### 💾 Connect to `kiko-db-service` via pgAdmin (on local machine)

1. Install desktop [pgAdmin](https://www.pgadmin.org/)
2. Add New Server in pgAdmin:
   - Click Add New Server
   - Go to General tab:
     - Name: kiko-platform Database
   - Go to Connection tab:
     |Field |Value |
     |---------------|-----------|
     |Host |localhost (or kiko-db-service if inside Docker network) |
     |Port |5432 |
     |Username |kiko |
     |Password |kiko |
     |Maintenance DB |kiko-platform |
   - ✅ Optionally check: "Save password"
3. Test Connection
   - Click Save, and you should now see your kiko database and be able to:
     - View tables
     - Run queries
     - Inspect user data
     - Manually enter or edit values.

**Note**: Login credentials is in `backend/init_db.py` file.

## 🧩 How to Add a New Feature?

1. Backend (API + Service)

- Create a route under: `backend/app/api/routes/`.
- Add service logic in: `backend/app/services/`.
- Define model in: `backend/app/models/`.
- Register the route in `main.py`.

2. Frontend (Streamlit)

- Create a new page in `frontend/pages/`.
- Use `st.session_state.role` to control access.
- Use `render_sidebar()` from `pages.sidebar.py`.

3. Database (if needed)

- Add a SQLAlchemy ORM in `backend/app/orm_models/`.
- Add intial table creation logic in `scripts/init_db.py`.

## 🔐 Authentication & Roles

Roles supported:

- 👩‍🎓 **Learner**: View courses, ask questions.
- 👨‍🏫 **Instructor**: Upload docs, view learner statistics, ask quetions.
- 🛠️ **Admin**: Manage uploads, system settings, pipeline.

Stored in JWT and checked via:

```bash
Depends(require_role(["Learner", "Instructor", "Admin"]))
```

## 🧪 Running Tests

```bash
docker-compose exec kiko-backend-service bash
```

```bash
pytest tests/backend/
```

## 🤖 Tech Stack

| Layer      | Tool                    |
| ---------- | ----------------------- |
| Frontend   | Streamlit               |
| Backend    | FastAPI                 |
| DB         | PostgreSQL + pgvector   |
| Embeddings | sentence-transformers   |
| OCR/Tables | open-source VLM tools   |
| Deployment | Docker + Docker Compose |
| Auth       | JSON Web Token (JWT)    |

## 🤝 Contribution Guidelines

1. Fork or clone the repository.
   ```bash
   git clone git@github.com:DataScienceLabFHSWF/kiko-platform.git
   ```
2. Create a new branch
   ```bash
   git checkout -b develop-new-feature-name
   ```
3. Make your changes. Follow modular structure: route → model → service → test → UI.
4. Commit your changes
   ```bash
   git commit -am 'Add new feature'
   ```
5. Push to the branch
   ```bash
   git push origin develop-new-feature-name
   ```
6. Submit a [Pull Request](https://github.com/DataScienceLabFHSWF/kiko-platform/pulls) with a clear description.

## 👨‍🔧 Maintainers

- [Amir](https://github.com/Amirkz80) – Data Engineering (DE), Fullstack.
- [Ole](https://github.com/hennkar) – DE, Ontology, Fullstack.
- [Sanjay Gupta](https://github.com/sanjaycg486) – Fullstack, Architecture and LLMs.

## 💬 Questions or Feedback?

Open an [issue](https://github.com/DataScienceLabFHSWF/kiko-platform/issues) or start a discussion.
