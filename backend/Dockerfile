FROM python:3.10-slim

WORKDIR /backend


# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    git git-lfs \
    libgl1 libglib2.0-0 \
    build-essential python3-dev \
    tesseract-ocr \
    tesseract-ocr-eng \
    && rm -rf /var/lib/apt/lists/* \
    && git lfs install

# Install Poetry
RUN pip install --no-cache-dir poetry

# Configure Poetry: don't create virtual env (we're in container)
RUN poetry config virtualenvs.create false

# Copy pyproject.toml and poetry.lock
COPY pyproject.toml poetry.lock ./

# Install dependencies
RUN poetry install --only=main --no-root

# Copy the rest of the application
COPY . .

CMD ["sh", "-c", "python init_db.py && uvicorn app.main:app --host 0.0.0.0 --port ${BACKEND_PORT}"]
