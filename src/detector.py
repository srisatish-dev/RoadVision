"""
RoadVision — Module: YOLO Detector (M2)
=======================================
Reusable detector abstraction for road-scene object detection using YOLO.

Abstracts Ultralytics YOLO logic so the rest of the system operates on a clean,
structured detection schema (class_id, class_name, confidence, x1, y1, x2, y2).
Includes multi-threaded CPU acceleration and configurable inference image resolution.
"""

import logging
import os
from typing import List, Dict, Any, Optional, Union
import numpy as np

logger = logging.getLogger(__name__)


class Detection:
    """Dataclass-like representation of a single object detection."""
    def __init__(
        self,
        class_id: int,
        class_name: str,
        confidence: float,
        x1: float,
        y1: float,
        x2: float,
        y2: float
    ):
        self.class_id = int(class_id)
        self.class_name = str(class_name)
        self.confidence = float(confidence)
        self.x1 = float(x1)
        self.y1 = float(y1)
        self.x2 = float(x2)
        self.y2 = float(y2)

    @property
    def width(self) -> float:
        return self.x2 - self.x1

    @property
    def height(self) -> float:
        return self.y2 - self.y1

    @property
    def centroid(self) -> tuple[float, float]:
        return (self.x1 + self.x2) / 2.0, (self.y1 + self.y2) / 2.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "class_id": self.class_id,
            "class_name": self.class_name,
            "confidence": round(self.confidence, 4),
            "x1": round(self.x1, 2),
            "y1": round(self.y1, 2),
            "x2": round(self.x2, 2),
            "y2": round(self.y2, 2),
            "centroid": (round(self.centroid[0], 2), round(self.centroid[1], 2))
        }

    def __repr__(self) -> str:
        return f"Detection({self.class_name}, conf={self.confidence:.2f}, bbox=[{self.x1:.1f},{self.y1:.1f},{self.x2:.1f},{self.y2:.1f}])"


class YOLODetector:
    """
    YOLO Object Detector wrapper. Handles model loading, device selection,
    multi-threading CPU optimization, and frame-by-frame inference.
    """

    def __init__(
        self,
        model_path: str = "yolov8n.pt",
        confidence_threshold: float = 0.25,
        device: Optional[str] = None
    ):
        self.model_path = model_path
        self.confidence_threshold = confidence_threshold
        self.device = self._resolve_device(device)
        self.model = None

        self._optimize_pytorch()
        self._load_model()

    def _optimize_pytorch(self) -> None:
        """Enable multi-threading on CPU for maximum throughput."""
        try:
            import torch
            num_threads = min(8, max(2, os.cpu_count() or 4))
            torch.set_num_threads(num_threads)
            logger.info(f"PyTorch configured with {num_threads} CPU worker threads.")
        except Exception as e:
            logger.debug(f"PyTorch thread optimization skipped: {e}")

    def _resolve_device(self, requested_device: Optional[str]) -> str:
        """Auto-detect or validate PyTorch device."""
        if requested_device and requested_device.lower() != "auto":
            return requested_device

        try:
            import torch
            if torch.cuda.is_available():
                logger.info(f"CUDA device detected: {torch.cuda.get_device_name(0)}")
                return "cuda"
        except ImportError:
            pass

        return "cpu"

    def _load_model(self) -> None:
        """Load Ultralytics YOLO model safely."""
        logger.info(f"Loading YOLO model from '{self.model_path}' on device '{self.device}'...")
        try:
            from ultralytics import YOLO
            self.model = YOLO(self.model_path)
            logger.info(f"Successfully loaded YOLO model: {self.model_path}")
        except Exception as e:
            err_msg = (
                f"Failed to load YOLO model '{self.model_path}'. "
                f"Error details: {e}. "
                "Ensure 'ultralytics' is installed and the weights file/name is valid."
            )
            logger.error(err_msg)
            raise RuntimeError(err_msg) from e

    def predict(
        self,
        frame: np.ndarray,
        confidence_threshold: Optional[float] = None,
        imgsz: Optional[int] = None
    ) -> List[Detection]:
        """
        Perform object detection on a single video frame (numpy BGR image).

        :param frame: BGR image array from OpenCV
        :param confidence_threshold: Override instance confidence threshold if provided
        :param imgsz: Optional inference image size (e.g., 384 for ultra-fast FPS)
        :return: List of Detection objects
        """
        if self.model is None:
            raise RuntimeError("YOLO model is not initialized.")

        conf = confidence_threshold if confidence_threshold is not None else self.confidence_threshold

        kwargs: Dict[str, Any] = {
            "source": frame,
            "conf": conf,
            "device": self.device,
            "verbose": False,
        }
        if imgsz:
            kwargs["imgsz"] = imgsz

        # Run inference using Ultralytics YOLO
        results = self.model.predict(**kwargs)

        detections: List[Detection] = []

        if not results:
            return detections

        result = results[0]
        boxes = result.boxes

        if boxes is None or len(boxes) == 0:
            return detections

        names = result.names

        for box in boxes:
            cls_id = int(box.cls[0].item())
            class_name = names.get(cls_id, f"class_{cls_id}")
            score = float(box.conf[0].item())
            coords = box.xyxy[0].tolist()

            det = Detection(
                class_id=cls_id,
                class_name=class_name,
                confidence=score,
                x1=coords[0],
                y1=coords[1],
                x2=coords[2],
                y2=coords[3]
            )
            detections.append(det)

        return detections

    def get_classes(self) -> Dict[int, str]:
        """Return class mapping dictionary (class_id -> class_name)."""
        if self.model and hasattr(self.model, "names"):
            return self.model.names
        return {}
