# ─────────────────────────────────────────────────────────────
# CricketIQ Backend — Dockerfile
# Multi-stage build for a lean production image.
# ─────────────────────────────────────────────────────────────

# ── Stage 1: dependency builder ───────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /app

# System deps for psycopg2 & asyncpg compilation
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc libpq-dev curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install --prefix=/install --no-cache-dir -r requirements.txt

# ── Stage 2: runtime image ────────────────────────────────────
FROM python:3.11-slim AS runtime

WORKDIR /app

# Runtime deps only
RUN apt-get update && apt-get install -y --no-install-recommends libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy project source
COPY . .

# Create non-root user for security
RUN useradd -m -u 1000 cricketiq && chown -R cricketiq:cricketiq /app
USER cricketiq

# Expose API port
EXPOSE 8000

# Default command (overridable via docker-compose or platform env)
CMD ["sh", "backend/start.sh"]
