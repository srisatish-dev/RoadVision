# Feature Specifications — RoadVision

Detailed spec for each feature in the current scope.

---

## F1 — YOLO Road-Scene Object Detection

**Input**: Video frame (numpy array, BGR)
**Output**: List of detections `[{class, confidence, bbox}]`

### Detected Classes

| Category | Classes |
|----------|---------|
| Vehicles | car, bus, truck, motorcycle, bicycle, auto-rickshaw |
| Road Users | person |
| Infrastructure | traffic light, stop sign, road barrier |
| Road Hazards | pothole, construction debris |

**Source**: Custom-trained YOLO model (training TBD)

---

## F2 — Object Tracking

**Input**: Per-frame detections
**Output**: Tracked objects with persistent IDs `Car #1, Person #2, ...`

**Algorithm**: Lightweight IoU-based greedy assignment
**Scope**: Temporary IDs, best-effort across occlusion
**Not implemented**: Kalman filter, deep re-identification, optical flow

---

## F3 — Object Counting

**Input**: Tracked objects list
**Output**:
```
Total Objects: 12
Vehicles: 8
Road Users: 2
Infrastructure: 1
Road Hazards: 1
```

---

## F4 — Object Categorization

**Mapping**:
```
car, bus, truck, motorcycle, bicycle, auto-rickshaw → VEHICLES
person → ROAD USERS
traffic light, stop sign, road barrier → INFRASTRUCTURE
pothole, construction debris → ROAD HAZARDS
```

---

## F5 — Road-Zone Analysis

**Zones**:
- Horizontal: `LEFT | CENTER | RIGHT` (frame thirds by centroid x)
- Vertical: `FAR | NEAR` (frame halves by centroid y)

**Output per object**: `Car #1 → CENTER / NEAR`

**Important**: Image-space only. No real-world distance claimed.

---

## F6 — Moving / Stationary Classification

**Algorithm**: Compare centroid displacement over smoothing_frames frames.
- `displacement > movement_threshold_px` → **Moving**
- Otherwise → **Stationary**

**Not used**: Optical flow, trajectory prediction

---

## F7 — Scene Density

**Output**: `LOW | MEDIUM | HIGH`

**Default algorithm** (count-based):
- `< low_threshold` → LOW
- `low_threshold ≤ count < high_threshold` → MEDIUM
- `≥ high_threshold` → HIGH

All thresholds configurable in `config/config.yaml`.

---

## F8 — Danger-Zone Analysis

**Danger Zone**: Predefined rectangle, default = center-bottom 50% × center 50% of frame.

**Trigger**: Object bbox overlaps danger zone by > `overlap_threshold`

**Output**: `ACTIVE` or `CLEAR` + list of objects in zone

**Not implemented**: Collision prediction, TTC, exact distance

---

## F9 — Contextual Alerts

**Rules**:

| Trigger | Alert |
|---------|-------|
| Relevant object in danger zone | "CAUTION: Object inside danger zone" |
| Pothole / debris / barrier detected | "Potential road obstruction detected" |
| Traffic light + vehicle in CENTER/NEAR | "Potential signal-risk condition" |

**Wording policy**: Always use "Potential", "Possible", "CAUTION".
Never claim confirmed violations, collisions, or accidents.

---

## F10 — Scene Summary

**Output structure**:
```
ROAD SCENE SUMMARY
Total Objects: XX
Vehicles: XX | Road Users: XX | Infrastructure: XX | Road Hazards: XX
Density: LOW / MEDIUM / HIGH
Moving: XX | Stationary: XX
Danger Zone: ACTIVE / CLEAR
Alerts: [list]
```

---

## F11 — Live Dashboard

**Layout**:
- Left: Annotated video frame (bboxes, labels, IDs, zones)
- Right: Scene Summary sidebar

**Rendering**: OpenCV overlay (default) or Streamlit (optional)

---

## Out of Scope

- Accident prediction
- Collision prediction
- TTC (Time-to-Collision)
- Autonomous vehicle control
- Exact distance measurement
- 3D scene understanding
- Trajectory prediction
- Confirmed traffic-law violation detection
