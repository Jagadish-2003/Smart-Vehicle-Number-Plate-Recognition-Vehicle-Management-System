"""Vehicle Database page: register/edit vehicles, issue/settle challans,
and manage the blacklist. This is the admin side of the "Vehicle Management
System" — the Image/Live/Video detection pages are the read side.
"""
import streamlit as st
import pandas as pd


def render(services: dict):
    st.title("🗂️ Vehicle Database")
    vs = services["vehicle_service"]

    tab_vehicles, tab_challans, tab_blacklist = st.tabs(
        ["🚙 Vehicles", "🧾 Challans", "⛔ Blacklist"]
    )

    with tab_vehicles:
        st.subheader("Registered Vehicles")
        query = st.text_input("Search by plate or owner name", "")
        vehicles = vs.all_vehicles(query)
        if vehicles:
            st.dataframe(pd.DataFrame(vehicles), use_container_width=True, hide_index=True)
        else:
            st.info("No vehicles registered yet.")

        st.divider()
        st.subheader("Add / Update Vehicle")
        with st.form("vehicle_form", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            plate_number = c1.text_input("Plate Number *").upper().strip()
            owner_name = c2.text_input("Owner Name")
            owner_phone = c3.text_input("Owner Phone")

            c4, c5, c6 = st.columns(3)
            brand = c4.text_input("Brand")
            model = c5.text_input("Model")
            vehicle_type = c6.selectbox(
                "Vehicle Type", ["Hatchback", "Sedan", "SUV", "MUV", "Motorcycle", "Truck", "Other"]
            )

            c7, c8, c9 = st.columns(3)
            color = c7.text_input("Color")
            reg_state = c8.text_input("Registration State")
            authorized = c9.checkbox("Authorized", value=True)

            c10, c11, c12 = st.columns(3)
            rc_expiry = c10.text_input("RC Expiry (YYYY-MM-DD)")
            insurance_valid_till = c11.text_input("Insurance Valid Till (YYYY-MM-DD)")
            puc_valid_till = c12.text_input("PUC Valid Till (YYYY-MM-DD)")

            if st.form_submit_button("Save Vehicle", type="primary"):
                if not plate_number:
                    st.error("Plate Number is required.")
                else:
                    vs.save_vehicle(
                        plate_number=plate_number, owner_name=owner_name, owner_phone=owner_phone,
                        brand=brand, model=model, vehicle_type=vehicle_type, color=color,
                        reg_state=reg_state, rc_expiry=rc_expiry,
                        insurance_valid_till=insurance_valid_till, puc_valid_till=puc_valid_till,
                        authorized=authorized,
                    )
                    st.success(f"Saved {plate_number}.")
                    st.rerun()

        with st.expander("Remove a vehicle"):
            del_plate = st.text_input("Plate number to remove", key="del_vehicle_plate")
            if st.button("Delete Vehicle") and del_plate:
                vs.remove_vehicle(del_plate)
                st.success(f"Removed {del_plate.upper()}.")
                st.rerun()

    with tab_challans:
        st.subheader("Issue a Challan")
        with st.form("challan_form", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            plate = c1.text_input("Plate Number *").upper().strip()
            reason = c2.text_input("Violation / Reason")
            amount = c3.number_input("Amount (₹)", min_value=0.0, step=100.0)
            if st.form_submit_button("Issue Challan", type="primary"):
                if not plate:
                    st.error("Plate Number is required.")
                else:
                    vs.add_challan(plate, reason, amount)
                    st.success(f"Challan issued for {plate}.")
                    st.rerun()

        st.divider()
        st.subheader("Look Up Challans")
        lookup_plate = st.text_input("Plate number", key="challan_lookup")
        if lookup_plate:
            report = vs.lookup(lookup_plate, fuzzy=False)
            if report["challans"]:
                df = pd.DataFrame(report["challans"])
                st.dataframe(df, use_container_width=True, hide_index=True)
                for c in report["challans"]:
                    if c["status"] == "pending":
                        cols = st.columns([3, 1])
                        cols[0].write(f"Challan #{c['id']} — {c['reason']} (₹{c['amount']})")
                        if cols[1].button("Mark Paid", key=f"pay_{c['id']}"):
                            vs.set_challan_status(c["id"], "paid")
                            st.rerun()
            else:
                st.info("No challans found for this plate.")

    with tab_blacklist:
        st.subheader("Blacklisted Vehicles")
        blacklisted = vs.all_blacklisted()
        if blacklisted:
            st.dataframe(pd.DataFrame(blacklisted), use_container_width=True, hide_index=True)
        else:
            st.info("No vehicles are currently blacklisted.")

        c1, c2 = st.columns(2)
        with c1:
            with st.form("blacklist_add_form", clear_on_submit=True):
                bl_plate = st.text_input("Plate Number to blacklist").upper().strip()
                bl_reason = st.text_input("Reason")
                if st.form_submit_button("Add to Blacklist", type="primary"):
                    if bl_plate and vs.blacklist_add(bl_plate, bl_reason):
                        st.success(f"{bl_plate} added to blacklist.")
                        st.rerun()
                    elif bl_plate:
                        st.warning(f"{bl_plate} is already blacklisted.")
        with c2:
            with st.form("blacklist_remove_form", clear_on_submit=True):
                rm_plate = st.text_input("Plate Number to remove from blacklist").upper().strip()
                if st.form_submit_button("Remove from Blacklist"):
                    if rm_plate:
                        vs.blacklist_remove(rm_plate)
                        st.success(f"{rm_plate} removed from blacklist.")
                        st.rerun()
