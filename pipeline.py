"""
RoadVision — Main Pipeline Entry Point (Phase 2A)
=================================================
Usage:
    python pipeline.py --video input/sample_road.mp4
    python pipeline.py --video input/sample_road.mp4 --confidence 0.30

Pipeline:
    Input Video -> Frame Extraction -> YOLO Object Detection ->
    Annotated Visualizations -> Processed Output Video
"""

import sys
import os

# Redirect execution to src.main
from src.main import main

if __name__ == "__main__":
    main()
