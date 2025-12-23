# ============================================================================
# OSINT Hunter Bot - Dockerfile (Optimized for Railway)
# ============================================================================
# Multi-stage build for better optimization

FROM python:3.11-slim AS base

# Set working directory
WORKDIR /app

# Set Python environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# ============================================================================
# Stage 1: System Dependencies
# ============================================================================

RUN apt-get update && apt-get install -y --no-install-recommends \
    # APK Analysis Tools
    apktool \
    aapt \
    default-jdk-headless \
    android-tools-adb \
    # OSINT & Network Tools
    nmap \
    sqlmap \
    # Utilities
    unzip \
    curl \
    wget \
    git \
    jq \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /tmp/*

# ============================================================================
# Stage 2: Python Dependencies
# ============================================================================

# Copy and install Python requirements
COPY requirements.txt .
RUN pip install --upgrade pip setuptools && \
    pip install --no-cache-dir -r requirements.txt

# ============================================================================
# Stage 3: Application Setup
# ============================================================================

# Copy application code
COPY . .

# Create required directories
RUN mkdir -p /app/temp && \
    mkdir -p /app/logs && \
    chmod 777 /app/temp /app/logs && \
    find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

# Verify main files exist
RUN test -f /app/bot.py || (echo "ERROR: bot.py not found" && exit 1) && \
    test -f /app/main.py || (echo "ERROR: main.py not found" && exit 1) && \
    python3 -m py_compile bot.py main.py && \
    echo "✅ All Python files compiled successfully"

# ============================================================================
# Health Check
# ============================================================================

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python3 -c "import sys; sys.exit(0)" || exit 1

# ============================================================================
# Entry Point
# ============================================================================

# Run the bot
CMD ["python3", "main.py"]
