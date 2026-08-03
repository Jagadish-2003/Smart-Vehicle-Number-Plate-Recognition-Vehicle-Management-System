"""Coordinates the end-to-end detection pipeline:
detect -> crop -> preprocess -> OCR -> validate -> duplicate check -> save.

Used by the Image Detection, Live Camera, and Video Detection pages.
"""
import os
import uuid
import cv2
from datetime import datetime
from ai.vehicle_plate_detector import detect_plates
from ai.ocr_engine import read_plate_text
from utils.validation import validate_plate
from utils.cache import duplicate_cache
from database.database import insert_detection
from config.settings import BASE_DIR
from utils.logger import logger

CROPPED_DIR = os.path.join(BASE_DIR, "outputs", "cropped_plates")
ANNOTATED_DIR = os.path.join(BASE_DIR, "outputs", "annotated_images")


class DetectionService:
    def __init__(self, model, ocr_reader, config_manager):
        self.model = model
        self.ocr_reader = ocr_reader
        self.config = config_manager

    def _save_crop(self, crop, plate_text: str) -> str:
        os.makedirs(CROPPED_DIR, exist_ok=True)
        filename = f"{plate_text or 'unknown'}_{uuid.uuid4().hex[:8]}.jpg"
        path = os.path.join(CROPPED_DIR, filename)
        cv2.imwrite(path, crop)
        return path

    def process_frame(self, frame, source: str = "image", save_crops: bool = True) -> dict:
        """Runs the full pipeline on a single BGR frame/image.
        Returns {"detections": [ {bbox, plate, valid, confidence, ocr_confidence, saved} ]}
        """
        conf_th = self.config.get("model", "confidence_threshold", default=0.5)
        iou_th = self.config.get("model", "iou_threshold", default=0.45)
        min_ocr_conf = self.config.get("ocr", "min_confidence", default=0.4)
        min_len = self.config.get("validation", "min_plate_length", default=8)
        max_len = self.config.get("validation", "max_plate_length", default=11)

        plate_detections = detect_plates(self.model, frame, conf_th, iou_th)
        results = []

        for det in plate_detections:
            ocr_result = read_plate_text(self.ocr_reader, det["crop"])
            validation = validate_plate(
                ocr_result["best_text"], ocr_result["best_confidence"],
                min_confidence=min_ocr_conf, min_len=min_len, max_len=max_len,
            )

            plate_text = validation["plate"]
            is_valid = validation["valid"]
            saved = False
            image_path = ""

            if plate_text:
                is_duplicate = duplicate_cache.is_duplicate(plate_text)
                if not is_duplicate:
                    if save_crops:
                        image_path = self._save_crop(det["crop"], plate_text)
                    insert_detection(
                        plate_number=plate_text,
                        ocr_confidence=ocr_result["best_confidence"],
                        detection_confidence=det["confidence"],
                        image_path=image_path,
                        source=source,
                        status="valid" if is_valid else "invalid",
                        remarks=validation["reason"],
                    )
                    saved = True

            results.append({
                "bbox": det["bbox"],
                "detection_confidence": det["confidence"],
                "ocr_confidence": ocr_result["best_confidence"],
                "raw_text": ocr_result["best_text"],
                "plate": plate_text,
                "valid": is_valid,
                "reason": validation["reason"],
                "saved": saved,
            })

        return {"detections": results, "timestamp": datetime.now().isoformat(timespec="seconds")}
