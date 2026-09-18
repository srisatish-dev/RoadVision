"""
RoadVision — Main Page Routes
=============================
Renders the HTML web interface.
"""

from flask import Blueprint, render_template

main_bp = Blueprint("main", __name__)


@main_bp.route("/", methods=["GET"])
def index():
    """Render main dashboard page."""
    return render_template("dashboard.html")
