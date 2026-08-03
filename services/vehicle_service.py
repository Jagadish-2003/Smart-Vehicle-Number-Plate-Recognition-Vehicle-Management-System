"""Wraps the vehicle/challan/blacklist tables and adds a fuzzy lookup so a
slightly-imperfect OCR read (e.g. one wrong character) can still match a
registered vehicle, the way a real ANPR gate system would.
"""
import difflib
from database.database import (
    get_vehicle, list_vehicles, upsert_vehicle, delete_vehicle, all_vehicle_plates,
    get_challans, add_challan, update_challan_status, delete_challan,
    is_blacklisted, add_to_blacklist, remove_from_blacklist, list_blacklist,
)


class VehicleService:
    def lookup(self, plate_number: str, fuzzy: bool = True) -> dict:
        """Returns a full report for a plate: vehicle info, challans,
        blacklist status, authorized status, and how confidently it matched.
        """
        plate_number = (plate_number or "").upper().strip()
        vehicle = get_vehicle(plate_number)
        matched_plate = plate_number
        match_type = "exact" if vehicle else "none"

        if not vehicle and fuzzy and plate_number:
            candidate, score = self._closest_match(plate_number)
            if candidate and score >= 0.82:
                vehicle = get_vehicle(candidate)
                matched_plate = candidate
                match_type = "fuzzy"

        challans = get_challans(matched_plate) if vehicle else []
        pending_challans = [c for c in challans if c["status"] == "pending"]
        blacklist_entry = is_blacklisted(matched_plate) if vehicle or plate_number else is_blacklisted(plate_number)

        return {
            "queried_plate": plate_number,
            "matched_plate": matched_plate if vehicle else None,
            "match_type": match_type,
            "found": vehicle is not None,
            "vehicle": vehicle,
            "challans": challans,
            "pending_challans": pending_challans,
            "blacklisted": blacklist_entry is not None,
            "blacklist_reason": blacklist_entry["reason"] if blacklist_entry else None,
            "authorized": bool(vehicle["authorized"]) if vehicle else None,
        }

    def _closest_match(self, plate_number: str):
        plates = all_vehicle_plates()
        if not plates:
            return None, 0.0
        matches = difflib.get_close_matches(plate_number, plates, n=1, cutoff=0.6)
        if not matches:
            return None, 0.0
        best = matches[0]
        score = difflib.SequenceMatcher(None, plate_number, best).ratio()
        return best, score

    # --- CRUD passthroughs (kept here so pages only import one service) ---
    def save_vehicle(self, **kwargs):
        upsert_vehicle(**kwargs)

    def remove_vehicle(self, plate_number: str):
        delete_vehicle(plate_number)

    def all_vehicles(self, query: str = ""):
        return list_vehicles(query)

    def add_challan(self, plate_number: str, reason: str, amount: float, status: str = "pending"):
        return add_challan(plate_number, reason, amount, status)

    def set_challan_status(self, challan_id: int, status: str):
        update_challan_status(challan_id, status)

    def remove_challan(self, challan_id: int):
        delete_challan(challan_id)

    def blacklist_add(self, plate_number: str, reason: str) -> bool:
        return add_to_blacklist(plate_number, reason)

    def blacklist_remove(self, plate_number: str):
        remove_from_blacklist(plate_number)

    def all_blacklisted(self):
        return list_blacklist()
