"""Basic sanity tests for the plate validation pipeline.
Run with: python -m pytest tests/ -v
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.validation import clean_text, regex_validate, validate_plate


def test_clean_text_strips_symbols_and_spaces():
    assert clean_text("HR 26 FC-2782") == "HR26FC2782"


def test_clean_text_uppercases():
    assert clean_text("hr26fc2782") == "HR26FC2782"


def test_regex_validate_accepts_standard_format():
    assert regex_validate("HR26FC2782") is True


def test_regex_validate_rejects_bad_format():
    assert regex_validate("HELLO123") is False


def test_validate_plate_full_pipeline():
    result = validate_plate("HR 26 FC-2782", ocr_confidence=0.9)
    assert result["plate"] == "HR26FC2782"
    assert result["valid"] is True


def test_validate_plate_low_confidence_is_invalid():
    result = validate_plate("HR26FC2782", ocr_confidence=0.1, min_confidence=0.4)
    assert result["valid"] is False
    assert result["reason"] == "low_confidence"


if __name__ == "__main__":
    test_clean_text_strips_symbols_and_spaces()
    test_clean_text_uppercases()
    test_regex_validate_accepts_standard_format()
    test_regex_validate_rejects_bad_format()
    test_validate_plate_full_pipeline()
    test_validate_plate_low_confidence_is_invalid()
    print("All tests passed.")
