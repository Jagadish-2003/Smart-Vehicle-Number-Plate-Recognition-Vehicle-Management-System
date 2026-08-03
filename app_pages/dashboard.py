"""Dashboard page: KPIs, recent detections, system status."""
import streamlit as st
import pandas as pd
from database.database import get_stats, get_all_detections
from components.metric_cards import render_kpi_row


def render(services: dict):
    st.title("📊 Dashboard")

    stats = get_stats()
    render_kpi_row(stats)

    st.subheader("Recent Detection History")
    recent = get_all_detections(limit=10)
    if recent:
        st.dataframe(pd.DataFrame(recent), use_container_width=True, hide_index=True)
    else:
        st.info("No detections yet. Try Image Detection, Live Camera, or Video Detection.")

    st.subheader("System Status")
    model_status = services["settings_service"].model_status(
        model_loaded=services["model"] is not None,
        ocr_loaded=services["ocr_reader"] is not None,
    )
    cols = st.columns(3)
    cols[0].metric("YOLO Model", "Loaded ✅" if model_status["yolo_loaded"] else "Not Loaded ❌")
    cols[1].metric("EasyOCR Engine", "Loaded ✅" if model_status["ocr_loaded"] else "Not Loaded ❌")
    cols[2].metric("Weights File", "Found ✅" if model_status["weights_exist"] else "Missing ❌")
