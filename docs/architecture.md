# 🏗️ Architecture

KIKO is organized as a Docker-based application with a frontend, backend, database, vector search, model runtime, and document-processing pipeline.

## High-level architecture

```text
User
  |
  v
Frontend
  |
  v
FastAPI Backend
  |
  +--> PostgreSQL + pgvector
  |
  +--> Ollama
  |
  +--> Hugging Face models
  |
  +--> Document processing pipeline
```
