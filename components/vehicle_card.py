"""Renders the vehicle report card shown after a plate is read: owner info,
vehicle details, pending challans, blacklist alert, authorized status.

This is the "Vehicle Management System" half of the app — the part that
goes beyond raw plate text and turns a detection into a usable report,
matching the project's Expected Output section (owner, vehicle, challans,
blacklist status, authorized status).
"""
import streamlit as st
import pandas as pd


def render_vehicle_card(report: dict, allow_quick_add: bool = True, vehicle_service=None):
    plate = report["queried_plate"]

    if not report["found"]:
        st.warning(f"🔍 No vehicle record found for **{plate}**.")
        if allow_quick_add and vehicle_service is not None:
            with st.expander("➕ Register this plate in the demo vehicle database"):
                _quick_add_form(plate, vehicle_service)
        return

    v = report["vehicle"]
    if report["match_type"] == "fuzzy":
        st.caption(f"⚠️ No exact match for `{plate}` — showing closest record `{report['matched_plate']}` "
                   f"(OCR reads can be off by a character).")

    if report["blacklisted"]:
        st.error(f"🚨 **BLACKLISTED VEHICLE** — {report['blacklist_reason']}")
    elif not report["authorized"]:
        st.warning("🔶 This vehicle is **not authorized**.")
    else:
        st.success("✅ Vehicle is authorized and in good standing.")

    cols = st.columns(3)
    cols[0].metric("Owner", v["owner_name"] or "—")
    cols[1].metric("Vehicle", f"{v['brand']} {v['model']}".strip() or "—")
    cols[2].metric("Registration State", v["reg_state"] or "—")

    cols2 = st.columns(3)
    cols2[0].metric("Pending Challans", len(report["pending_challans"]))
    cols2[1].metric("Blacklist Status", "Yes" if report["blacklisted"] else "No")
    cols2[2].metric("Authorized", "Yes" if report["authorized"] else "No")

    with st.expander("Full vehicle details"):
        details = {
            "Plate Number": v["plate_number"],
            "Owner Phone": v["owner_phone"],
            "Vehicle Type": v["vehicle_type"],
            "Color": v["color"],
            "RC Expiry": v["rc_expiry"],
            "Insurance Valid Till": v["insurance_valid_till"],
            "PUC Valid Till": v["puc_valid_till"],
        }
        st.table(pd.DataFrame(details.items(), columns=["Field", "Value"]))

    if report["challans"]:
        with st.expander(f"Challan history ({len(report['challans'])})"):
            st.dataframe(pd.DataFrame(report["challans"]), use_container_width=True, hide_index=True)


def _quick_add_form(plate: str, vehicle_service):
    with st.form(key=f"quick_add_{plate}"):
        c1, c2 = st.columns(2)
        owner_name = c1.text_input("Owner Name", key=f"qa_owner_{plate}")
        owner_phone = c2.text_input("Owner Phone", key=f"qa_phone_{plate}")
        c3, c4 = st.columns(2)
        brand = c3.text_input("Brand", key=f"qa_brand_{plate}")
        model = c4.text_input("Model", key=f"qa_model_{plate}")
        c5, c6 = st.columns(2)
        vehicle_type = c5.selectbox(
            "Vehicle Type", ["Hatchback", "Sedan", "SUV", "MUV", "Motorcycle", "Truck", "Other"],
            key=f"qa_type_{plate}",
        )
        color = c6.text_input("Color", key=f"qa_color_{plate}")
        reg_state = st.text_input("Registration State", key=f"qa_state_{plate}")
        authorized = st.checkbox("Authorized vehicle", value=True, key=f"qa_auth_{plate}")

        if st.form_submit_button("Save to Vehicle Database", type="primary"):
            vehicle_service.save_vehicle(
                plate_number=plate, owner_name=owner_name, owner_phone=owner_phone,
                brand=brand, model=model, vehicle_type=vehicle_type, color=color,
                reg_state=reg_state, authorized=authorized,
            )
            st.success(f"Saved {plate} to the vehicle database.")
            st.rerun()
