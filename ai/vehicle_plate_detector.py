"""Runs YOLO license-plate detection on an image and returns bounding boxes
plus cropped plate regions.

Because this project's model is trained on a small custom dataset, recall
can be inconsistent on plates that look different from the training images
(unusual angle, lighting, distance). To compensate without retraining, this
module:

  1. Runs detection at the configured confidence threshold first.
  2. If nothing is found, retries once at a lower "rescue" threshold with
     test-time augmentation enabled (Ultralytics' `augment=True` runs
     multi-scale/flip inference and merges results -- it's slower but
     noticeably improves recall on small-data models).

This is a mitigation, not a substitute for more training data -- see
README.md -> "Improving detection accuracy" for how to properly retrain
with a larger dataset.
"""
import numpy as np
from utils.logger import logger

RESCUE_CONF = 0.20


def _extract(results, image) -> list:
    detections = []
    for result in results:
        boxes = result.boxes
        if boxes is None:
            continue
        for box in boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
            confidence = float(box.conf[0])
            x1, y1 = max(x1, 0), max(y1, 0)
            x2, y2 = min(x2, image.shape[1]), min(y2, image.shape[0])
            if x2 <= x1 or y2 <= y1:
                continue
            crop = image[y1:y2, x1:x2].copy()
            detections.append({
                "bbox": (x1, y1, x2, y2),
                "confidence": confidence,
                "crop": crop,
            })
    return detections


def detect_plates(model, image: np.ndarray, conf_threshold: float = 0.5,
                   iou_threshold: float = 0.45, allow_rescue: bool = True) -> list:
    """Returns a list of dicts: {bbox: (x1,y1,x2,y2), confidence: float, crop: np.ndarray}"""
    results = model.predict(image, conf=conf_threshold, iou=iou_threshold, verbose=False)
    detections = _extract(results, image)

    if not detections and allow_rescue and conf_threshold > RESCUE_CONF:
        logger.info(f"No detections at conf={conf_threshold}; retrying at conf={RESCUE_CONF} with TTA")
        try:
            rescue_results = model.predict(
                image, conf=RESCUE_CONF, iou=iou_threshold, verbose=False, augment=True,
            )
        except Exception as e:  # augment can occasionally fail on tiny images; fall back cleanly
            logger.warning(f"TTA rescue pass failed ({e}); retrying without augmentation")
            rescue_results = model.predict(image, conf=RESCUE_CONF, iou=iou_threshold, verbose=False)
        detections = _extract(rescue_results, image)

    logger.info(f"YOLO detected {len(detections)} plate(s)")
    return detections
