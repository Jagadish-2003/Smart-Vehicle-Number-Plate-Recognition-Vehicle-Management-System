"""Image Detection page: upload -> detect -> crop -> OCR -> validate -> save -> display."""
import streamlit as st
import numpy as np
import cv2
from PIL import Image
from ai.vehicle_plate_detector import detect_plates
from ai.ocr_engine import read_plate_text
from utils.validation import validate_plate
from utils.cache import duplicate_cache
from database.database import insert_detection
from components.vehicle_card import render_vehicle_card


def render(services: dict):
    st.title("🖼️ Image Detection")

    uploaded = st.file_uploader("Upload a vehicle image", type=["jpg", "jpeg", "png"])
    if not uploaded:
        st.info("Upload an image to run detection.")
        return

    pil_image = Image.open(uploaded).convert("RGB")
    image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)

    st.image(pil_image, caption="Original Image", use_container_width=True)

    if st.button("Run Detection", type="primary"):
        with st.spinner("Detecting plates..."):
            result = services["detection_service"].process_frame(image, source="image")

        detections = result["detections"]
        if not detections:
            st.warning("No license plate detected in this image.")
            return

        for i, det in enumerate(detections, start=1):
            st.subheader(f"Detection {i}")
            x1, y1, x2, y2 = det["bbox"]
            crop = image[y1:y2, x1:x2]

            cols = st.columns(2)
            cols[0].image(cv2.cvtColor(crop, cv2.COLOR_BGR2RGB), caption="Cropped Plate")

            annotated = image.copy()
            color = (0, 200, 0) if det["valid"] else (0, 0, 220)
            cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 3)
            cols[1].image(cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB), caption="Detected Region")

            st.write(f"**YOLO Confidence:** {det['detection_confidence']:.2f}")
            st.write(f"**OCR Confidence:** {det['ocr_confidence']:.2f}")
            st.write(f"**Raw OCR Text:** `{det['raw_text']}`")
            st.write(f"**Corrected Plate:** `{det['plate']}`")
            if det["valid"]:
                st.success(f"Valid plate ✅ ({det['reason']})")
            else:
                st.error(f"Invalid plate ❌ ({det['reason']})")
            st.caption("Saved to database" if det["saved"] else "Not saved (duplicate or empty)")

            if det["plate"]:
                st.markdown("#### Vehicle Report")
                report = services["vehicle_service"].lookup(det["plate"])
                render_vehicle_card(report, vehicle_service=services["vehicle_service"])
