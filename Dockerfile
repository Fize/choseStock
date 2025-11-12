# syntax=docker/dockerfile:1.6

FROM python:3.11-slim AS builder

WORKDIR /app

ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:${PATH}"

COPY pyproject.toml uv.lock ./

# Derive an installable requirements file directly from the project metadata
RUN python - <<'PY'
import tomllib
from pathlib import Path
project = tomllib.loads(Path("pyproject.toml").read_text())
reqs = "\n".join(project.get("project", {}).get("dependencies", [])) + "\n"
Path("requirements.txt").write_text(reqs)
PY

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY dataflows_mcp ./dataflows_mcp

FROM python:3.11-slim AS runtime

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:${PATH}"

RUN apt-get update && apt-get install -y --no-install-recommends \
    libxml2 \
    libxslt1.1 \
    libffi8 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /opt/venv /opt/venv
COPY dataflows_mcp ./dataflows_mcp

EXPOSE 8000

# CMD ["python", "-m", "dataflows_mcp.server.mcp_server", "--transport", "streamable-http", "--host", "0.0.0.0", "--port", "8000"]
# CMD ["a-share-mcp", "--transport", "sse", "--host", "0.0.0.0", "--port", "8000"]
CMD ["python", "-m", "dataflows_mcp.server.mcp_server", "--transport", "sse", "--host", "0.0.0.0", "--port", "8000"]
