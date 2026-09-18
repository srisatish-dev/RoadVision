# Data Directory — RoadVision

This directory holds datasets used for training the custom YOLO model.

> ⚠️ **Raw data, annotations, and video files are git-ignored.**
> Only README and placeholder files are tracked.

---

## Structure

```
data/
├── raw/                    # Raw collected images/videos (git-ignored)
├── annotated/              # Annotated datasets in YOLO format (git-ignored)
│   ├── images/
│   │   ├── train/
│   │   ├── val/
│   │   └── test/
│   └── labels/
│       ├── train/
│       ├── val/
│       └── test/
├── splits/                 # Train/val/test split manifests (git-ignored)
├── sample_footage/         # Sample driving video for testing (git-ignored)
└── README.md               # This file
```

---

## Dataset Strategy (TBD)

Custom road-specific classes that require annotated data:

| Class | Status |
|-------|--------|
| Auto-rickshaw | ⏳ Dataset TBD |
| Pothole | ⏳ Dataset TBD |
| Road Barrier | ⏳ Dataset TBD |
| Construction Debris | ⏳ Dataset TBD |

Candidate open datasets to evaluate:
- RDD2022 (Road Damage Detection)
- Kaggle pothole datasets
- Roboflow Universe (Indian road scenes)
- Custom collection + annotation

**Do NOT download any datasets until the strategy is confirmed.**

---

## YOLO Dataset YAML (to be generated)

Once the dataset is prepared, a `dataset.yaml` file will be generated here:

```yaml
# data/dataset.yaml (example — not final)
path: data/annotated
train: images/train
val: images/val
test: images/test

nc: 12
names:
  - car
  - bus
  - truck
  - motorcycle
  - bicycle
  - auto-rickshaw
  - person
  - traffic light
  - stop sign
  - road barrier
  - pothole
  - construction debris
```
