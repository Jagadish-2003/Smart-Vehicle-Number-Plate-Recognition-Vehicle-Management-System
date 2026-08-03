"""Loads and caches the YOLO detector and EasyOCR reader."""
import os
import streamlit as st
from ultralytics import YOLO
import easyocr
from config.settings import BASE_DIR
from utils.logger import logger


@st.cache_resource(show_spinner="Loading YOLO model...")
def load_yolo_model(weights_path: str) -> YOLO:
    full_path = weights_path if os.path.isabs(weights_path) else os.path.join(BASE_DIR, weights_path)
    if not os.path.exists(full_path):
        raise FileNotFoundError(f"YOLO weights not found at {full_path}")
    model = YOLO(full_path)
    logger.info(f"YOLO model loaded from {full_path}")
    return model


@st.cache_resource(show_spinner="Loading EasyOCR engine...")
def load_ocr_engine(languages=("en",), gpu: bool = False) -> easyocr.Reader:
    reader = easyocr.Reader(list(languages), gpu=gpu)
    logger.info(f"EasyOCR engine loaded (languages={languages}, gpu={gpu})")
    return reader
