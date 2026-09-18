# RoadVision — System Architecture

## Pipeline Overview

```
Driving Video (MP4)
       │
       ▼
┌─────────────────────┐
│  M1: Frame Handler  │  OpenCV VideoCapture; frame-skip support
└──────────┬──────────┘
           │  frame (numpy BGR array)
           ▼
┌─────────────────────┐
│  M2: YOLO Detector  │  Custom-trained YOLO model
│  (detector.py)      │  → detections: [class, confidence, bbox]
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  M3: Object Tracker │  IoU/centroid-based lightweight tracker
│  (tracker.py)       │  → tracked_objects: [..., track_id]
└──────────┬──────────┘
           │
    ┌──────┴──────────────────────────────────┐
    │              (parallel analysis)         │
    ▼              ▼              ▼            ▼
┌────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
│  M4    │  │   M5     │  │   M6     │  │   M8     │
│Counter │  │  Zone    │  │  Motion  │  │ Danger   │
│Categor.│  │Analyzer  │  │Classify  │  │  Zone    │
└───┬────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘
    │             │              │              │
    └──────┬──────┴──────────────┘              │
           │                                    │
           ▼                                    │
┌─────────────────────┐                         │
│  M7: Density Est.   │                         │
└──────────┬──────────┘                         │
           │                                    │
           ▼                                    │
┌─────────────────────────────────────────────────┐
│           M9: Alert Generator                   │
│   (M4 + M5 + M6 + M7 + M8 → alert strings)     │
└──────────┬──────────────────────────────────────┘
           │
           ▼
┌─────────────────────┐
│  M10: Scene Summary │  Aggregates all outputs → SceneSummary dict
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  M11: Dashboard     │  Annotated frame + sidebar panel → OpenCV window
└─────────────────────┘
```

## Module Dependency Table

| Module | Depends On | Output Used By |
|--------|-----------|----------------|
| M1 Frame Handler | Video file | M2 |
| M2 YOLO Detector | M1, model weights | M3 |
| M3 Tracker | M2 | M4, M5, M6, M8 |
| M4 Categorizer | M3 | M7, M9, M10 |
| M5 Zone Analyzer | M3 | M9, M10, M11 |
| M6 Motion Classifier | M3 (+ history) | M9, M10 |
| M7 Density Estimator | M4 | M9, M10 |
| M8 Danger Zone | M3 | M9, M10 |
| M9 Alert Generator | M4, M5, M6, M7, M8 | M10 |
| M10 Scene Summary | M4–M9 | M11 |
| M11 Dashboard | M2 (frame), M3, M10 | Output |

## Training vs. Application Separation

```
training/           ← All training code (runs on Colab)
src/                ← All inference + analysis code (runs locally)
models/             ← Trained weights (exported from Colab)
data/               ← Datasets (git-ignored)
config/config.yaml  ← Shared configuration
```
