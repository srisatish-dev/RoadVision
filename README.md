# RoadVision 🚗

**Context-Aware Road Scene Intelligence using YOLO**

> *From object detection to context-aware road-scene understanding.*

---

## Overview

RoadVision is a computer-vision system built for the **VisionX Hackathon** that processes driving footage using YOLO object detection and lightweight spatial, temporal, and contextual scene-analysis techniques.

Phase 2A delivers the **YOLO Road-Scene Video Detection Prototype**, a clean and modular video-processing pipeline that processes input road videos through a pretrained YOLO model, visualizes object detections (bounding boxes, class labels, confidence scores), and exports the processed output video.

---

## Architecture

The core video detection pipeline is designed to be fully modular and decoupled from the CLI and web interface:

```
[ Input Video ]
       │
       ▼
┌─────────────────────────────────────────┐
│            VideoProcessor               │
│  • Validates input format & specs       │
│  • Manages OpenCV VideoCapture & Writer │
└────────────────────┬────────────────────┘
                     │  Per-frame (numpy BGR image)
                     ▼
┌─────────────────────────────────────────┐
│             YOLODetector                │
│  • Loads YOLO model (once)              │
│  • Performs inference on device         │
│  • Returns structured Detection objects │
└────────────────────┬────────────────────┘
                     │  List of Detection objects
                     ▼
┌─────────────────────────────────────────┐
│         Visualization & Output          │
│  • Renders bounding boxes & labels      │
│  • Writes frame to output video file    │
│  • Accumulates detection statistics     │
└────────────────────┬────────────────────┘
                     │
                     ▼
[ Processed Output Video + Statistics Summary ]
```

---

## Setup

### 1. Prerequisites
- Python 3.10+ (tested on Python 3.13)
- PyTorch (CPU or CUDA GPU)

### 2. Install Dependencies
Install all required packages from `requirements.txt`:

```bash
pip install -r requirements.txt
```

This installs:
- `ultralytics` (YOLO framework)
- `opencv-python` (video processing & rendering)
- `Flask` & `Flask-CORS` (local web application)
- `PyYAML` (configuration management)

---

## Running the Prototype

### Option A — Command Line Interface (CLI)

Run the video detection prototype on a sample video:

```bash
# Basic run with default video
python src/main.py --input input/road_video.mp4

# Run via root pipeline script
python pipeline.py --video input/road_video.mp4

# Specify custom model, confidence threshold, and device
python src/main.py --input input/road_video.mp4 --model yolov8s.pt --confidence 0.30 --device cuda
```

### Option B — Web Interface Prototype

Launch the local web server:

```bash
python run.py
```

Then open your browser at `http://localhost:5000` to upload a video, start processing, and download the output.

---

## Output

Processed videos are saved automatically to the `output/` directory:

```
output/
└── road_video_detected.mp4
```

### Example Summary Output (CLI)

At the end of processing, a summary report is printed to the terminal:

```
============================================================
 RoadVision — Phase 2A Video Processing Summary
============================================================
Status:             SUCCESS
Input Video:        input/road_video.mp4
Output Video:       output/road_video_detected.mp4
Frames Processed:   300
Processing Time:    12.4s
Average FPS:        24.2 FPS
------------------------------------------------------------
Detections Summary (across all frames):
  • Car            : 240
  • Person         : 85
  • Motorcycle     : 42
  • Bus            : 12
Total Detections:   379
============================================================
```

---

## Configuration

All configurable parameters are centralized in `config/config.yaml`.

```yaml
# Model Configuration
model:
  weights_path: "yolov8n.pt"      # Model file or pretrained name (yolov8n.pt, yolov8s.pt, etc.)
  confidence_threshold: 0.25     # Detection confidence threshold (0.0 - 1.0)
  nms_iou_threshold: 0.45        # NMS IoU threshold
  device: "auto"                 # "cpu", "cuda", or "auto"

# Video Input & Output Configuration
video:
  default_input: "input/sample.mp4"
  input_dir: "input"
  output_dir: "output"
  frame_skip: 1                  # 1 = process every frame, 2 = process every 2nd frame
  max_width: 1280                # Max width for frame processing (None to keep original)
```

### Changing the Model
To change the YOLO model variant or use a custom fine-tuned weights file (e.g. after Colab training):
1. Update `config/config.yaml` → `model.weights_path: "models/roadvision_best.pt"`
2. Or pass via CLI: `python src/main.py --model models/roadvision_best.pt`

### Changing Confidence Threshold
- Edit `config/config.yaml` → `model.confidence_threshold: 0.30`
- Or pass via CLI: `python src/main.py --confidence 0.30`

---

## Current Detected Classes

Initially relies on pretrained COCO classes for road scenes:
- `car`, `bus`, `truck`, `motorcycle`, `bicycle`, `person`, `traffic light`, `stop sign`

> **Note**: Fine-tuning for custom classes (`pothole`, `road barrier`, `auto-rickshaw`, `road debris`) will be performed in Phase 2B on Google Colab without requiring changes to the core `VideoProcessor` pipeline.

---

## Project Structure

```
RoadVision/
├── config/
│   └── config.yaml              # Central configuration file
├── src/
│   ├── detector.py              # YOLODetector abstraction module
│   ├── video_processor.py       # VideoProcessor engine & renderer
│   └── main.py                  # CLI entry point & summary reporter
├── app/                         # Flask web application layer
│   ├── routes/                  # REST API & page routes
│   ├── static/                  # CSS & JS frontend assets
│   └── templates/               # HTML templates
├── input/                       # Input videos directory
├── output/                      # Processed output videos directory
├── models/                      # Fine-tuned model weights directory
├── scripts/
│   └── generate_sample_video.py # Synthetic test video generator
├── pipeline.py                  # Root CLI wrapper
├── run.py                       # Root web server launcher
├── requirements.txt             # Python dependencies
└── README.md                    # Project documentation
```

---

## Hackathon
**VisionX** — One-Day Computer Vision Hackathon
