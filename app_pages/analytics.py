"""Analytics page: KPIs + Plotly charts built from the full detections table."""
import streamlit as st
from components.metric_cards import render_confidence_kpis
from components.charts import (
    daily_trend_chart, hourly_trend_chart, top_plates_chart,
    valid_invalid_pie, confidence_histogram,
)


def render(services: dict):
    st.title("📈 Analytics")
    report = services["analytics_service"].get_full_report()

    if report["row_count"] == 0:
        st.info("No data yet — run some detections first.")
        return

    render_confidence_kpis(report["confidence_stats"])
    st.metric("Total Records", report["row_count"])

    col1, col2 = st.columns(2)
    with col1:
        fig = daily_trend_chart(report["daily_trend"])
        if fig:
            st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig = hourly_trend_chart(report["hourly_trend"])
        if fig:
            st.plotly_chart(fig, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        fig = top_plates_chart(report["top_plates"])
        if fig:
            st.plotly_chart(fig, use_container_width=True)
    with col4:
        fig = valid_invalid_pie(report["valid_vs_invalid"])
        if fig:
            st.plotly_chart(fig, use_container_width=True)

    col5, col6 = st.columns(2)
    with col5:
        fig = confidence_histogram(report["dataframe"], "ocr_confidence", "OCR Confidence Distribution")
        if fig:
            st.plotly_chart(fig, use_container_width=True)
    with col6:
        fig = confidence_histogram(report["dataframe"], "detection_confidence", "Detection Confidence Distribution")
        if fig:
            st.plotly_chart(fig, use_container_width=True)
