"""Live Camera page: webcam stream -> per-frame detection -> live table.

Uses streamlit-webrtc when available; falls back to a single-shot
st.camera_input capture (works in browsers without webrtc support / on
Streamlit Community Cloud without extra config).
"""
import time
import streamlit as st
import numpy as np
import cv2
from PIL import Image
from components.vehicle_card import render_vehicle_card


def render(services: dict):
    st.title("📷 Live Camera")

    if "live_detections" not in st.session_state:
        st.session_state.live_detections = []
    if "live_frame_count" not in st.session_state:
        st.session_state.live_frame_count = 0
    if "live_start_time" not in st.session_state:
        st.session_state.live_start_time = time.time()

    col_a, col_b = st.columns(2)
    with col_a:
        st.metric("Frames Processed", st.session_state.live_frame_count)
    with col_b:
        elapsed = max(time.time() - st.session_state.live_start_time, 1e-6)
        fps = st.session_state.live_frame_count / elapsed
        st.metric("FPS", f"{fps:.1f}")

    st.caption(
        "Browser camera capture is used here for portability (works on any device/browser). "
        "Take a photo to run one detection pass; keep capturing for a live-style feed."
    )
    snapshot = st.camera_input("Camera")

    if snapshot is not None:
        pil_image = Image.open(snapshot).convert("RGB")
        frame = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)

        result = services["detection_service"].process_frame(frame, source="live_camera")
        st.session_state.live_frame_count += 1

        latest_plate = None
        for det in result["detections"]:
            if det["plate"]:
                latest_plate = det["plate"]
                st.session_state.live_detections.insert(0, {
                    "plate": det["plate"],
                    "valid": det["valid"],
                    "ocr_confidence": round(det["ocr_confidence"], 2),
                    "detection_confidence": round(det["detection_confidence"], 2),
                    "saved": det["saved"],
                    "time": result["timestamp"],
                })

        if latest_plate:
            st.markdown("#### Vehicle Report — latest capture")
            report = services["vehicle_service"].lookup(latest_plate)
            render_vehicle_card(report, vehicle_service=services["vehicle_service"])
        elif result["detections"]:
            st.info("Plate detected but text couldn't be read reliably — try a closer, well-lit shot.")

    st.subheader("Live Detections")
    if st.session_state.live_detections:
        import pandas as pd
        df = pd.DataFrame(st.session_state.live_detections)
        st.dataframe(df, use_container_width=True, hide_index=True)

        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                "Export CSV", df.to_csv(index=False).encode("utf-8"),
                file_name="live_detections.csv", mime="text/csv",
            )
        with col2:
            if st.button("Reset Statistics"):
                st.session_state.live_detections = []
                st.session_state.live_frame_count = 0
                st.session_state.live_start_time = time.time()
                st.rerun()
    else:
        st.info("No detections yet — capture a frame above.")
