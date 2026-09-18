"""
RoadVision — Phase 2A Video Detection Main CLI
==============================================
CLI entry point to run pretrained YOLO object detection on a road-scene video or live webcam.

Usage:
    python src/main.py --input input/sample_video.mp4
    python src/main.py --webcam 0
    python src/main.py --input input/road.mp4 --model yolov8s.pt --confidence 0.30 --device cpu
"""

import argparse
import logging
import os
import sys
import cv2
import yaml
from typing import Dict, Any

# Ensure project root is in python path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.detector import YOLODetector
from src.video_processor import VideoProcessor

# Setup basic logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("RoadVision")


def load_config(config_path: str = "config/config.yaml") -> Dict[str, Any]:
    """Load configuration from YAML file if it exists."""
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            logger.warning(f"Could not parse config file '{config_path}': {e}. Using default values.")
    return {}


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="RoadVision — YOLO Road Scene Video & Live Webcam Detection Prototype"
    )
    parser.add_argument(
        "--input", "-i",
        type=str,
        default=None,
        help="Path to input video file (e.g., input/road_video.mp4)"
    )
    parser.add_argument(
        "--webcam", "-w",
        type=int,
        default=None,
        help="Webcam camera device index (e.g., 0 for default camera)"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default=None,
        help="Path to output video file (e.g., output/detected_video.mp4)"
    )
    parser.add_argument(
        "--model", "-m",
        type=str,
        default=None,
        help="YOLO model path or pretrained name (e.g., yolov8n.pt, yolov8s.pt)"
    )
    parser.add_argument(
        "--confidence", "-c",
        type=float,
        default=None,
        help="Confidence threshold for object detection (0.0 to 1.0, default: 0.25)"
    )
    parser.add_argument(
        "--device", "-d",
        type=str,
        default=None,
        help="Device to run inference on ('cpu', 'cuda', 'auto')"
    )
    parser.add_argument(
        "--config",
        type=str,
        default="config/config.yaml",
        help="Path to YAML configuration file"
    )
    return parser.parse_args()


def print_summary(summary: Dict[str, Any]) -> None:
    """Print clean human-readable execution summary."""
    print("\n" + "=" * 60)
    print(" RoadVision — Processing Summary")
    print("=" * 60)
    print(f"Status:             {summary.get('status', 'SUCCESS').upper()}")
    print(f"Input:              {summary.get('input_path', 'Live Webcam')}")
    if 'output_path' in summary:
        print(f"Output Video:       {summary['output_path']}")
    print(f"Frames Processed:   {summary['frames_processed']}")
    print(f"Processing Time:    {summary['elapsed_seconds']}s")
    print(f"Average FPS:        {summary['average_fps']} FPS")
    print("-" * 60)
    print("Detections Summary (across all frames):")

    class_counts = summary.get("class_counts", {})
    if class_counts:
        sorted_counts = sorted(class_counts.items(), key=lambda x: x[1], reverse=True)
        for class_name, count in sorted_counts:
            print(f"  • {class_name.capitalize():<15}: {count}")
    else:
        print("  • No objects detected.")

    total_unique = summary.get('total_unique_objects', summary.get('total_detections', 0))
    print(f"Total Unique Objects: {total_unique}")
    if 'total_raw_detections' in summary:
        print(f"Total Raw Detections: {summary['total_raw_detections']}")
    print("=" * 60 + "\n")


def run_live_webcam_cli(processor: VideoProcessor, camera_index: int, confidence: float):
    """Run live OpenCV window for terminal webcam detection."""
    logger.info(f"Opening live webcam feed on device index {camera_index}... Press 'q' to stop.")
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        logger.error(f"Unable to open camera device index {camera_index}")
        sys.exit(1)

    window_name = "RoadVision — Live Webcam Detection (Press 'q' to Quit)"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

    frames_processed = 0
    total_detections_count = 0
    class_counts: Dict[str, int] = {}
    import time
    start_time = time.time()

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            detections = processor.detector.predict(frame, confidence_threshold=confidence)
            annotated_frame = processor.render_detections(frame, detections)

            frames_processed += 1
            total_detections_count += len(detections)
            for det in detections:
                class_counts[det.class_name] = class_counts.get(det.class_name, 0) + 1

            cv2.imshow(window_name, annotated_frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()

    elapsed = time.time() - start_time
    avg_fps = frames_processed / elapsed if elapsed > 0 else 0.0

    print_summary({
        "status": "success",
        "input_path": f"Webcam Device #{camera_index}",
        "frames_processed": frames_processed,
        "total_detections": total_detections_count,
        "class_counts": class_counts,
        "elapsed_seconds": round(elapsed, 2),
        "average_fps": round(avg_fps, 2)
    })


def main():
    args = parse_args()
    config = load_config(args.config)

    # Resolve settings (CLI args override config defaults)
    model_cfg = config.get("model", {})
    video_cfg = config.get("video", {})

    model_path = args.model or model_cfg.get("weights_path") or "yolov8n.pt"
    if not os.path.exists(model_path) and not model_path.endswith(".pt"):
        model_path = "yolov8n.pt"
    elif not os.path.exists(model_path) and model_path.startswith("models/"):
        logger.info(f"Custom weights '{model_path}' not found yet. Using pretrained 'yolov8n.pt'.")
        model_path = "yolov8n.pt"

    confidence = args.confidence if args.confidence is not None else model_cfg.get("confidence_threshold", 0.25)
    device = args.device or model_cfg.get("device", "auto")

    frame_skip = video_cfg.get("frame_skip", 1)
    max_width = video_cfg.get("max_width", 1280)

    logger.info("Initializing YOLODetector...")
    try:
        detector = YOLODetector(
            model_path=model_path,
            confidence_threshold=confidence,
            device=device
        )
    except Exception as e:
        logger.error(f"Failed to initialize detector: {e}")
        sys.exit(1)

    logger.info("Initializing VideoProcessor...")
    processor = VideoProcessor(
        detector=detector,
        output_dir="output",
        frame_skip=frame_skip,
        max_width=max_width
    )

    # If --webcam is specified, run webcam loop
    if args.webcam is not None:
        run_live_webcam_cli(processor, camera_index=args.webcam, confidence=confidence)
        return

    # Video file mode
    input_path = args.input or video_cfg.get("default_input") or "input/sample.mp4"
    output_path = args.output

    if not os.path.exists(input_path):
        print(f"\n[ERROR] Input video not found: '{input_path}'")
        print("Provide a valid input video path using: python src/main.py --input <path_to_video.mp4>")
        print("Or run live webcam mode using:          python src/main.py --webcam 0\n")
        sys.exit(1)

    try:
        summary = processor.process_video(
            input_path=input_path,
            output_path=output_path,
            confidence_threshold=confidence
        )
        print_summary(summary)
    except Exception as e:
        logger.error(f"Error processing video: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
