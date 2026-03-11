# 1. Use a minimal Python base image to reduce attack surface (LotL mitigation)
FROM python:3.11-slim

# Set environment variables securely
# Don't write pyc files to physical disk
ENV PYTHONDONTWRITEBYTECODE=1
# Force stdout/stderr unbuffered to ensure logs stream immediately
ENV PYTHONUNBUFFERED=1

# 2. Principle of Least Privilege: Create a non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set working directory
WORKDIR /app

# Create the data directory that will be mounted as tmpfs (in-memory)
RUN mkdir -p /app/data

# Copy dependency requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . /app

# Ensure the non-root user owns the application directory
RUN chown -R appuser:appuser /app

# 3. Switch to the non-root user
USER appuser

# Default command to run the Python worker (pipeline will be built in Phase 3)
# For now, it will just keep the container alive or run a placeholder script
CMD ["python", "-c", "print('Secure Python Worker Initialized... waiting for pipeline commands.') && sleep infinity"]
