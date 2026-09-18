"""
RoadVision — Module: Object Tracker (M3)
=========================================
Assigns and maintains temporary tracking IDs across consecutive frames using a
lightweight IoU & centroid-based tracking approach.

Ensures that:
1. Physical objects maintain a persistent track ID (e.g., Car #1, Car #2).
2. Unique physical object counts are tracked (e.g., 10 unique cars, not 1000 per-frame detections).
"""

import math
import logging
from typing import List, Dict, Tuple, Any, Optional
import numpy as np

from src.detector import Detection

logger = logging.getLogger(__name__)


class TrackedObject:
    """Represents a single tracked physical object across frames."""

    def __init__(self, track_id: int, detection: Detection):
        self.track_id = track_id
        self.class_id = detection.class_id
        self.class_name = detection.class_name
        self.confidence = detection.confidence
        self.x1 = detection.x1
        self.y1 = detection.y1
        self.x2 = detection.x2
        self.y2 = detection.y2
        self.centroid = detection.centroid
        self.missing_frames = 0
        self.total_frames_seen = 1
        self.history: List[Tuple[float, float]] = [self.centroid]

    def update(self, detection: Detection):
        """Update tracked object with new frame detection."""
        self.confidence = detection.confidence
        self.x1 = detection.x1
        self.y1 = detection.y1
        self.x2 = detection.x2
        self.y2 = detection.y2
        self.centroid = detection.centroid
        self.missing_frames = 0
        self.total_frames_seen += 1
        self.history.append(self.centroid)
        if len(self.history) > 30:  # Keep last 30 centroids for motion history
            self.history.pop(0)

    @property
    def bbox(self) -> Tuple[float, float, float, float]:
        return (self.x1, self.y1, self.x2, self.y2)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "track_id": self.track_id,
            "class_id": self.class_id,
            "class_name": self.class_name,
            "confidence": round(self.confidence, 2),
            "bbox": [round(self.x1, 1), round(self.y1, 1), round(self.x2, 1), round(self.y2, 1)],
            "centroid": (round(self.centroid[0], 1), round(self.centroid[1], 1)),
            "frames_seen": self.total_frames_seen
        }


def compute_iou(boxA: Tuple[float, float, float, float], boxB: Tuple[float, float, float, float]) -> float:
    """Compute Intersection over Union (IoU) between two bounding boxes."""
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])

    interArea = max(0.0, xB - xA) * max(0.0, yB - yA)
    boxAArea = max(0.0, boxA[2] - boxA[0]) * max(0.0, boxA[3] - boxA[1])
    boxBArea = max(0.0, boxB[2] - boxB[0]) * max(0.0, boxB[3] - boxB[1])

    unionArea = boxAArea + boxBArea - interArea
    if unionArea <= 0:
        return 0.0
    return interArea / unionArea


class ObjectTracker:
    """
    Lightweight Greedy Centroid & IoU Object Tracker.
    Maintains persistent IDs for physical objects across video frames.
    """

    def __init__(self, max_missing_frames: int = 15, max_distance_px: float = 100.0, min_iou: float = 0.20):
        self.max_missing_frames = max_missing_frames
        self.max_distance_px = max_distance_px
        self.min_iou = min_iou
        self.next_id = 1
        self.active_tracks: List[TrackedObject] = []
        # Unique physical object counters (class_name -> count of unique IDs)
        self.unique_counts_by_class: Dict[str, int] = {}
        # Set of tracked unique IDs seen per class to avoid double-counting
        self._tracked_ids_by_class: Dict[str, set] = {}

    def reset(self):
        """Reset tracking state for a new video."""
        self.next_id = 1
        self.active_tracks = []
        self.unique_counts_by_class = {}
        self._tracked_ids_by_class = {}

    def update(self, detections: List[Detection]) -> List[TrackedObject]:
        """
        Update tracker with new frame detections.

        :param detections: List of Detection objects from YOLO detector
        :return: List of active TrackedObject instances
        """
        # Increment missing frames counter for all existing active tracks
        for track in self.active_tracks:
            track.missing_frames += 1

        if not detections:
            # Remove tracks missing for too long
            self.active_tracks = [t for t in self.active_tracks if t.missing_frames <= self.max_missing_frames]
            return [t for t in self.active_tracks if t.missing_frames == 0]

        if not self.active_tracks:
            # First frame or no existing tracks: register all detections as new unique objects
            for det in detections:
                self._register_new_track(det)
            return self.active_tracks

        # Match existing active tracks with new detections of the same class
        matched_tracks = set()
        matched_detections = set()

        # Build association matrix (IoU / Distance)
        candidates = []
        for t_idx, track in enumerate(self.active_tracks):
            for d_idx, det in enumerate(detections):
                # Only match same class
                if track.class_name.lower() != det.class_name.lower():
                    continue

                iou = compute_iou(track.bbox, (det.x1, det.y1, det.x2, det.y2))
                dist = math.hypot(track.centroid[0] - det.centroid[0], track.centroid[1] - det.centroid[1])

                if iou >= self.min_iou or dist <= self.max_distance_px:
                    # Score combination (higher IoU / lower dist is better)
                    score = iou + (1.0 - min(1.0, dist / self.max_distance_px))
                    candidates.append((score, t_idx, d_idx))

        # Sort candidate matches by highest compatibility score first
        candidates.sort(key=lambda x: x[0], reverse=True)

        for score, t_idx, d_idx in candidates:
            if t_idx in matched_tracks or d_idx in matched_detections:
                continue

            # Update matched track
            self.active_tracks[t_idx].update(detections[d_idx])
            matched_tracks.add(t_idx)
            matched_detections.add(d_idx)

        # Register remaining unmatched detections as new physical objects
        for d_idx, det in enumerate(detections):
            if d_idx not in matched_detections:
                self._register_new_track(det)

        # Filter out tracks that have been missing for too long
        self.active_tracks = [t for t in self.active_tracks if t.missing_frames <= self.max_missing_frames]

        # Return currently visible tracks in this frame
        return [t for t in self.active_tracks if t.missing_frames == 0]

    def _register_new_track(self, det: Detection) -> TrackedObject:
        """Assign a new unique track ID to a newly discovered physical object."""
        track = TrackedObject(track_id=self.next_id, detection=det)
        self.next_id += 1
        self.active_tracks.append(track)

        cls = det.class_name.lower()
        if cls not in self._tracked_ids_by_class:
            self._tracked_ids_by_class[cls] = set()
        self._tracked_ids_by_class[cls].add(track.track_id)
        self.unique_counts_by_class[cls] = len(self._tracked_ids_by_class[cls])

        return track

    def get_unique_counts(self) -> Dict[str, int]:
        """Return dict of unique physical object counts per class."""
        return self.unique_counts_by_class.copy()

    def get_total_unique_objects(self) -> int:
        """Return total unique physical objects counted across all classes."""
        return sum(self.unique_counts_by_class.values())
