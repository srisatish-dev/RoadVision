"""
RoadVision — REST API Routes
=============================
JSON API endpoints consumed by the JavaScript frontend.

Planned Endpoints:

    POST /api/upload
        Accept a driving video file upload.
        Returns: { "status": "ok", "filename": "..." }

    POST /api/process/start
        Start the CV pipeline on the uploaded video.
        Returns: { "status": "started" }

    POST /api/process/stop
        Stop the running CV pipeline.
        Returns: { "status": "stopped" }

    GET  /api/frame
        Return the latest annotated video frame as a base64-encoded JPEG.
        Returns: { "frame": "<base64>", "timestamp": "..." }

    GET  /api/summary
        Return the latest road scene summary as JSON.
        Returns: {
            "total_objects": int,
            "vehicles": int,
            "road_users": int,
            "infrastructure": int,
            "road_hazards": int,
            "per_class": { class: count },
            "density": "LOW|MEDIUM|HIGH",
            "moving": int,
            "stationary": int,
            "danger_zone_active": bool,
            "alerts": [ alert_string, ... ],
            "objects": [
                {
                    "track_id": int,
                    "class_name": str,
                    "confidence": float,
                    "bbox": [x1, y1, x2, y2],
                    "h_zone": "LEFT|CENTER|RIGHT",
                    "v_zone": "FAR|NEAR",
                    "motion_state": "Moving|Stationary"
                },
                ...
            ]
        }

    GET  /api/status
        Return the current pipeline status.
        Returns: { "running": bool, "video_loaded": bool, "frame_count": int }

NOTE: This file is a STUB. Full implementation begins in Phase 2.
"""

# routes/api.py — Placeholder
