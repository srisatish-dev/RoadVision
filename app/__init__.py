"""
RoadVision — Flask Application Factory
=======================================
Factory to initialize and configure the Flask web application.
"""

import os
import yaml
from flask import Flask


def create_app(config_path: str = "config/config.yaml") -> Flask:
    """Create and configure Flask application."""
    app = Flask(__name__)

    # Load YAML config
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f) or {}
    else:
        cfg = {}

    server_cfg = cfg.get("server", {})
    model_cfg = cfg.get("model", {})

    app.config["SECRET_KEY"] = server_cfg.get("secret_key", "roadvision-dev-key")
    app.config["UPLOAD_FOLDER"] = server_cfg.get("upload_folder", "data/uploads")
    app.config["OUTPUT_FOLDER"] = "output"
    app.config["MODEL_PATH"] = model_cfg.get("weights_path", "yolov8n.pt")
    app.config["CONF_THRESH"] = model_cfg.get("confidence_threshold", 0.25)
    app.config["DEVICE"] = model_cfg.get("device", "auto")

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    os.makedirs(app.config["OUTPUT_FOLDER"], exist_ok=True)

    # Register Blueprints
    from app.routes.main import main_bp
    from app.routes.api import api_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp)

    return app
