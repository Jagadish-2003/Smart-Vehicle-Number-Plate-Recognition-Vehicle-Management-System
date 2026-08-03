"""Static, non-editable path/constant settings for the application."""
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(BASE_DIR, "config", "app_config.json")

APP_NAME = "Smart Vehicle Number Plate Recognition & Vehicle Management System"
APP_ICON = "🚗"

# Indian registration number formats: AA00AA0000 / AA00A0000 / AA0AA0000
PLATE_REGEX_PATTERNS = [
    r"^[A-Z]{2}[0-9]{2}[A-Z]{2}[0-9]{4}$",
    r"^[A-Z]{2}[0-9]{2}[A-Z][0-9]{4}$",
    r"^[A-Z]{2}[0-9][A-Z]{2}[0-9]{4}$",
]
