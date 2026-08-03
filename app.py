"""Application entry point.

Startup sequence:
User Starts Application -> app.py -> Load Configuration (config_manager.py)
-> Load YOLO Model (model_loader.py) -> Load EasyOCR (ocr_engine.py)
-> Create Database (database.py) -> Initialize Cache (cache.py)
-> Launch Streamlit UI
"""
import streamlit as st

from config.settings import APP_NAME, APP_ICON, BASE_DIR
from config.config_manager import config_manager
from ai.model_loader import load_yolo_model, load_ocr_engine
from database.database import init_db
from utils.cache import duplicate_cache
from utils.logger import logger

from services.detection_service import DetectionService
from services.analytics_service import AnalyticsService
from services.history_service import HistoryService
from services.settings_service import SettingsService
from services.vehicle_service import VehicleService

from components.navbar import render_sidebar
from components.footer import render_footer

from app_pages import (
    home, dashboard, image_detection, live_camera, video_detection, history,
    analytics, settings, vehicle_manager,
)

st.set_page_config(page_title=APP_NAME, page_icon=APP_ICON, layout="wide")


@st.cache_resource(show_spinner=False)
def bootstrap():
    """Runs once per server process: loads models, initializes DB, warms cache."""
    logger.info("Bootstrapping application...")
    init_db()

    weights_path = config_manager.get("model", "weights_path")
    model = load_yolo_model(weights_path)

    languages = config_manager.get("ocr", "languages", default=["en"])
    gpu = config_manager.get("ocr", "gpu", default=False)
    ocr_reader = load_ocr_engine(tuple(languages), gpu)

    duplicate_cache.window_seconds = config_manager.get(
        "cache", "duplicate_window_seconds", default=30
    )

    logger.info("Bootstrap complete.")
    return model, ocr_reader


def build_services(model, ocr_reader) -> dict:
    detection_service = DetectionService(model, ocr_reader, config_manager)
    return {
        "model": model,
        "ocr_reader": ocr_reader,
        "config_manager": config_manager,
        "detection_service": detection_service,
        "analytics_service": AnalyticsService(),
        "history_service": HistoryService(),
        "settings_service": SettingsService(config_manager),
        "vehicle_service": VehicleService(),
    }


def main():
    if "page" not in st.session_state:
        st.session_state.page = "home"

    try:
        model, ocr_reader = bootstrap()
    except FileNotFoundError as e:
        st.error(f"Startup failed: {e}")
        st.stop()

    services = build_services(model, ocr_reader)

    render_sidebar(st.session_state.page)

    page_map = {
        "home": home.render,
        "dashboard": dashboard.render,
        "image_detection": image_detection.render,
        "live_camera": live_camera.render,
        "video_detection": video_detection.render,
        "vehicle_manager": vehicle_manager.render,
        "history": history.render,
        "analytics": analytics.render,
        "settings": settings.render,
    }

    page_map[st.session_state.page](services)
    render_footer()


if __name__ == "__main__":
    main()
