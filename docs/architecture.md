# RoadVision — System Architecture

## Application Type
**Local Web Application** — runs entirely on the local machine, accessed via browser at `http://localhost:5000`.

No cloud inference. No external API calls. All CV processing stays in the Python backend.

---

## Full System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         BROWSER                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  HTML / CSS / JavaScript Dashboard                       │  │
│  │  (app/templates/ + app/static/)                          │  │
│  │                                                           │  │
│  │   Video Frame Panel   │   Road Scene Summary Sidebar     │  │
│  │   + Controls          │   + Alerts + Chart               │  │
│  └───────────────────────────────────────────────────────────┘  │
└──────────────────────────┬──────────────────────────────────────┘
                           │  HTTP (REST API / polling)
                           │  GET /api/frame
                           │  GET /api/summary
                           │  POST /api/upload
                           │  POST /api/process/start
                           │  POST /api/process/stop
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FLASK BACKEND                                 │
│             http://localhost:5000                                │
│                                                                  │
│  app/routes/main.py   → Page routes (GET /)                    │
│  app/routes/api.py    → REST API routes                        │
└──────────────────────────┬──────────────────────────────────────┘
                           │  Python function calls
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│              PYTHON CV PIPELINE  (src/)                         │
│                                                                  │
│  Uploaded Video File                                            │
│       │                                                         │
│       ▼                                                         │
│  ┌─────────────────┐                                            │
│  │ M1: Frame Handler│  OpenCV VideoCapture                      │
│  └────────┬────────┘                                            │
│           ▼                                                     │
│  ┌─────────────────┐                                            │
│  │ M2: YOLO Detect │  Custom-trained model (models/*.pt)        │
│  └────────┬────────┘                                            │
│           ▼                                                     │
│  ┌─────────────────┐                                            │
│  │  M3: Tracker    │  IoU/centroid lightweight                  │
│  └────────┬────────┘                                            │
│    ┌──────┴───────────────────────────────┐                     │
│    ▼         ▼             ▼              ▼                     │
│ ┌──────┐ ┌──────┐    ┌──────────┐  ┌──────────┐               │
│ │  M4  │ │  M5  │    │    M6    │  │    M8    │               │
│ │Count │ │ Zone │    │  Motion  │  │  Danger  │               │
│ │Categ.│ │Anlyz.│    │  Classif.│  │   Zone   │               │
│ └──┬───┘ └──┬───┘    └────┬─────┘  └────┬─────┘               │
│    └────────┴──────┬───────┘             │                      │
│                    ▼                      │                      │
│           ┌─────────────────┐             │                      │
│           │ M7: Density     │             │                      │
│           └────────┬────────┘             │                      │
│                    └─────────┬────────────┘                      │
│                              ▼                                   │
│                     ┌─────────────────┐                          │
│                     │ M9: Alerts      │                          │
│                     └────────┬────────┘                          │
│                              ▼                                   │
│                     ┌─────────────────┐                          │
│                     │ M10: Summary    │ → JSON dict              │
│                     └────────┬────────┘                          │
│                              │                                   │
│            Annotated Frame (base64 JPEG) + Summary (JSON)       │
└──────────────────────────────┼──────────────────────────────────┘
                               │
                    (back to Flask → browser)
```

---

## REST API Contract

| Method | Endpoint | Request | Response |
|--------|----------|---------|----------|
| `GET` | `/` | — | Dashboard HTML page |
| `POST` | `/api/upload` | `multipart/form-data` video file | `{ status, filename }` |
| `POST` | `/api/process/start` | — | `{ status: "started" }` |
| `POST` | `/api/process/stop` | — | `{ status: "stopped" }` |
| `GET` | `/api/frame` | — | `{ frame: "<base64 JPEG>", frame_index }` |
| `GET` | `/api/summary` | — | Full scene summary JSON |
| `GET` | `/api/status` | — | `{ running, video_loaded, frame_count }` |

---

## Module Dependency Table

| Module | Depends On | Output Used By |
|--------|-----------|----------------|
| M1 Frame Handler | Video file (uploaded via `/api/upload`) | M2 |
| M2 YOLO Detector | M1, model weights | M3 |
| M3 Tracker | M2 | M4, M5, M6, M8 |
| M4 Categorizer | M3 | M7, M9, M10 |
| M5 Zone Analyzer | M3 | M9, M10, API response |
| M6 Motion Classifier | M3 (+ history) | M9, M10 |
| M7 Density Estimator | M4 | M9, M10 |
| M8 Danger Zone | M3 | M9, M10 |
| M9 Alert Generator | M4, M5, M6, M7, M8 | M10 |
| M10 Scene Summary | M4–M9 | `/api/summary` endpoint |
| Flask API | M10 + annotated frame | Browser JS |
| Browser JS (dashboard.js) | Flask API | User (renders dashboard) |

---

## Technology Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | HTML5, CSS3, JavaScript (ES6+) |
| **UI Framework** | Bootstrap 5 |
| **Charts** | Chart.js |
| **Backend** | Python + Flask |
| **Object Detection** | YOLO (Ultralytics) — custom trained |
| **Video Processing** | OpenCV (`cv2`) |
| **Object Tracking** | IoU/centroid tracker (custom lightweight) |
| **Scene Analysis** | Pure Python rule-based logic |
| **Configuration** | YAML (`config/config.yaml`) |
| **Training** | Google Colab (GPU) — separate from app |

---

## Training vs. Application Separation

```
┌──────────────────────────────────┐
│   GOOGLE COLAB (training only)  │
│   training/notebooks/            │
│   → Dataset → Train → Export     │
│   → best.pt                      │
└─────────────────┬────────────────┘
                  │  models/roadvision_best.pt
                  ▼
┌──────────────────────────────────┐
│   LOCAL MACHINE (inference)     │
│   python run.py                  │
│   → http://localhost:5000        │
│   Flask + src/ + models/         │
└──────────────────────────────────┘
```

---

## Directory Responsibility Map

```
app/                → Flask web app (routes, templates, static files)
src/                → CV pipeline modules (all inference logic)
training/           → Colab training notebooks + scripts
data/               → Datasets (git-ignored) + uploaded videos
models/             → Trained YOLO weights (git-ignored)
config/config.yaml  → All tuneable parameters
docs/               → Documentation
tests/              → Unit + integration tests
run.py              → Start the Flask web server
```
