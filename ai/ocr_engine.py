"""Runs EasyOCR on both the raw crop and the preprocessed crop, and keeps
whichever result has higher OCR confidence."""
import numpy as np
from ai.preprocessing import preprocess_plate
from utils.logger import logger


def _run_easyocr(reader, image: np.ndarray):
    results = reader.readtext(image)
    if not results:
        return "", 0.0
    # Concatenate all detected text fragments, weight confidence by text length
    texts, confidences, weights = [], [], []
    for _, text, conf in results:
        texts.append(text)
        confidences.append(conf)
        weights.append(max(len(text), 1))
    combined_text = "".join(texts)
    weighted_conf = sum(c * w for c, w in zip(confidences, weights)) / sum(weights)
    return combined_text, float(weighted_conf)


def read_plate_text(reader, cropped_plate: np.ndarray) -> dict:
    """Returns the best OCR result across the raw and preprocessed image."""
    raw_text, raw_conf = _run_easyocr(reader, cropped_plate)

    processed_image = preprocess_plate(cropped_plate)
    processed_text, processed_conf = _run_easyocr(reader, processed_image)

    if processed_conf >= raw_conf:
        best_text, best_conf, source = processed_text, processed_conf, "processed"
    else:
        best_text, best_conf, source = raw_text, raw_conf, "raw"

    logger.info(
        f"OCR raw='{raw_text}'({raw_conf:.2f}) processed='{processed_text}'({processed_conf:.2f}) "
        f"-> chose {source}"
    )

    return {
        "raw_text": raw_text,
        "raw_confidence": raw_conf,
        "processed_text": processed_text,
        "processed_confidence": processed_conf,
        "best_text": best_text,
        "best_confidence": best_conf,
        "processed_image": processed_image,
        "source": source,
    }
