# SuperClaude Docker Image
# Multi-stage build for optimal image size

FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Create app directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements files
COPY examples/gemini-file-search/requirements.txt /app/requirements-gemini.txt
COPY examples/tv3-integration/requirements.txt /app/requirements-tv3.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r /app/requirements-gemini.txt && \
    pip install --no-cache-dir -r /app/requirements-tv3.txt

# Copy application code
COPY . /app/

# Create directory for outputs
RUN mkdir -p /app/outputs

# Set permissions
RUN chmod +x /app/deploy.sh /app/examples/demo/demo_test.py

# Default command - run demo tests
CMD ["python3", "examples/demo/demo_test.py"]

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python3 -c "import sys; sys.exit(0)"

# Labels
LABEL maintainer="SuperClaude Team"
LABEL version="2.0.1"
LABEL description="SuperClaude with MCP integrations and Gemini File Search RAG"
LABEL documentation="https://github.com/NomenAK/SuperClaude"

# Expose port for potential web interface (future)
EXPOSE 8000

# Volume for persistent data
VOLUME ["/app/outputs", "/app/.env"]
