"""Reusable KPI metric card rendering for Dashboard and Analytics pages."""
import streamlit as st


def render_kpi_row(stats: dict):
    cols = st.columns(4)
    labels = [
        ("Total Detections", stats.get("total", 0)),
        ("Valid Plates", stats.get("valid", 0)),
        ("Invalid Plates", stats.get("invalid", 0)),
        ("Today's Detections", stats.get("today", 0)),
    ]
    for col, (label, value) in zip(cols, labels):
        col.metric(label, value)


def render_confidence_kpis(conf_stats: dict):
    cols = st.columns(2)
    cols[0].metric("Avg OCR Confidence", f"{conf_stats.get('avg_ocr_confidence', 0):.2f}")
    cols[1].metric("Avg Detection Confidence", f"{conf_stats.get('avg_detection_confidence', 0):.2f}")
