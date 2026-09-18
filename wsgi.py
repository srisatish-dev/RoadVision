"""
RoadVision — WSGI Production Server Entrypoint
==============================================
Provides the WSGI application object for Gunicorn, Waitress, and cloud platforms
(Hugging Face Spaces, Render, Railway, AWS, GCP).

Usage with Gunicorn:
    gunicorn --workers 1 --threads 4 --timeout 120 --bind 0.0.0.0:$PORT wsgi:app
"""

import os
import sys

# Ensure root directory is in python path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app import create_app

config_path = os.environ.get("ROADVISION_CONFIG", "config/config.yaml")
app = create_app(config_path)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
