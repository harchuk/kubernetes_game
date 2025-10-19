FROM python:3.11-slim

ENV POETRY_VERSION=1.8.3
WORKDIR /app

RUN pip install "poetry==${POETRY_VERSION}" && \
    poetry config virtualenvs.create false

COPY pyproject.toml poetry.lock* ./
RUN poetry install --no-root

COPY app ./app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
