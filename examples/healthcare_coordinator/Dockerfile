# Healthcare Coordinator Dockerfile
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH=/app
ENV HIPAA_COMPLIANT=true

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    libssl-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Create healthcare user for security
RUN groupadd -r healthcare && useradd -r -g healthcare healthcare

# Create necessary directories
RUN mkdir -p /app /healthcare/data /healthcare/logs /healthcare/config && \
    chown -R healthcare:healthcare /app /healthcare

# Set working directory
WORKDIR /app

# Copy Python requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy healthcare-specific configurations
COPY config/healthcare_config.json /healthcare/config/

# Copy application code
COPY src/ ./src/

# Create data and log directories with proper permissions
RUN chown -R healthcare:healthcare /app /healthcare

# Switch to healthcare user for security
USER healthcare

# Health check for healthcare systems
HEALTHCHECK --interval=60s --timeout=30s --start-period=120s --retries=3 \
    CMD python -c "
from src.patient_care_coordinator import PatientCareCoordinator
import asyncio

async def health_check():
    try:
        coordinator = PatientCareCoordinator()
        status = await coordinator.get_system_status()
        print('OK' if status['system_health'] == 'operational' else 'UNHEALTHY')
        await coordinator.cleanup()
    except Exception as e:
        print('ERROR:', str(e))
        exit(1)

asyncio.run(health_check())
" || exit 1

# Default command with healthcare compliance
CMD ["python", "-m", "src.patient_care_coordinator", "--system-status"]

# Labels for healthcare compliance
LABEL maintainer="Cursor AI Agent Ecosystem"
LABEL version="2.0.0"
LABEL description="Patient Care Coordinator - AI-Powered Healthcare Management"
LABEL hipaa_compliant="true"
LABEL healthcare_purpose="patient_care_coordination"

# Expose port for healthcare API (optional)
EXPOSE 8001

# Volumes for healthcare data persistence
VOLUME ["/healthcare/data", "/healthcare/logs", "/healthcare/config"]
