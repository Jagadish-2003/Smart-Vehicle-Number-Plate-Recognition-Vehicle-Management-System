"""Image preprocessing pipeline applied to cropped plate regions before OCR.

Pipeline: grayscale -> gaussian blur -> CLAHE -> OTSU threshold -> resize
"""
import cv2
import numpy as np


def to_grayscale(image: np.ndarray) -> np.ndarray:
    if len(image.shape) == 2:
        return image
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


def gaussian_blur(image: np.ndarray, ksize=(5, 5)) -> np.ndarray:
    return cv2.GaussianBlur(image, ksize, 0)


def apply_clahe(image: np.ndarray, clip_limit: float = 2.0, tile_grid_size=(8, 8)) -> np.ndarray:
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)
    return clahe.apply(image)


def otsu_threshold(image: np.ndarray) -> np.ndarray:
    _, thresh = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return thresh


def resize(image: np.ndarray, scale: float = 2.0) -> np.ndarray:
    h, w = image.shape[:2]
    return cv2.resize(image, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_CUBIC)


def preprocess_plate(image: np.ndarray) -> np.ndarray:
    """Runs the full preprocessing pipeline on a cropped plate image and
    returns a processed (binary, upscaled) image ready for OCR."""
    gray = to_grayscale(image)
    blurred = gaussian_blur(gray)
    enhanced = apply_clahe(blurred)
    thresholded = otsu_threshold(enhanced)
    processed = resize(thresholded)
    return processed
