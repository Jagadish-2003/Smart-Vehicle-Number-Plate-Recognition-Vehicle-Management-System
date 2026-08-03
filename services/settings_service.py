"""Settings page support: config read/write, cache clearing, storage info,
and basic system/model health checks."""
import os
import shutil
from config.settings import BASE_DIR
from utils.cache import duplicate_cache
from database.database import delete_all_detections, DB_PATH


class SettingsService:
    def __init__(self, config_manager):
        self.config = config_manager

    def update_threshold(self, section: str, key: str, value):
        self.config.set(section, key, value)

    def clear_cache(self):
        duplicate_cache.clear()

    def clear_database(self):
        delete_all_detections()

    def storage_info(self) -> dict:
        def dir_size(path):
            total = 0
            if os.path.exists(path):
                for dirpath, _, filenames in os.walk(path):
                    for f in filenames:
                        total += os.path.getsize(os.path.join(dirpath, f))
            return round(total / (1024 * 1024), 2)  # MB

        return {
            "cropped_plates_mb": dir_size(os.path.join(BASE_DIR, "outputs", "cropped_plates")),
            "annotated_images_mb": dir_size(os.path.join(BASE_DIR, "outputs", "annotated_images")),
            "videos_mb": dir_size(os.path.join(BASE_DIR, "outputs", "videos")),
            "database_mb": round(os.path.getsize(DB_PATH) / (1024 * 1024), 2) if os.path.exists(DB_PATH) else 0,
            "disk_free_gb": round(shutil.disk_usage(BASE_DIR).free / (1024 ** 3), 2),
        }

    def model_status(self, model_loaded: bool, ocr_loaded: bool) -> dict:
        weights_path = os.path.join(BASE_DIR, self.config.get("model", "weights_path"))
        return {
            "yolo_loaded": model_loaded,
            "ocr_loaded": ocr_loaded,
            "weights_exist": os.path.exists(weights_path),
            "weights_path": weights_path,
        }
