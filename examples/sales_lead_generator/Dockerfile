# Sales Lead Generator Dockerfile
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH=/app

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY config/ ./config/

# Create data directory
RUN mkdir -p /app/data /app/logs

# Create non-root user
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.path.append('/app'); from src.lead_generator import SalesLeadGenerator; print('OK')" || exit 1

# Default command
CMD ["python", "-m", "src.main", "--single-run"]

# Expose port for web interface (optional)
EXPOSE 8000

# Labels
LABEL maintainer="Cursor AI Agent Ecosystem"
LABEL version="2.0.0"
LABEL description="Sales Lead Generator - Professional B2B Lead Generation System"
