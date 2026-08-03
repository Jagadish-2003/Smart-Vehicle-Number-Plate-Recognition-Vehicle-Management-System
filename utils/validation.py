"""Cleans raw OCR text and validates it against Indian plate formats."""
import re
from config.settings import PLATE_REGEX_PATTERNS

_COMPILED_PATTERNS = [re.compile(p) for p in PLATE_REGEX_PATTERNS]


def clean_text(raw_text: str) -> str:
    """Remove spaces/symbols, uppercase, keep only A-Z and 0-9."""
    if not raw_text:
        return ""
    text = raw_text.upper()
    text = re.sub(r"[^A-Z0-9]", "", text)
    return text


def strip_known_prefixes(text: str) -> str:
    """Remove common junk OCR prefixes like 'IND' that sometimes get read
    from the plate's country stamp before the actual registration number."""
    for prefix in ("IND",):
        if text.startswith(prefix) and len(text) - len(prefix) >= 8:
            text = text[len(prefix):]
    return text


def check_length(text: str, min_len: int = 8, max_len: int = 11) -> bool:
    return min_len <= len(text) <= max_len


def check_confidence(confidence: float, min_confidence: float = 0.4) -> bool:
    return confidence >= min_confidence


def regex_validate(text: str) -> bool:
    return any(p.match(text) for p in _COMPILED_PATTERNS)


def validate_plate(raw_text: str, ocr_confidence: float, min_confidence: float = 0.4,
                    min_len: int = 8, max_len: int = 11) -> dict:
    """Full validation pipeline. Returns dict with cleaned text, validity, reason."""
    text = clean_text(raw_text)
    text = strip_known_prefixes(text)

    if not check_length(text, min_len, max_len):
        return {"plate": text, "valid": False, "reason": "invalid_length"}
    if not check_confidence(ocr_confidence, min_confidence):
        return {"plate": text, "valid": False, "reason": "low_confidence"}
    if not regex_validate(text):
        return {"plate": text, "valid": False, "reason": "regex_mismatch"}

    return {"plate": text, "valid": True, "reason": "ok"}
