"""Settings page: editable thresholds, cache/database management, storage info."""
import streamlit as st


def render(services: dict):
    st.title("⚙️ Settings")
    config = services["config_manager"]
    settings_service = services["settings_service"]

    st.subheader("Detection Thresholds")
    conf = st.slider("YOLO Confidence Threshold", 0.0, 1.0,
                      config.get("model", "confidence_threshold", default=0.5), 0.01)
    iou = st.slider("YOLO IOU Threshold", 0.0, 1.0,
                     config.get("model", "iou_threshold", default=0.45), 0.01)
    ocr_conf = st.slider("Minimum OCR Confidence", 0.0, 1.0,
                          config.get("ocr", "min_confidence", default=0.4), 0.01)

    if st.button("Save Thresholds", type="primary"):
        settings_service.update_threshold("model", "confidence_threshold", conf)
        settings_service.update_threshold("model", "iou_threshold", iou)
        settings_service.update_threshold("ocr", "min_confidence", ocr_conf)
        st.success("Settings saved.")

    st.divider()
    st.subheader("Cache Management")
    from utils.cache import duplicate_cache
    st.write(f"Cached plates in duplicate-detection window: **{duplicate_cache.size()}**")
    if st.button("Clear Cache"):
        settings_service.clear_cache()
        st.success("Cache cleared.")

    st.divider()
    st.subheader("Database Management")
    if st.button("Clear All Detection Records", type="secondary"):
        st.session_state.confirm_clear_db = True
    if st.session_state.get("confirm_clear_db"):
        st.warning("This permanently deletes every detection record.")
        if st.button("Confirm Clear Database", type="primary"):
            settings_service.clear_database()
            st.session_state.confirm_clear_db = False
            st.success("Database cleared.")

    st.divider()
    st.subheader("Storage Information")
    storage = settings_service.storage_info()
    cols = st.columns(4)
    cols[0].metric("Cropped Plates", f"{storage['cropped_plates_mb']} MB")
    cols[1].metric("Annotated Images", f"{storage['annotated_images_mb']} MB")
    cols[2].metric("Videos", f"{storage['videos_mb']} MB")
    cols[3].metric("Database", f"{storage['database_mb']} MB")
    st.caption(f"Free disk space: {storage['disk_free_gb']} GB")

    st.divider()
    st.subheader("Model Status")
    model_status = settings_service.model_status(
        model_loaded=services["model"] is not None,
        ocr_loaded=services["ocr_reader"] is not None,
    )
    st.json(model_status)
