# Dataset Guide — RoadVision

> **Status**: Dataset strategy TBD. Do NOT download anything yet.

---

## Required Classes

### Standard Classes (COCO-compatible)
These classes are commonly available in COCO-trained YOLO models.
They may still need to be included in our training split depending on
the final pretrained-weight ruling.

| Class | COCO Name |
|-------|-----------|
| Car | car |
| Bus | bus |
| Truck | truck |
| Motorcycle | motorcycle |
| Bicycle | bicycle |
| Person | person |
| Traffic Light | traffic light |
| Stop Sign | stop sign |

### Custom Road-Specific Classes
These classes require dedicated annotated datasets and custom training.

| Class | Notes |
|-------|-------|
| **Auto-rickshaw** | South Asian road-specific; not in COCO |
| **Pothole** | Road hazard; not in COCO |
| **Road Barrier** | Road infrastructure; not reliably in COCO |
| **Construction Debris** | Road hazard; not in COCO |

---

## Candidate Datasets (To Evaluate — NOT Downloaded)

| Dataset | Classes | License | Notes |
|---------|---------|---------|-------|
| RDD2022 (Road Damage Detection) | Road damage/potholes | Research | Multi-country |
| Roboflow Universe — Pothole | Pothole | Varies | Check license |
| Roboflow Universe — Indian Traffic | Auto-rickshaw, vehicles | Varies | Check license |
| Kaggle Pothole Detection | Pothole | Public | Check license |
| Custom collection | All custom | Own | Annotation required |

---

## Annotation Format

YOLO format (one `.txt` per image):
```
class_id  x_center  y_center  width  height
```
All values normalized to [0, 1] relative to image width/height.

Recommended annotation tools:
- **LabelImg** (offline, free)
- **Roboflow** (online, freemium)
- **CVAT** (online, open source)

---

## Dataset Split Recommendation

| Split | Ratio | Purpose |
|-------|-------|---------|
| Train | 70–80% | Model training |
| Val | 10–15% | Hyperparameter tuning / early stopping |
| Test | 10–15% | Final evaluation (held out) |

---

## YOLO Dataset YAML Template

```yaml
# data/dataset.yaml — fill in after dataset is confirmed
path: ../data/annotated
train: images/train
val: images/val
test: images/test

nc: 12   # number of classes
names:
  0: car
  1: bus
  2: truck
  3: motorcycle
  4: bicycle
  5: auto-rickshaw
  6: person
  7: traffic light
  8: stop sign
  9: road barrier
  10: pothole
  11: construction debris
```

---

## Acknowledgement Requirement

All datasets used must be properly documented and credited in `README.md`
and any hackathon submission materials.
