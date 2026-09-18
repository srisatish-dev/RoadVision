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

## Application Type

**Local Web Application** — runs entirely on your machine, accessed in the browser at `http://localhost:5000`.
No cloud inference. No external APIs. All CV processing stays in the Python backend.

```
Browser (Dashboard UI)
    ↓  REST API
Flask Backend (Python)
    ↓  Python calls
CV Pipeline (src/)   ← YOLO + Tracking + Scene Analysis
    ↓
Flask → Browser Dashboard
```

---

## Project Structure

```
RoadVision/
├── app/                    # Flask web application
│   ├── routes/
│   │   ├── main.py         # Page routes  (GET /)
│   │   └── api.py          # REST API     (/api/*)
│   ├── static/
│   │   ├── css/dashboard.css
│   │   └── js/dashboard.js
│   └── templates/
│       ├── base.html
│       └── dashboard.html
├── src/                    # Python CV pipeline modules
│   ├── detector.py         # M2 — YOLO detector wrapper
│   ├── tracker.py          # M3 — Object tracker
│   ├── categorizer.py      # M4 — Counter + categorizer
│   ├── zone_analyzer.py    # M5 — Zone analysis
│   ├── motion_classifier.py# M6 — Moving/stationary
│   ├── density_estimator.py# M7 — Scene density
│   ├── danger_zone.py      # M8 — Danger-zone analysis
│   ├── alert_generator.py  # M9 — Contextual alerts
│   ├── scene_summary.py    # M10 — Scene summary
│   └── utils.py            # Shared utilities
├── training/               # Google Colab training workflow
│   ├── notebooks/          # Colab training notebooks
│   └── scripts/            # Dataset preparation scripts
├── data/                   # Datasets + uploaded videos (git-ignored)
├── models/                 # Trained YOLO weights (git-ignored)
├── config/config.yaml      # All configurable parameters
├── docs/                   # Documentation
├── tests/                  # Unit + integration tests
├── run.py                  # Flask application entry point
├── requirements.txt        # Python dependencies
└── README.md
```

---

## Training vs. Application Split

| Concern | Location | Runs On |
|---------|----------|---------|
| Dataset prep | `training/scripts/` | Local / Colab |
| YOLO training | `training/notebooks/` | **Google Colab** |
| Model evaluation | `training/notebooks/` | **Google Colab** |
| Trained weights | `models/` | Exported from Colab |
| CV pipeline | `src/` | **Local machine** |
| Flask backend | `app/` | **Local machine** |
| Web dashboard | `app/templates/` + `app/static/` | **Browser** |

---

## Quick Start (After Model is Available)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Place trained model in models/
#    e.g., models/roadvision_best.pt

# 3. Start the web server
python run.py

# 4. Open in browser
#    http://localhost:5000

# 5. Upload driving video → click ▶ Start
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
