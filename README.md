# RoadVision 🚗

**Context-Aware Road Scene Intelligence using YOLO**

> *From object detection to context-aware road-scene understanding.*

---

## Overview

RoadVision is a computer-vision system built for the **VisionX Hackathon** that processes
driving footage and goes beyond basic object detection by adding spatial, temporal, and
contextual analysis on top of a YOLO-based detector.

The system detects vehicles, pedestrians, road infrastructure, and road hazards — then
applies lightweight rule-based analysis to provide:

- **Object tracking** with temporary IDs
- **Object counting & categorization** (Vehicles / Road Users / Infrastructure / Road Hazards)
- **Road-zone awareness** (LEFT | CENTER | RIGHT × FAR | NEAR)
- **Moving vs. stationary classification**
- **Road-scene density** (LOW / MEDIUM / HIGH)
- **Danger-zone analysis** (predefined near-center region)
- **Contextual road alerts** (rule-based cautions)
- **Overall scene summary**
- **Live dashboard** (annotated video + sidebar)

---

## Core Pipeline

```
Driving Video
    ↓
Frame Processing
    ↓
YOLO Object Detection
    ↓
Object Tracking
    ↓
Count + Categorize
    ↓
Road-Zone Analysis
    ↓
Moving / Stationary Classification
    ↓
Scene Density Estimation
    ↓
Danger-Zone Analysis
    ↓
Contextual Alerts
    ↓
Overall Scene Summary
    ↓
Live Dashboard
```

---

## Detected Object Classes

### Vehicles
`car` · `bus` · `truck` · `motorcycle` · `bicycle` · `auto-rickshaw`

### Road Users
`person`

### Infrastructure
`traffic light` · `stop sign` · `road barrier`

### Road Hazards
`pothole` · `construction/road debris`

> **Note**: Standard classes (car, bus, truck, motorcycle, bicycle, person, traffic light,
> stop sign) may be available from a COCO-compatible YOLO model. Custom road-specific
> classes (auto-rickshaw, pothole, road barrier, construction debris) require custom
> training data and a dedicated training run.

---

## Project Structure

```
RoadVision/
├── src/                    # Application source code (inference + analysis)
│   ├── detector.py         # YOLO detector wrapper
│   ├── tracker.py          # Lightweight object tracker
│   ├── categorizer.py      # Object counter and categorizer
│   ├── zone_analyzer.py    # Road-zone (LEFT/CENTER/RIGHT × FAR/NEAR)
│   ├── motion_classifier.py# Moving / stationary classifier
│   ├── density_estimator.py# Scene density (LOW/MEDIUM/HIGH)
│   ├── danger_zone.py      # Danger-zone overlap analysis
│   ├── alert_generator.py  # Contextual alert rules
│   ├── scene_summary.py    # Scene summary composer
│   ├── dashboard.py        # Live dashboard renderer
│   └── utils.py            # Shared utilities
├── training/               # Training scripts and Colab notebooks
│   ├── notebooks/          # Google Colab training notebooks
│   ├── scripts/            # Dataset prep and training utility scripts
│   └── README.md           # Training workflow documentation
├── data/                   # Dataset directory (not committed)
│   ├── raw/                # Raw collected images/videos
│   ├── annotated/          # Annotated datasets (YOLO format)
│   └── splits/             # train / val / test splits
├── models/                 # Trained model weights (not committed)
│   └── README.md           # Model registry and notes
├── config/
│   └── config.yaml         # All configurable thresholds and parameters
├── docs/                   # Project documentation
│   ├── architecture.md     # System architecture notes
│   ├── dataset_guide.md    # Dataset sourcing and annotation guide
│   ├── training_guide.md   # Colab training workflow guide
│   └── feature_spec.md     # Detailed feature specifications
├── tests/                  # Unit and integration tests
├── pipeline.py             # Main application entry point
├── requirements.txt        # Python dependencies
├── .gitignore              # Git ignore rules
└── README.md               # This file
```

---

## Training vs. Application Split

| Concern | Location | Runs On |
|---------|----------|---------|
| Dataset prep | `training/scripts/` | Local / Colab |
| YOLO training | `training/notebooks/` | **Google Colab** |
| Model evaluation | `training/notebooks/` | **Google Colab** |
| Trained weights | `models/` | Exported from Colab |
| Inference pipeline | `src/` | **Local machine** |
| Dashboard | `src/dashboard.py` | **Local machine** |

---

## Quick Start (After Model is Available)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Place trained model in models/
#    e.g., models/roadvision_best.pt

# 3. Run on a video
python pipeline.py --video path/to/driving_footage.mp4
```

---

## Scope Boundaries

### ✅ Current Scope
Object detection · Object tracking · Counting · Categorization ·
Zone analysis · Motion classification · Density estimation ·
Danger-zone analysis · Contextual alerts · Scene summary · Live dashboard

### 🔮 Future Scope Only
Time-to-Conflict (TTC) · Pedestrian trajectory prediction ·
True depth/distance estimation · 3D scene understanding ·
Collision prediction · Autonomous vehicle control

### ❌ Explicitly Out of Scope
Accident prediction · Confirmed traffic-law violation detection ·
Exact distance measurement · Advanced dynamic risk prediction

---

## Hackathon
**VisionX** — One-Day Computer Vision Hackathon

---

## Acknowledgements

- Datasets, external libraries, and any pretrained components will be documented here
  once dataset and training strategy decisions are finalized.
