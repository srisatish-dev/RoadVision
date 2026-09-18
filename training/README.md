# Training Directory — RoadVision

This directory contains everything related to **model training**.

Training is performed on **Google Colab**, not on the local machine.

---

## Structure

```
training/
├── notebooks/              # Google Colab training notebooks
│   └── RoadVision_Train.ipynb   (to be created in Phase 1)
├── scripts/                # Dataset preparation and utility scripts
│   └── prepare_dataset.py       (to be created in Phase 1)
├── requirements_training.txt    # Colab-specific training dependencies
└── README.md               # This file
```

---

## Workflow

```
Google Colab
    ↓
Mount Google Drive / Upload Dataset
    ↓
Install training dependencies (requirements_training.txt)
    ↓
Run YOLO training (notebooks/RoadVision_Train.ipynb)
    ↓
Evaluate model (mAP, precision, recall)
    ↓
Export best.pt
    ↓
Download to local: models/roadvision_best.pt
    ↓
Run local inference via pipeline.py
```

---

## Important Notes

- **Do NOT run training locally.** The local machine is used for inference only.
- **Pretrained initialization strategy** must be confirmed before training starts.
- **Dataset strategy** must be confirmed before training starts.
- Training outputs (runs/, weights/) are git-ignored.
