"""Processes a video file frame-by-frame: detects, OCRs, validates, saves
detections and produces an annotated output video."""
import os
import time
import cv2
import numpy as np
from ai.vehicle_plate_detector import detect_plates
from ai.ocr_engine import read_plate_text
from utils.validation import validate_plate
from utils.logger import logger


def _draw_detection(frame, bbox, plate_text, valid):
    x1, y1, x2, y2 = bbox
    color = (0, 200, 0) if valid else (0, 0, 220)
    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
    label = plate_text if plate_text else "..."
    cv2.putText(frame, label, (x1, max(y1 - 10, 15)), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
    return frame


def process_video(video_path: str, output_path: str, model, ocr_reader, detection_service,
                   frame_skip: int = 3, progress_callback=None) -> dict:
    """Runs the full pipeline over a video and writes an annotated output video.
    detection_service must expose .process_frame(frame, source='video') -> dict|None
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise IOError(f"Could not open video: {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS) or 20
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    frame_idx = 0
    saved_plates = []
    start_time = time.time()

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_idx % frame_skip == 0:
            result = detection_service.process_frame(frame, source="video")
            if result:
                for det in result.get("detections", []):
                    frame = _draw_detection(frame, det["bbox"], det["plate"], det["valid"])
                    if det["saved"]:
                        saved_plates.append(det["plate"])

        writer.write(frame)
        frame_idx += 1

        if progress_callback and total_frames:
            progress_callback(min(frame_idx / total_frames, 1.0))

    cap.release()
    writer.release()

    elapsed = time.time() - start_time
    logger.info(f"Video processed: {frame_idx} frames in {elapsed:.1f}s -> {output_path}")

    return {
        "frames_processed": frame_idx,
        "elapsed_seconds": elapsed,
        "output_path": output_path,
        "unique_plates": sorted(set(saved_plates)),
    }
