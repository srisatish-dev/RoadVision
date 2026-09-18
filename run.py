"""
RoadVision — Flask Web Server Entry Point
=========================================
Run the local web application:

    python run.py

Then open in your browser:
    http://localhost:5000
"""

import os
import sys
import yaml

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app import create_app


def main():
    app = create_app("config/config.yaml")

    # Load host/port from config
    host = "0.0.0.0"
    port = 5000
    debug = True

    if os.path.exists("config/config.yaml"):
        with open("config/config.yaml", "r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f) or {}
            server_cfg = cfg.get("server", {})
            host = server_cfg.get("host", host)
            port = server_cfg.get("port", port)
            debug = server_cfg.get("debug", debug)

    print("\n" + "=" * 60)
    print(" 🚗 Starting RoadVision Web Application")
    print(f" Access URL: http://localhost:{port}")
    print("=" * 60 + "\n")

    app.run(host=host, port=port, debug=debug)


if __name__ == "__main__":
    main()
