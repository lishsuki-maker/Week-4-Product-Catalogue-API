# Stage 1: build
FROM python:3.12 AS builder
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Stage 2: runtime
FROM python:3.12
WORKDIR /app
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl=8.14.1-2+deb13u4 && \
    rm -rf /var/lib/apt/lists/*

# Create a non-root user
RUN useradd --create-home --uid 1001 appuser


COPY --from=builder /install /usr/local
COPY app.py .

USER 1001

EXPOSE 5000

# Healthcheck
HEALTHCHECK --interval=10s --timeout=3s --retries=5 \
    CMD ["curl", "-f", "http://localhost:5000/api/dbcheck"]
    
CMD ["python3", "app.py"]
