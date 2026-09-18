# =============================================================================
# RoadVision — Production Docker Container
# Compatible with: Hugging Face Spaces, Render, Railway, AWS ECS, GCP Cloud Run
# =============================================================================
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    PORT=7860 \
    OMP_NUM_THREADS=4 \
    MKL_NUM_THREADS=4

# Install essential system dependencies for OpenCV and video processing
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    ffmpeg \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set up working directory
WORKDIR /app

# Create a non-root user (required for Hugging Face Spaces & security)
RUN useradd -m -u 1000 user && \
    mkdir -p /app/data/uploads /app/output /app/input /app/models && \
    chown -R user:user /app

# Install python dependencies
COPY --chown=user:user requirements.txt /app/
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY --chown=user:user . /app/

# Switch to non-root user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

# Pre-download YOLOv8n weights inside container to eliminate cold-start lag
RUN python -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"

# Expose standard container port
EXPOSE 7860 5000

# Start Gunicorn WSGI server binding to dynamic cloud PORT (fallback to 7860)
CMD ["sh", "-c", "gunicorn --workers 1 --threads 4 --timeout 180 --bind 0.0.0.0:${PORT:-7860} wsgi:app"]
