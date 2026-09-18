"""
RoadVision — Sample Video Generator Script
===========================================
Generates a synthetic driving video for quick local testing when no real
driving footage is available.

Generates: input/sample_road_test.mp4 (5 seconds @ 30 FPS, 1280x720)
"""

import os
import cv2
import numpy as np


def generate_sample_video(output_path: str = "input/sample_road_test.mp4", duration_sec: int = 5, fps: int = 30):
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    width, height = 1280, 720
    total_frames = duration_sec * fps
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    if not writer.isOpened():
        raise RuntimeError(f"Could not open VideoWriter for '{output_path}'")

    print(f"Generating synthetic road test video: '{output_path}' ({total_frames} frames)...")

    for i in range(total_frames):
        # Create dark road background
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        frame[:] = (50, 50, 50)  # Grey road

        # Draw lane markers
        cv2.line(frame, (width // 3, 0), (width // 4, height), (255, 255, 255), 4)
        cv2.line(frame, (2 * width // 3, 0), (3 * width // 4, height), (255, 255, 255), 4)

        # Draw moving car (blue rectangle moving down center lane)
        car_y = int(100 + (i / total_frames) * (height - 250))
        car_x = int(width // 2 - 60)
        cv2.rectangle(frame, (car_x, car_y), (car_x + 120, car_y + 160), (255, 100, 0), -1)
        cv2.putText(frame, "TEST VEHICLE", (car_x + 10, car_y + 80), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        # Draw moving pedestrian (green circle moving across left side)
        ped_x = int(50 + (i / total_frames) * 300)
        ped_y = 450
        cv2.circle(frame, (ped_x, ped_y), 25, (0, 255, 0), -1)

        # Write frame
        writer.write(frame)

    writer.release()
    print(f"Successfully generated sample video at: '{output_path}'")


if __name__ == "__main__":
    generate_sample_video()
