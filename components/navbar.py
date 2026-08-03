"""Sidebar: branding + a Home shortcut + current-page indicator.
Primary navigation happens via the button grid on the Home page.
"""
import streamlit as st
from config.settings import APP_NAME, APP_ICON

PAGE_LABELS = {
    "home": "Home",
    "dashboard": "Dashboard",
    "image_detection": "Image Detection",
    "live_camera": "Live Camera",
    "video_detection": "Video Detection",
    "vehicle_manager": "Vehicle Database",
    "history": "Detection History",
    "analytics": "Analytics",
    "settings": "Settings",
}


def render_sidebar(current_page: str):
    with st.sidebar:
        st.markdown(f"### {APP_ICON} {APP_NAME}")
        st.caption(f"Viewing: **{PAGE_LABELS.get(current_page, current_page)}**")

        if current_page != "home":
            if st.button("🏠  Back to Home", use_container_width=True):
                st.session_state.page = "home"
                st.rerun()

        st.divider()
