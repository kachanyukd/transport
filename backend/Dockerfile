# ============================================================
# Stage 1: builder — install dependencies, compile extensions
# ============================================================
FROM python:3.12-slim AS builder

WORKDIR /app

# System packages required to compile psycopg2-binary
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Install all dependencies to a local prefix so stage 2 is clean
RUN pip install --upgrade pip --quiet \
    && pip install --prefix=/install -r requirements.txt --quiet

# ============================================================
# Stage 2: runtime — clean image without build tools
# Result: ~180 MB (vs ~800 MB single-stage)
# ============================================================
FROM python:3.12-slim AS runtime

WORKDIR /app

# Only runtime lib needed (psycopg2-binary links against libpq)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy compiled packages from builder stage
COPY --from=builder /install /usr/local

# Copy application source
COPY . .

# Create non-root user for security
RUN useradd --no-create-home --shell /bin/false fleet \
    && chown -R fleet:fleet /app
USER fleet

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=fleet.settings.production

EXPOSE 8000

# Run migrations then start Gunicorn
CMD ["sh", "-c", "python manage.py migrate --noinput && \
    python manage.py collectstatic --noinput && \
    gunicorn fleet.wsgi:application \
      --bind 0.0.0.0:8000 \
      --workers 4 \
      --worker-class gthread \
      --threads 2 \
      --timeout 60 \
      --access-logfile - \
      --error-logfile -"]
