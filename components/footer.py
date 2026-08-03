"""Simple footer shown at the bottom of every page."""
import streamlit as st


def render_footer():
    st.divider()
    st.caption(
        "Smart Vehicle Number Plate Recognition & Vehicle Management System "
        "· Built with Streamlit, YOLO11 & EasyOCR"
    )
