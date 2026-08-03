"""SQLite persistence layer for detections."""
import os
import sqlite3
import threading
from datetime import datetime
from config.settings import BASE_DIR
from utils.logger import logger

DB_PATH = os.path.join(BASE_DIR, "database", "anpr.db")
_lock = threading.Lock()

SCHEMA = """
CREATE TABLE IF NOT EXISTS detections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plate_number TEXT NOT NULL,
    ocr_confidence REAL,
    detection_confidence REAL,
    detection_time TEXT NOT NULL,
    image_path TEXT,
    source TEXT,
    status TEXT,
    remarks TEXT
);
CREATE INDEX IF NOT EXISTS idx_plate_number ON detections(plate_number);
CREATE INDEX IF NOT EXISTS idx_detection_time ON detections(detection_time);

CREATE TABLE IF NOT EXISTS vehicles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plate_number TEXT UNIQUE NOT NULL,
    owner_name TEXT,
    owner_phone TEXT,
    brand TEXT,
    model TEXT,
    vehicle_type TEXT,
    color TEXT,
    reg_state TEXT,
    rc_expiry TEXT,
    insurance_valid_till TEXT,
    puc_valid_till TEXT,
    authorized INTEGER DEFAULT 1,
    created_at TEXT
);
CREATE INDEX IF NOT EXISTS idx_vehicle_plate ON vehicles(plate_number);

CREATE TABLE IF NOT EXISTS challans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plate_number TEXT NOT NULL,
    challan_no TEXT,
    reason TEXT,
    amount REAL,
    issue_date TEXT,
    status TEXT DEFAULT 'pending'
);
CREATE INDEX IF NOT EXISTS idx_challan_plate ON challans(plate_number);

CREATE TABLE IF NOT EXISTS blacklist (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plate_number TEXT UNIQUE NOT NULL,
    reason TEXT,
    added_on TEXT
);
CREATE INDEX IF NOT EXISTS idx_blacklist_plate ON blacklist(plate_number);
"""


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with _lock:
        conn = get_connection()
        conn.executescript(SCHEMA)
        conn.commit()
        conn.close()
    logger.info(f"Database ready at {DB_PATH}")


def insert_detection(plate_number: str, ocr_confidence: float, detection_confidence: float,
                      image_path: str = "", source: str = "image", status: str = "valid",
                      remarks: str = "") -> int:
    with _lock:
        conn = get_connection()
        cur = conn.execute(
            """INSERT INTO detections
               (plate_number, ocr_confidence, detection_confidence, detection_time,
                image_path, source, status, remarks)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (plate_number, ocr_confidence, detection_confidence,
             datetime.now().isoformat(timespec="seconds"), image_path, source, status, remarks),
        )
        conn.commit()
        new_id = cur.lastrowid
        conn.close()
    return new_id


def search_detections(query: str = "", status: str = "all", limit: int = 500) -> list:
    sql = "SELECT * FROM detections WHERE 1=1"
    params = []
    if query:
        sql += " AND plate_number LIKE ?"
        params.append(f"%{query.upper()}%")
    if status != "all":
        sql += " AND status = ?"
        params.append(status)
    sql += " ORDER BY detection_time DESC LIMIT ?"
    params.append(limit)

    conn = get_connection()
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_all_detections(limit: int = 1000) -> list:
    return search_detections(limit=limit)


def delete_detection(detection_id: int) -> bool:
    with _lock:
        conn = get_connection()
        conn.execute("DELETE FROM detections WHERE id = ?", (detection_id,))
        conn.commit()
        conn.close()
    return True


def delete_all_detections() -> bool:
    with _lock:
        conn = get_connection()
        conn.execute("DELETE FROM detections")
        conn.commit()
        conn.close()
    return True


def get_stats() -> dict:
    conn = get_connection()
    total = conn.execute("SELECT COUNT(*) c FROM detections").fetchone()["c"]
    valid = conn.execute("SELECT COUNT(*) c FROM detections WHERE status = 'valid'").fetchone()["c"]
    invalid = total - valid
    today = datetime.now().strftime("%Y-%m-%d")
    today_count = conn.execute(
        "SELECT COUNT(*) c FROM detections WHERE detection_time LIKE ?", (f"{today}%",)
    ).fetchone()["c"]
    conn.close()
    return {"total": total, "valid": valid, "invalid": invalid, "today": today_count}


# ---------------------------------------------------------------------------
# Vehicles (vehicle master / "Vehicle Management System")
# ---------------------------------------------------------------------------

def upsert_vehicle(plate_number: str, owner_name: str = "", owner_phone: str = "", brand: str = "",
                    model: str = "", vehicle_type: str = "", color: str = "", reg_state: str = "",
                    rc_expiry: str = "", insurance_valid_till: str = "", puc_valid_till: str = "",
                    authorized: bool = True) -> None:
    plate_number = (plate_number or "").upper().strip()
    with _lock:
        conn = get_connection()
        existing = conn.execute("SELECT id FROM vehicles WHERE plate_number = ?", (plate_number,)).fetchone()
        if existing:
            conn.execute(
                """UPDATE vehicles SET owner_name=?, owner_phone=?, brand=?, model=?, vehicle_type=?,
                   color=?, reg_state=?, rc_expiry=?, insurance_valid_till=?, puc_valid_till=?, authorized=?
                   WHERE plate_number=?""",
                (owner_name, owner_phone, brand, model, vehicle_type, color, reg_state, rc_expiry,
                 insurance_valid_till, puc_valid_till, int(authorized), plate_number),
            )
        else:
            conn.execute(
                """INSERT INTO vehicles (plate_number, owner_name, owner_phone, brand, model, vehicle_type,
                   color, reg_state, rc_expiry, insurance_valid_till, puc_valid_till, authorized, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (plate_number, owner_name, owner_phone, brand, model, vehicle_type, color, reg_state,
                 rc_expiry, insurance_valid_till, puc_valid_till, int(authorized),
                 datetime.now().isoformat(timespec="seconds")),
            )
        conn.commit()
        conn.close()


def get_vehicle(plate_number: str):
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM vehicles WHERE plate_number = ?", ((plate_number or "").upper().strip(),)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def list_vehicles(query: str = "") -> list:
    conn = get_connection()
    if query:
        rows = conn.execute(
            "SELECT * FROM vehicles WHERE plate_number LIKE ? OR owner_name LIKE ? ORDER BY plate_number",
            (f"%{query.upper()}%", f"%{query}%"),
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM vehicles ORDER BY plate_number").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def delete_vehicle(plate_number: str) -> None:
    with _lock:
        conn = get_connection()
        conn.execute("DELETE FROM vehicles WHERE plate_number = ?", ((plate_number or "").upper().strip(),))
        conn.commit()
        conn.close()


def all_vehicle_plates() -> list:
    conn = get_connection()
    rows = conn.execute("SELECT plate_number FROM vehicles").fetchall()
    conn.close()
    return [r["plate_number"] for r in rows]


# ---------------------------------------------------------------------------
# Challans
# ---------------------------------------------------------------------------

def add_challan(plate_number: str, reason: str, amount: float, status: str = "pending",
                 challan_no: str = "") -> int:
    plate_number = (plate_number or "").upper().strip()
    with _lock:
        conn = get_connection()
        cur = conn.execute(
            """INSERT INTO challans (plate_number, challan_no, reason, amount, issue_date, status)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (plate_number, challan_no or f"CHL{uuid_suffix()}", reason, amount,
             datetime.now().strftime("%Y-%m-%d"), status),
        )
        conn.commit()
        new_id = cur.lastrowid
        conn.close()
    return new_id


def get_challans(plate_number: str) -> list:
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM challans WHERE plate_number = ? ORDER BY issue_date DESC",
        ((plate_number or "").upper().strip(),),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def update_challan_status(challan_id: int, status: str) -> None:
    with _lock:
        conn = get_connection()
        conn.execute("UPDATE challans SET status = ? WHERE id = ?", (status, challan_id))
        conn.commit()
        conn.close()


def delete_challan(challan_id: int) -> None:
    with _lock:
        conn = get_connection()
        conn.execute("DELETE FROM challans WHERE id = ?", (challan_id,))
        conn.commit()
        conn.close()


def uuid_suffix() -> str:
    import uuid
    return uuid.uuid4().hex[:6].upper()


# ---------------------------------------------------------------------------
# Blacklist
# ---------------------------------------------------------------------------

def add_to_blacklist(plate_number: str, reason: str) -> bool:
    plate_number = (plate_number or "").upper().strip()
    try:
        with _lock:
            conn = get_connection()
            conn.execute(
                "INSERT INTO blacklist (plate_number, reason, added_on) VALUES (?, ?, ?)",
                (plate_number, reason, datetime.now().strftime("%Y-%m-%d")),
            )
            conn.commit()
            conn.close()
        return True
    except sqlite3.IntegrityError:
        return False


def remove_from_blacklist(plate_number: str) -> None:
    with _lock:
        conn = get_connection()
        conn.execute("DELETE FROM blacklist WHERE plate_number = ?", ((plate_number or "").upper().strip(),))
        conn.commit()
        conn.close()


def is_blacklisted(plate_number: str):
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM blacklist WHERE plate_number = ?", ((plate_number or "").upper().strip(),)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def list_blacklist() -> list:
    conn = get_connection()
    rows = conn.execute("SELECT * FROM blacklist ORDER BY added_on DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ---------------------------------------------------------------------------
# Demo data seeding — runs once, only if the tables are empty
# ---------------------------------------------------------------------------

def seed_demo_data():
    if list_vehicles():
        return  # demo vehicles already seeded (or user has real data now)

    demo_vehicles = [
        ("KA01AB1234", "Rahul Sharma", "9845012345", "Hyundai", "Creta", "SUV", "White", "Karnataka",
         "2027-05-10", "2026-11-20", "2026-09-15", True),
        ("KA05MJ4589", "Priya Nair", "9900112233", "Honda", "City", "Sedan", "Silver", "Karnataka",
         "2026-08-01", "2026-04-01", "2026-05-01", False),
        ("MH12DE1433", "Aditya Kulkarni", "9822334455", "Maruti Suzuki", "Swift", "Hatchback", "Red", "Maharashtra",
         "2028-01-15", "2027-01-01", "2026-12-01", True),
        ("DL8CAF5678", "Simran Kaur", "9871122334", "Toyota", "Innova Crysta", "MUV", "Black", "Delhi",
         "2027-09-09", "2026-10-10", "2026-08-20", True),
        ("TN09BZ0007", "Karthik Raja", "9944556677", "Royal Enfield", "Classic 350", "Motorcycle", "Green", "Tamil Nadu",
         "2026-03-01", "2025-12-01", "2025-11-01", False),
        ("AP09CJ2020", "Lakshmi Reddy", "9866778899", "Tata", "Nexon", "SUV", "Blue", "Andhra Pradesh",
         "2027-07-07", "2026-06-06", "2026-06-06", True),
    ]
    for v in demo_vehicles:
        upsert_vehicle(*v)

    add_challan("KA05MJ4589", "Signal jump (red light violation)", 1000)
    add_challan("KA05MJ4589", "No parking zone", 500)
    add_challan("TN09BZ0007", "Riding without helmet", 500)
    add_challan("AP09CJ2020", "Overspeeding", 1500, status="paid")

    add_to_blacklist("TN09BZ0007", "Reported stolen — pending police verification")


init_db()
seed_demo_data()
