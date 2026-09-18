"""
RoadVision — Module: Contextual Alert Generator (M9)
=====================================================
Responsibility:
    Generate simple, rule-based contextual road alerts based on the
    combined outputs of the detection, zone, motion, and danger-zone modules.

Inputs:
    - List of TrackedObject objects (with class, zone, motion_state)
    - Danger-zone analysis result
    - Config (alert wording, enabled alert categories)

Outputs:
    - alerts: list of alert strings

Alert Rules (planned):
    Rule 1 — Danger Zone Alert:
        IF object in danger zone AND class in danger_zone_relevant_classes
        → "CAUTION: Object inside danger zone"

    Rule 2 — Road Hazard Alert:
        IF class in hazard_classes (pothole / debris / barrier)
        → "Potential road obstruction detected"

    Rule 3 — Signal Risk Alert:
        IF traffic light detected AND vehicle detected in CENTER/NEAR zone
        → "Potential signal-risk condition"

IMPORTANT WORDING POLICY:
    All alerts must use cautious, non-definitive language:
    - "Potential", "Possible", "CAUTION"
    - Do NOT claim confirmed traffic violations.
    - Do NOT claim collision prediction.
    - Do NOT claim accident prediction.

NOTE: This file is a STUB. Implementation begins in Phase 1.
"""

# alert_generator.py — Placeholder
