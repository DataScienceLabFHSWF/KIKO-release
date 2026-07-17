FROM python:3.10-slim
WORKDIR /frontend

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

CMD ["sh", "-c", "streamlit run main.py --server.port=${FRONTEND_PORT} --server.address=0.0.0.0"]