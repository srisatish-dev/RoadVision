# Training Guide — RoadVision (Google Colab)

> **Status**: Training strategy TBD (pretrained init ruling pending).
> This guide describes the planned workflow. Do NOT execute yet.

---

## Overview

All model training runs on **Google Colab**, not on the local machine.

The local machine is used only for inference after the trained model is exported.

---

## Training Scenarios

### Scenario A — Pretrained Initialization Permitted (Transfer Learning)

```
Colab
  ↓
Load YOLO pretrained backbone (e.g., yolov8n.pt / yolov8s.pt)
  ↓
Load custom dataset (data/dataset.yaml)
  ↓
Fine-tune on combined dataset (standard + custom classes)
  ↓
Evaluate: mAP, precision, recall per class
  ↓
Export best.pt
  ↓
Download → models/roadvision_best.pt
```

### Scenario B — From-Scratch Training Required

```
Colab
  ↓
Initialize YOLO with random weights
  ↓
Load combined dataset (larger dataset needed)
  ↓
Train from scratch (more epochs, more data required)
  ↓
Evaluate: mAP, precision, recall per class
  ↓
Export best.pt
  ↓
Download → models/roadvision_best.pt
```

---

## Colab Notebook Plan

The notebook `training/notebooks/RoadVision_Train.ipynb` will cover:

1. Environment setup (install ultralytics, dependencies)
2. Mount Google Drive / upload dataset
3. Dataset validation (check annotations, class distribution)
4. Training configuration (epochs, batch size, image size)
5. Training run
6. Evaluation (confusion matrix, mAP curves)
7. Export best model

---

## Key Training Hyperparameters (Planned)

| Parameter | Planned Value | Notes |
|-----------|--------------|-------|
| Model variant | yolov8n / yolov8s | Nano or small for speed |
| Epochs | 50–100 | Adjust based on convergence |
| Batch size | 16–32 | Colab GPU dependent |
| Image size | 640 | Standard YOLO input |
| Optimizer | AdamW | Default Ultralytics |
| Learning rate | Auto | Ultralytics default scheduler |

---

## Evaluation Metrics

- **mAP@0.5** — primary accuracy metric
- **Precision** — per class
- **Recall** — per class
- **Inference speed** — FPS on local CPU

---

## Export

After training, export the best checkpoint:

```python
# In Colab notebook
model = YOLO("runs/detect/train/weights/best.pt")
# Download best.pt to local machine
```

Place the downloaded file at:
```
models/roadvision_best.pt
```

Update `config/config.yaml`:
```yaml
model:
  weights_path: "models/roadvision_best.pt"
```

---

## Important Rules

- Training computation stays on Colab.
- Do NOT run training on the local machine.
- Pretrained initialization strategy must be confirmed before starting.
- Dataset must be confirmed and annotated before training.
