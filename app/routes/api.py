"""
RoadVision — REST API Routes
=============================
JSON API endpoints for video upload, processing control, frame streaming,
live webcam stream, and scene summary status.
"""

import os
import time
import base64
import logging
from typing import Dict, Any
import cv2
import numpy as np
from flask import Blueprint, request, jsonify, current_app, send_from_directory, Response
from werkzeug.utils import secure_filename

from src.detector import YOLODetector
from src.video_processor import VideoProcessor

logger = logging.getLogger(__name__)

api_bp = Blueprint("api", __name__)

# Global state instances
_detector_instance: YOLODetector = None
_last_summary: Dict[str, Any] = {}
_is_processing: bool = False

# Live Webcam State
_webcam_active: bool = False
_live_webcam_summary: Dict[str, Any] = {}


def get_detector() -> YOLODetector:
    """Lazy initializer for YOLODetector."""
    global _detector_instance
    if _detector_instance is None:
        model_path = current_app.config.get("MODEL_PATH", "yolov8n.pt")
        conf_thresh = current_app.config.get("CONF_THRESH", 0.25)
        device = current_app.config.get("DEVICE", "auto")
        _detector_instance = YOLODetector(
            model_path=model_path,
            confidence_threshold=conf_thresh,
            device=device
        )
    return _detector_instance


@api_bp.route("/api/upload", methods=["POST"])
def upload_video():
    """Upload input video file."""
    if "video" not in request.files:
        return jsonify({"status": "error", "error": "No video file provided"}), 400

    file = request.files["video"]
    if not file or file.filename == "":
        return jsonify({"status": "error", "error": "No file selected"}), 400

    upload_folder = current_app.config.get("UPLOAD_FOLDER", "data/uploads")
    os.makedirs(upload_folder, exist_ok=True)

    original_filename = file.filename
    sanitized_filename = secure_filename(original_filename)
    if not sanitized_filename:
        sanitized_filename = f"upload_{int(time.time())}.mp4"

    save_path = os.path.join(upload_folder, sanitized_filename)
    file.save(save_path)

    logger.info(f"Uploaded video saved to: '{save_path}'")
    return jsonify({
        "status": "success",
        "message": f"Video uploaded successfully: {sanitized_filename}",
        "filename": sanitized_filename,
        "original_filename": original_filename,
        "input_path": save_path
    })


@api_bp.route("/api/process/start", methods=["POST"])
def start_processing():
    """Start video processing on an uploaded file."""
    global _is_processing, _last_summary

    data = request.get_json(silent=True) or {}
    requested_filename = data.get("filename")

    upload_folder = current_app.config.get("UPLOAD_FOLDER", "data/uploads")
    output_folder = current_app.config.get("OUTPUT_FOLDER", "output")
    os.makedirs(upload_folder, exist_ok=True)
    os.makedirs(output_folder, exist_ok=True)

    input_path = None
    target_filename = None

    if requested_filename:
        # Check direct filename and sanitized filename
        clean_name = secure_filename(requested_filename)
        candidates = [
            os.path.join(upload_folder, requested_filename),
            os.path.join(upload_folder, clean_name),
            os.path.join("input", requested_filename),
            os.path.join("input", clean_name),
            requested_filename
        ]
        for c in candidates:
            if os.path.exists(c) and os.path.isfile(c):
                input_path = c
                target_filename = os.path.basename(c)
                break

    # Fallback to latest uploaded file if not found
    if not input_path:
        if os.path.exists(upload_folder):
            files = [f for f in os.listdir(upload_folder) if not f.startswith(".")]
            if files:
                # Sort by modification time descending
                files.sort(key=lambda f: os.path.getmtime(os.path.join(upload_folder, f)), reverse=True)
                input_path = os.path.join(upload_folder, files[0])
                target_filename = files[0]

    # Fallback to sample video in input/
    if not input_path and os.path.exists("input"):
        sample_files = [f for f in os.listdir("input") if f.endswith((".mp4", ".avi", ".mov"))]
        if sample_files:
            input_path = os.path.join("input", sample_files[0])
            target_filename = sample_files[0]

    if not input_path or not os.path.exists(input_path):
        return jsonify({
            "status": "error",
            "error": "No valid video file found to process. Please select a video file first."
        }), 400

    name, ext = os.path.splitext(target_filename)
    if not ext:
        ext = ".mp4"
    output_filename = f"{name}_processed{ext}"
    output_path = os.path.join(output_folder, output_filename)

    try:
        _is_processing = True
        detector = get_detector()
        processor = VideoProcessor(detector=detector, output_dir=output_folder)

        summary = processor.process_video(input_path=input_path, output_path=output_path)
        _last_summary = summary

        return jsonify({
            "status": "success",
            "message": "Video processed successfully",
            "summary": summary,
            "output_filename": output_filename,
            "stream_url": f"/api/stream/{output_filename}",
            "download_url": f"/api/output/{output_filename}"
        })
    except Exception as e:
        logger.error(f"Error processing video in web API: {e}", exc_info=True)
        return jsonify({"status": "error", "error": f"Processing failed: {str(e)}"}), 500
    finally:
        _is_processing = False


@api_bp.route("/api/process/stop", methods=["POST"])
@api_bp.route("/api/process/reset", methods=["POST"])
def reset_processing():
    """Reset processing state."""
    global _is_processing
    _is_processing = False
    return jsonify({"status": "success", "message": "Processing state reset."})


@api_bp.route("/api/stream/<filename>", methods=["GET"])
def stream_output(filename: str):
    """Stream processed output video as live MJPEG frames for browser playback."""
    output_folder = current_app.config.get("OUTPUT_FOLDER", "output")
    file_path = os.path.join(output_folder, filename)
    if not os.path.exists(file_path):
        return jsonify({"status": "error", "error": f"Output file '{filename}' not found"}), 404

    def generate_frames():
        cap = cv2.VideoCapture(file_path)
        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        frame_delay = max(0.01, 1.0 / fps)

        try:
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    # Loop playback when reaching end of video
                    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    continue

                ret_encode, buffer = cv2.imencode('.jpg', frame)
                if not ret_encode:
                    continue

                frame_bytes = buffer.tobytes()
                yield (
                    b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n'
                )
                time.sleep(frame_delay)
        finally:
            cap.release()

    return Response(
        generate_frames(),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )


# ---------------------------------------------------------------------------
# LIVE WEBCAM API ENDPOINTS
# ---------------------------------------------------------------------------

def _update_webcam_stats(stats: Dict[str, Any]):
    """Callback to store real-time webcam statistics."""
    global _live_webcam_summary
    _live_webcam_summary = stats


@api_bp.route("/api/webcam/start", methods=["POST"])
def start_webcam():
    """Start live webcam analysis session."""
    global _webcam_active, _live_webcam_summary
    _webcam_active = True
    _live_webcam_summary = {
        "status": "live",
        "frames_processed": 0,
        "total_unique_objects": 0,
        "total_raw_detections": 0,
        "class_counts": {},
        "elapsed_seconds": 0,
        "average_fps": 0.0
    }
    return jsonify({
        "status": "success",
        "message": "Live webcam analysis started",
        "stream_url": "/api/webcam/stream"
    })


@api_bp.route("/api/webcam/stop", methods=["POST"])
def stop_webcam():
    """Stop live webcam analysis session."""
    global _webcam_active
    _webcam_active = False
    return jsonify({
        "status": "success",
        "message": "Live webcam analysis stopped"
    })


@api_bp.route("/api/webcam/stream", methods=["GET"])
def webcam_stream():
    """Stream live webcam feed with YOLO object detection rendered in real time."""
    global _webcam_active

    camera_index = request.args.get("index", 0, type=int)
    _webcam_active = True

    detector = get_detector()
    processor = VideoProcessor(detector=detector)

    def is_active():
        return _webcam_active

    return Response(
        processor.generate_webcam_stream(
            camera_index=camera_index,
            is_active_check=is_active,
            stats_callback=_update_webcam_stats
        ),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )


_client_processor: VideoProcessor = None
_client_frames_count: int = 0
_client_start_time: float = 0.0


@api_bp.route("/api/webcam/infer_frame", methods=["POST"])
def infer_webcam_frame():
    """
    Process a single webcam frame sent from the client browser.
    Ensures live camera works seamlessly when deployed on cloud servers (Render, Hugging Face, etc.).
    """
    global _client_processor, _client_frames_count, _client_start_time, _live_webcam_summary

    data = request.get_json(silent=True) or {}
    image_b64 = data.get("image")
    if not image_b64:
        return jsonify({"status": "error", "error": "No image payload provided"}), 400

    try:
        # Reset tracking session if requested
        if data.get("reset"):
            detector = get_detector()
            _client_processor = VideoProcessor(detector=detector)
            _client_processor.tracker.reset()
            _client_frames_count = 0
            _client_start_time = time.time()

        # Decode base64 image
        if "," in image_b64:
            image_b64 = image_b64.split(",", 1)[1]
        img_bytes = base64.b64decode(image_b64)
        np_arr = np.frombuffer(img_bytes, np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        if frame is None:
            return jsonify({"status": "error", "error": "Invalid image data"}), 400

        detector = get_detector()
        if _client_processor is None:
            _client_processor = VideoProcessor(detector=detector)
            _client_processor.tracker.reset()
            _client_frames_count = 0
            _client_start_time = time.time()

        # Run detection & tracking
        detections = detector.predict(frame, confidence_threshold=0.20)
        tracked_objects = _client_processor.tracker.update(detections)
        annotated_frame = _client_processor.render_tracked_objects(frame, tracked_objects)

        _client_frames_count += 1
        elapsed = time.time() - _client_start_time
        fps = _client_frames_count / elapsed if elapsed > 0 else 0.0

        ret_encode, buffer = cv2.imencode('.jpg', annotated_frame, [cv2.IMWRITE_JPEG_QUALITY, 75])
        annotated_b64 = "data:image/jpeg;base64," + base64.b64encode(buffer.tobytes()).decode('utf-8')

        summary = {
            "status": "live",
            "frames_processed": _client_frames_count,
            "total_unique_objects": _client_processor.tracker.get_total_unique_objects(),
            "total_raw_detections": len(detections),
            "class_counts": _client_processor.tracker.get_unique_counts(),
            "currently_visible": len(tracked_objects),
            "elapsed_seconds": round(elapsed, 1),
            "average_fps": round(fps, 1)
        }
        _live_webcam_summary = summary

        return jsonify({
            "status": "success",
            "image": annotated_b64,
            "summary": summary
        })
    except Exception as e:
        logger.error(f"Error in infer_webcam_frame: {e}", exc_info=True)
        return jsonify({"status": "error", "error": str(e)}), 500


@api_bp.route("/api/webcam/summary", methods=["GET"])
def get_webcam_summary():
    """Get latest live webcam analysis summary."""
    return jsonify(_live_webcam_summary)


@api_bp.route("/api/output/<filename>", methods=["GET"])
def download_output(filename: str):
    """Serve processed output video files."""
    output_folder = current_app.config.get("OUTPUT_FOLDER", "output")
    return send_from_directory(output_folder, filename, as_attachment=True)


@api_bp.route("/api/summary", methods=["GET"])
def get_summary():
    """Get latest processing summary."""
    return jsonify(_last_summary)


@api_bp.route("/api/status", methods=["GET"])
def get_status():
    """Get current status."""
    return jsonify({
        "processing": _is_processing,
        "webcam_active": _webcam_active,
        "has_last_summary": bool(_last_summary)
    })
