"""Detection History page: search/filter/sort/display/delete/export."""
import streamlit as st


def render(services: dict):
    st.title("🕘 Detection History")
    history_service = services["history_service"]

    cols = st.columns([3, 1])
    query = cols[0].text_input("Search plate number", "")
    status = cols[1].selectbox("Filter", ["all", "valid", "invalid"])

    df = history_service.get_history(query=query, status=status)

    if df.empty:
        st.info("No detections match this search.")
        return

    df_sorted = df.sort_values("detection_time", ascending=False)
    st.dataframe(df_sorted, use_container_width=True, hide_index=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.download_button(
            "Export CSV", history_service.export_csv(df_sorted),
            file_name="detection_history.csv", mime="text/csv",
        )
    with col2:
        delete_id = st.number_input("Record ID to delete", min_value=0, step=1)
        if st.button("Delete Record") and delete_id:
            history_service.delete(int(delete_id))
            st.success(f"Deleted record {int(delete_id)}")
            st.rerun()
    with col3:
        if st.button("Delete All", type="secondary"):
            st.session_state.confirm_delete_all = True
        if st.session_state.get("confirm_delete_all"):
            st.warning("This will permanently delete all records.")
            if st.button("Confirm Delete All", type="primary"):
                history_service.delete_all()
                st.session_state.confirm_delete_all = False
                st.success("All records deleted.")
                st.rerun()
