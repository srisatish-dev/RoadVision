# Models Directory — RoadVision

Place trained model weight files here after exporting from Google Colab.

---

## Expected File

```
models/
└── roadvision_best.pt       # Final trained YOLO model weights
```

---

## How to Obtain

1. Complete training in Google Colab (`training/notebooks/RoadVision_Train.ipynb`)
2. The best checkpoint will be saved as `runs/detect/train/weights/best.pt` in Colab
3. Download it and rename to `roadvision_best.pt`
4. Place it in this directory

---

## Notes

- Model weight files (`*.pt`, `*.onnx`, `*.engine`) are **git-ignored**.
- Update `config/config.yaml → model.weights_path` to point to the model file.
- The training strategy (pretrained init vs. from scratch) is TBD.
