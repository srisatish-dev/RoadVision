# RoadVision — Project Report
### VisionX Hackathon | One-Day Computer Vision Challenge

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Problem Statement](#2-problem-statement)
3. [Proposed Solution](#3-proposed-solution)
4. [System Architecture](#4-system-architecture)
5. [Feature Modules](#5-feature-modules)
6. [Detection Classes](#6-detection-classes)
7. [Technical Stack](#7-technical-stack)
8. [Training Strategy](#8-training-strategy)
9. [Project Structure](#9-project-structure)
10. [Implementation Phases](#10-implementation-phases)
11. [Scope Boundaries](#11-scope-boundaries)
12. [Risks & Mitigations](#12-risks--mitigations)
13. [Acknowledgements](#13-acknowledgements)

---

## 1. Project Overview

| Field | Details |
|-------|---------|
| **Project Name** | RoadVision |
| **Project Title** | RoadVision — Context-Aware Road Scene Intelligence using YOLO |
| **Hackathon** | VisionX (One-Day Computer Vision Hackathon) |
| **Project Type** | Computer Vision / Road Scene Understanding |
| **Application Type** | Local Web Application (`http://localhost:5000`) |
| **Core Philosophy** | *From object detection to context-aware road-scene understanding* |

RoadVision is a computer vision system that processes driving footage and goes **beyond basic
object detection**. It applies lightweight spatial, temporal, and contextual analysis on top of
a YOLO-based detector to produce a rich understanding of road scenes in real time.

The system is delivered as a **local web application** — a Flask backend serves the CV pipeline,
and a browser-based dashboard visualises results. No internet connection or cloud APIs are required
during the demonstration.

---

## 2. Problem Statement

> *"The system should identify vehicles, pedestrians, road infrastructure, and other relevant
> road-scene objects from driving footage."*

Modern road scenes are complex — vehicles, pedestrians, traffic signals, road hazards, and
construction obstacles all interact simultaneously. Simple bounding-box detection is insufficient
for meaningful scene understanding.

RoadVision addresses this by enriching raw detections with:
- **Spatial context** (where is the object in the scene?)
- **Temporal context** (is the object moving or stationary?)
- **Scene-level context** (how dense is the scene? Is there a hazard nearby?)
- **Actionable output** (alerts, summary, dashboard)

---

## 3. Proposed Solution

```
Driving Footage
       ↓
Frame Processing
       ↓
YOLO Object Detection         ← custom-trained model
       ↓
Object Tracking               ← lightweight IoU/centroid tracker
       ↓
Count + Categorize            ← rule-based class grouping
       ↓
Road-Zone Analysis            ← image-space LEFT/CENTER/RIGHT × FAR/NEAR
       ↓
Moving / Stationary           ← frame-to-frame displacement threshold
       ↓
Scene Density                 ← configurable count/occupancy thresholds
       ↓
Danger-Zone Analysis          ← predefined near-center overlap check
       ↓
Contextual Alerts             ← rule-based caution strings
       ↓
Overall Scene Summary         ← structured aggregation of all above
       ↓
Live Dashboard                ← annotated video + sidebar panel
```

The system produces a **live dashboard** showing annotated driving footage alongside a
structured road-scene summary — all running locally, with no external API dependencies.

---

## 4. System Architecture

### Pipeline Flow

```
┌────────────────────────────────────────────────────────────────┐
│                        RoadVision Pipeline                     │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  [Video File]                                                  │
│       │                                                        │
│       ▼                                                        │
│  ┌─────────────────┐                                           │
│  │ M1: Frame Handler│  OpenCV VideoCapture                     │
│  └────────┬────────┘                                           │
│           │ frame (BGR numpy array)                            │
│           ▼                                                    │
│  ┌─────────────────┐                                           │
│  │ M2: YOLO Detect │  Custom-trained YOLO model               │
│  └────────┬────────┘  → [class, confidence, bbox]             │
│           │                                                    │
│           ▼                                                    │
│  ┌─────────────────┐                                           │
│  │  M3: Tracker    │  IoU/centroid lightweight tracking        │
│  └────────┬────────┘  → [track_id, class, bbox, centroid]     │
│           │                                                    │
│    ┌──────┴──────────────────────────────────┐                 │
│    ▼        ▼              ▼                 ▼                 │
│ ┌──────┐ ┌──────┐    ┌──────────┐    ┌──────────┐            │
│ │ M4   │ │  M5  │    │    M6    │    │    M8    │            │
│ │Count │ │ Zone │    │  Motion  │    │  Danger  │            │
│ │Categ.│ │Anlyz.│    │  Classif.│    │   Zone   │            │
│ └──┬───┘ └──┬───┘    └────┬─────┘    └────┬─────┘            │
│    │        │              │               │                   │
│    └────────┴──────┬───────┘               │                   │
│                    ▼                        │                   │
│           ┌─────────────────┐              │                   │
│           │ M7: Density Est.│              │                   │
│           └────────┬────────┘              │                   │
│                    │                        │                   │
│                    └────────────┬───────────┘                   │
│                                 ▼                               │
│                        ┌─────────────────┐                      │
│                        │ M9: Alert Gen.  │                      │
│                        └────────┬────────┘                      │
│                                 ▼                               │
│                        ┌─────────────────┐                      │
│                        │ M10: Scene Sum. │                      │
│                        └────────┬────────┘                      │
│                                 ▼                               │
│                        ┌─────────────────┐                      │
│                        │ M11: Dashboard  │  → OpenCV Window    │
│                        └─────────────────┘                      │
└────────────────────────────────────────────────────────────────┘
```

### Training vs. Application Separation

```
┌─────────────────────────────────────┐
│         GOOGLE COLAB                │
│  Dataset → Annotation → Training   │
│  → Evaluation → Export best.pt     │
└──────────────────┬──────────────────┘
                   │  best.pt
                   ▼
┌─────────────────────────────────────┐
│         LOCAL MACHINE               │
│  models/roadvision_best.pt          │
│  → pipeline.py → src/ modules       │
│  → Live Dashboard                   │
└─────────────────────────────────────┘
```

---

## 5. Feature Modules

### M1 — Frame Processing
Reads pre-recorded driving video files frame by frame using OpenCV.
Supports configurable frame-skip for performance tuning.

---

### M2 — YOLO Object Detection
The core detection engine. A custom-trained YOLO model detects all relevant road-scene
objects from each frame.

- **Input**: Raw video frame (numpy BGR array)
- **Output**: Detections — `[class_name, confidence, bounding_box (x1,y1,x2,y2)]`
- **Training**: Google Colab (strategy TBD — see §8)

---

### M3 — Object Tracking
Assigns and maintains temporary tracking IDs across consecutive frames.

- **Algorithm**: Lightweight IoU-based greedy association
- **IDs**: `Car #1`, `Person #2`, `Bike #1`, etc.
- **Scope**: Best-effort ID persistence; accepts occasional ID switches on heavy occlusion
- **Not used**: Kalman filtering, deep re-identification, optical flow

---

### M4 — Object Counting & Categorization
Groups detections into 4 top-level categories and counts them.

| Category | Classes |
|----------|---------|
| 🚗 Vehicles | car, bus, truck, motorcycle, bicycle, auto-rickshaw |
| 🚶 Road Users | person |
| 🚦 Infrastructure | traffic light, stop sign, road barrier |
| ⚠️ Road Hazards | pothole, construction debris |

**Example Output:**
```
Total Objects:  12
Vehicles:        8
Road Users:      2
Infrastructure:  1
Road Hazards:    1
```

---

### M5 — Road-Zone Analysis
Assigns each detected object an image-space zone based on its bounding-box centroid position.

```
┌──────────┬──────────┬──────────┐
│          │          │          │
│   LEFT   │  CENTER  │  RIGHT   │  ← FAR  (upper half)
│          │          │          │
├──────────┼──────────┼──────────┤
│          │          │          │
│   LEFT   │  CENTER  │  RIGHT   │  ← NEAR (lower half)
│          │          │          │
└──────────┴──────────┴──────────┘
```

**Example Output:**
```
Car  #1  →  CENTER / NEAR
Bike #2  →  RIGHT  / FAR
Person #1 → LEFT   / NEAR
```

> ⚠️ **Image-space positioning only. No real-world distance or depth is claimed.**

---

### M6 — Moving / Stationary Classification
Compares centroid positions of tracked objects across consecutive frames.

```
displacement > movement_threshold_px  →  Moving
displacement ≤ movement_threshold_px  →  Stationary
```

- Displacement averaged over configurable `smoothing_frames` to reduce jitter
- Threshold configurable in `config/config.yaml`
- **Not used**: Optical flow, trajectory prediction, Kalman smoothing

---

### M7 — Scene Density Estimation
Classifies the current road-scene density level.

```
Object Count < low_threshold          →  LOW
low_threshold ≤ Count < high_threshold →  MEDIUM
Object Count ≥ high_threshold         →  HIGH
```

Alternatively uses scene **occupancy ratio** (total bbox area / frame area).
Method and thresholds are configurable.

---

### M8 — Danger-Zone Analysis
Checks whether any relevant object enters a predefined near-center danger region.

```
┌──────────────────────────────────┐
│                                  │
│           FAR ZONE               │
│                                  │
│      ┌──────────────────┐        │
│      │                  │        │
│      │   DANGER  ZONE   │        │
│      │  (center-near)   │        │
│      └──────────────────┘        │
└──────────────────────────────────┘
```

- Output: `ACTIVE` or `CLEAR`
- Trigger: object bbox overlaps danger rectangle by more than `overlap_threshold`

> ⚠️ **This is NOT collision prediction. It is a simple spatial proximity check.**

---

### M9 — Contextual Alert Generator
Produces rule-based contextual caution strings.

| Trigger Condition | Alert |
|-------------------|-------|
| Relevant object in danger zone | `CAUTION: Object inside danger zone` |
| Pothole / debris / barrier detected | `Potential road obstruction detected` |
| Traffic light + vehicle in CENTER/NEAR | `Potential signal-risk condition` |

> **Wording Policy**: All alerts use cautious language — *"Potential"*, *"Possible"*,
> *"CAUTION"*. No confirmed violations, collisions, or accidents are asserted.

---

### M10 — Scene Summary Composer
Aggregates all module outputs into a structured scene summary.

```
ROAD SCENE SUMMARY
──────────────────────────────
Total Objects:   12

Vehicles:         8
Road Users:       2
Infrastructure:   1
Road Hazards:     1

Density:        MEDIUM

Moving:           7
Stationary:       5

Danger Zone:    ACTIVE

Alerts:
- Potential road obstruction detected
- CAUTION: Object inside danger zone
──────────────────────────────
```

---

### M11 — Live Dashboard
Renders the annotated video frame alongside the scene summary sidebar.

**Left Panel (Video)**:
- Bounding boxes colored by category
- Labels: `class | ID | confidence | zone`
- Semi-transparent danger zone overlay

**Right Panel (Sidebar)**:
- Real-time road scene summary
- Density indicator
- Motion counts
- Danger zone status
- Active alerts

---

## 6. Detection Classes

### Standard Classes (COCO-Compatible)

| Class | Category |
|-------|----------|
| car | Vehicles |
| bus | Vehicles |
| truck | Vehicles |
| motorcycle | Vehicles |
| bicycle | Vehicles |
| person | Road Users |
| traffic light | Infrastructure |
| stop sign | Infrastructure |

### Custom Road-Specific Classes (Require Training Data)

| Class | Category | Notes |
|-------|----------|-------|
| auto-rickshaw | Vehicles | South Asian road-specific; not in COCO |
| road barrier | Infrastructure | Not reliably in COCO |
| pothole | Road Hazards | Not in COCO |
| construction debris | Road Hazards | Not in COCO |

> Custom classes require annotated datasets and a dedicated training run on Google Colab.

---

## 7. Technical Stack

| Component | Technology |
|-----------|-----------|
| Object Detection | YOLO (Ultralytics) — custom trained |
| Object Tracking | Lightweight IoU/centroid tracker |
| Video Processing | OpenCV (`cv2`) |
| Dashboard | OpenCV overlay (default) / Streamlit (optional) |
| Numerical Operations | NumPy |
| Configuration | YAML (`config/config.yaml`) |
| Training Environment | Google Colab (GPU) |
| Inference Environment | Local machine (CPU) |
| Language | Python 3.13+ |

> All inference runs **locally** with **no external API calls** and **no internet dependency**
> during demonstration.

---

## 8. Training Strategy

### Training Environment
- **Platform**: Google Colab
- **Hardware**: Colab-provided GPU (T4 / A100)
- **Local machine**: Used for inference only

### Pending Decision — Pretrained Weight Ruling

> ⚠️ **The pretrained-initialization ruling from VisionX organizers is pending.**
> The training strategy below depends on this ruling.

#### Scenario A — Pretrained Initialization Permitted
```
YOLO pretrained backbone (e.g., YOLOv8n / YOLOv8s)
    ↓
Custom annotated dataset (standard + custom classes)
    ↓
Fine-tuning / transfer learning
    ↓
Evaluation (mAP, precision, recall)
    ↓
Export best.pt
    ↓
Local inference
```
- Faster convergence; feasible in one day
- Higher accuracy expected

#### Scenario B — From-Scratch Training Required
```
YOLO with random weight initialization
    ↓
Larger combined dataset required
    ↓
Training from scratch (more epochs)
    ↓
Evaluation
    ↓
Export best.pt
    ↓
Local inference
```
- Slower convergence; more data needed
- Higher risk within one-day constraint

### Dataset Strategy (TBD)
Custom road-specific classes require annotated datasets.
Candidate open datasets under evaluation:
- **RDD2022** (Road Damage Detection Dataset)
- **Roboflow Universe** — Indian traffic / pothole datasets
- **Kaggle** — pothole detection datasets
- Custom image collection + annotation

> ⚠️ No datasets have been downloaded yet. Strategy will be confirmed before Phase 1.

---

## 9. Project Structure

```
RoadVision/
├── config/
│   └── config.yaml              ← All configurable parameters
│
├── src/                         ← Application (inference + analysis)
│   ├── detector.py              ← M2: YOLO detector wrapper
│   ├── tracker.py               ← M3: Lightweight object tracker
│   ├── categorizer.py           ← M4: Counter & categorizer
│   ├── zone_analyzer.py         ← M5: Road-zone analysis
│   ├── motion_classifier.py     ← M6: Moving/stationary classifier
│   ├── density_estimator.py     ← M7: Scene density
│   ├── danger_zone.py           ← M8: Danger-zone analysis
│   ├── alert_generator.py       ← M9: Contextual alert rules
│   ├── scene_summary.py         ← M10: Scene summary composer
│   ├── dashboard.py             ← M11: Live dashboard renderer
│   └── utils.py                 ← Shared utilities
│
├── training/                    ← Training workflow (Colab)
│   ├── notebooks/               ← Colab training notebooks
│   ├── scripts/
│   │   └── prepare_dataset.py   ← Dataset preparation
│   ├── requirements_training.txt
│   └── README.md
│
├── data/                        ← Datasets (git-ignored)
│   └── README.md
│
├── models/                      ← Trained model weights (git-ignored)
│   └── README.md
│
├── docs/                        ← Documentation
│   ├── architecture.md
│   ├── dataset_guide.md
│   ├── training_guide.md
│   └── feature_spec.md
│
├── tests/                       ← Unit & integration tests
├── pipeline.py                  ← Main application entry point
├── requirements.txt             ← App dependencies
├── .gitignore
└── README.md
```

---

## 10. Implementation Phases

| Phase | Title | Status | Description |
|-------|-------|--------|-------------|
| **Phase 0** | Project Setup | ✅ Complete | Directory structure, config, stubs, docs |
| **Phase 1** | Model & Training | ⏳ Pending | Dataset, Colab notebook, YOLO training |
| **Phase 2** | Core Pipeline | ⏳ Pending | Detector, tracker, categorizer, zone analyzer |
| **Phase 3** | Scene Analysis | ⏳ Pending | Motion, density, danger zone, alerts |
| **Phase 4** | Dashboard | ⏳ Pending | OpenCV dashboard, scene summary |
| **Phase 5** | Integration & Demo | ⏳ Pending | End-to-end testing, demo preparation |

---

## 11. Scope Boundaries

### ✅ Current Implemented Scope
- YOLO object detection (custom-trained)
- Object tracking with temporary IDs
- Object counting (total + per-category)
- Object categorization (4 groups)
- Road-zone analysis (LEFT/CENTER/RIGHT × FAR/NEAR)
- Moving / stationary classification
- Scene density (LOW / MEDIUM / HIGH)
- Danger-zone analysis (predefined spatial region)
- Contextual alerts (rule-based cautions)
- Overall scene summary
- Live dashboard (annotated video + sidebar)

### 🔮 Future Scope Only
- Time-to-Conflict (TTC) estimation
- Pedestrian trajectory prediction
- True depth / distance estimation
- 3D scene understanding
- Larger road-hazard datasets
- More robust real-world deployment

### ❌ Explicitly Out of Scope
- Accident prediction
- Collision prediction
- Autonomous vehicle control
- Exact distance measurement
- Full 3D scene understanding
- Advanced trajectory prediction
- Complex dynamic risk prediction
- Confirmed traffic-law violation detection

---

## 12. Risks & Mitigations

| Risk | Severity | Mitigation |
|------|----------|------------|
| Pretrained weights not permitted | 🔴 High | Investigate from-scratch YOLO training; reduce custom class scope if needed |
| Custom dataset not available | 🔴 High | Evaluate open datasets (RDD2022, Roboflow); prepare to collect + annotate |
| Training time exceeds hackathon window | 🔴 High | Use Colab GPU; use smallest YOLO variant (nano/small); reduce epochs if needed |
| Inference FPS too low on local CPU | 🟡 Medium | Frame-skip; YOLO nano variant; resize frames |
| Tracker ID switching on occlusion | 🟡 Medium | Document as known limitation; lightweight trackers inherently imperfect |
| Dashboard rendering overhead | 🟡 Medium | Pre-compute text; lightweight OpenCV overlay |
| Zone boundaries misaligned with road | 🟡 Medium | Make boundaries configurable; allow tuning per video |
| Rule-based modules (M4–M11) | 🟢 Low | Fully deterministic; independently testable; no training required |

---

## 13. Acknowledgements

> This section will be updated once datasets, external libraries, and any pretrained
> components are finalized and confirmed.

### Libraries (Planned)
- [Ultralytics YOLO](https://github.com/ultralytics/ultralytics) — YOLO framework
- [OpenCV](https://opencv.org/) — Video processing and dashboard rendering
- [NumPy](https://numpy.org/) — Numerical operations

### Datasets (TBD)
- Dataset sources and licenses will be documented here once confirmed.

### Hackathon
- **VisionX** — One-Day Computer Vision Hackathon

---

*Report generated: September 18, 2026 — Phase 0 Complete*
*RoadVision © VisionX Hackathon Team*
