# RoadVision — Deployment Guide

This guide provides instructions to deploy RoadVision on free cloud hosting services and container platforms.

---

## Option 1: Hugging Face Spaces (Recommended — 100% Free & Fast)

Hugging Face Spaces provides free cloud hosting with CPU and optional GPU support.

### Steps:
1. Create a free account on [huggingface.co](https://huggingface.co).
2. Click **New Space** ([huggingface.co/new-space](https://huggingface.co/new-space)).
3. Fill in:
   - **Space name**: `roadvision` (or your choice)
   - **License**: `mit` or `apache-2.0`
   - **Space SDK**: Select **Docker** -> **Blank**
   - **Space hardware**: Free CPU (2 vCPU, 16 GB RAM)
4. Push or upload this project repository to your Hugging Face Space:
   ```bash
   git remote add space https://huggingface.co/spaces/YOUR_USERNAME/roadvision
   git push space main
   ```
5. Hugging Face will automatically detect the `Dockerfile`, build the image, pre-download YOLOv8 weights, and launch the application on port `7860`.

---

## Option 2: Render.com (Free Web Service)

Render builds and hosts Docker web services directly from GitHub.

### Steps:
1. Push your repository to your GitHub account.
2. Sign in to [render.com](https://render.com).
3. Click **New +** -> **Web Service**.
4. Connect your GitHub repository.
5. Render will automatically detect the included `render.yaml` or `Dockerfile`:
   - **Environment**: `Docker`
   - **Plan**: `Free`
6. Click **Create Web Service**.
7. Once deployed, Render will provide a public HTTPS URL (e.g., `https://roadvision-app.onrender.com`).

---

## Option 3: Railway.app

1. Sign in to [railway.app](https://railway.app).
2. Click **New Project** -> **Deploy from GitHub repo**.
3. Select your `RoadVision` repository.
4. Railway will automatically build the `Dockerfile` and expose the web app.

---

## Option 4: Local Docker Container

Run the production container locally with Docker:

```bash
# Build the Docker image
docker build -t roadvision:latest .

# Run the container on port 5000
docker run -d -p 5000:7860 --name roadvision-app roadvision:latest
```

Open [`http://localhost:5000`](http://localhost:5000) in your browser.
