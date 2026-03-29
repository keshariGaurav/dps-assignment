FROM python:3.12-slim

WORKDIR /app

# Install system deps required for uvloop
RUN apt-get update && apt-get install -y \
    gcc \
    build-essential \
    python3-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install --no-cache-dir uv

# VERY IMPORTANT: force uv to use system python
ENV UV_PYTHON=python3.12

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen

# Copy code
COPY . .

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uv", "run", "python", "main.py"]