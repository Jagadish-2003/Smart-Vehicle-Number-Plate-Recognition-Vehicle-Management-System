"""Video Detection page: upload -> extract/skip frames -> detect -> annotate
-> build output video -> download."""
import os
import tempfile
import streamlit as st
from ai.video_processor import process_video
from config.settings import BASE_DIR
from components.vehicle_card import render_vehicle_card

OUTPUT_DIR = os.path.join(BASE_DIR, "outputs", "videos")


def render(services: dict):
    st.title("🎬 Video Detection")

    uploaded = st.file_uploader("Upload a video", type=["mp4", "avi", "mov", "mkv"])
    frame_skip = st.slider("Frame skip (higher = faster, less accurate)", 1, 10,
                            services["config_manager"].get("video", "frame_skip", default=3))

    if not uploaded:
        st.info("Upload a video to run detection.")
        return

    if st.button("Process Video", type="primary"):
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded.name)[1]) as tmp_in:
            tmp_in.write(uploaded.read())
            input_path = tmp_in.name

        output_path = os.path.join(OUTPUT_DIR, f"annotated_{uploaded.name.rsplit('.', 1)[0]}.mp4")

        progress_bar = st.progress(0.0, text="Processing video...")

        def update_progress(fraction):
            progress_bar.progress(fraction, text=f"Processing video... {int(fraction * 100)}%")

        with st.spinner("Running detection pipeline over all frames..."):
            result = process_video(
                video_path=input_path,
                output_path=output_path,
                model=services["model"],
                ocr_reader=services["ocr_reader"],
                detection_service=services["detection_service"],
                frame_skip=frame_skip,
                progress_callback=update_progress,
            )

        os.unlink(input_path)
        st.success(f"Processed {result['frames_processed']} frames in {result['elapsed_seconds']:.1f}s")

        if result["unique_plates"]:
            st.write("**Unique plates detected:**")
            st.write(", ".join(f"`{p}`" for p in result["unique_plates"]))
            st.markdown("#### Vehicle Reports")
            for plate in result["unique_plates"]:
                with st.expander(f"Report for {plate}"):
                    report = services["vehicle_service"].lookup(plate)
                    render_vehicle_card(report, vehicle_service=services["vehicle_service"])
        else:
            st.info("No valid plates detected in this video.")

        with open(output_path, "rb") as f:
            st.download_button(
                "Download Annotated Video", f, file_name=os.path.basename(output_path),
                mime="video/mp4",
            )
