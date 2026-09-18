"""
RoadVision — Module: Object Tracker (M3)
=========================================
Responsibility:
    Assign and maintain temporary tracking IDs across consecutive frames
    using a lightweight centroid / IoU-based tracking approach.

Inputs:
    - Current frame detections (list of Detection objects)

Outputs:
    - List of TrackedObject objects:
        { track_id, class_name, confidence, bbox, centroid, age }

Algorithm (planned):
    - IoU-based greedy association between existing tracks and new detections
    - Tracks that go unmatched for > max_frames_missing frames are retired
    - New detections not matched to any track get a new track ID

NOTE: This file is a STUB. Implementation begins in Phase 1.
"""

# tracker.py — Placeholder
