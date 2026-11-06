"""
FILE 1 OF 3: DATABASE LAYER (database.py)
=========================================
Save this file as: database.py (in your main project folder)
Role: Creates the SQLite database (medconverge.db), defines the 5 tables
      (hospitals, equipment, ambulances, transfers, ledger), and seeds
      the 6 Bengaluru partner hospitals with the fixed deficit counts.
"""

import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "medconverge.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


SEED_HOSPITALS = [
    {
        "id": "H1",
        "name": "Victoria Trauma Center",
        "zone": "Central (KR Market)",
        "x": 340,
        "y": 260,
        "icu_beds_total": 16,
        "icu_beds_ready": 3,
        "nurse_ratio_ok": 1,
        "o2_hours_left": 18.5,
        "specialist": "Trauma & Ortho On-Site",
        "tier3_cath_ecmo": 0
    },
    {
        "id": "H2",
        "name": "Bowring & Lady Curzon",
        "zone": "Shivajinagar (3.8 km)",
        "x": 420,
        "y": 145,
        "icu_beds_total": 12,
        "icu_beds_ready": 2,
        "nurse_ratio_ok": 1,
        "o2_hours_left": 22.0,
        "specialist": "General Critical Care",
        "tier3_cath_ecmo": 0
    },
    {
        "id": "H3",
        "name": "St. John's Medical College",
        "zone": "Koramangala (5.2 km)",
        "x": 495,
        "y": 355,
        "icu_beds_total": 18,
        "icu_beds_ready": 5,
        "nurse_ratio_ok": 1,
        "o2_hours_left": 31.0,
        "specialist": "Neuro-Trauma & Burns",
        "tier3_cath_ecmo": 1
    },
    {
        "id": "H4",
        "name": "Manipal Hospital",
        "zone": "Old Airport Rd (7.4 km)",
        "x": 615,
        "y": 235,
        "icu_beds_total": 14,
        "icu_beds_ready": 6,
        "nurse_ratio_ok": 1,
        "o2_hours_left": 27.5,
        "specialist": "Cardiac & ECMO Team",
        "tier3_cath_ecmo": 1
    },
    {
        "id": "H5",
        "name": "Aster CMI Hospital",
        "zone": "Hebbal North (9.1 km)",
        "x": 365,
        "y": 65,
        "icu_beds_total": 10,
        "icu_beds_ready": 4,
        "nurse_ratio_ok": 1,
        "o2_hours_left": 24.0,
        "specialist": "Pediatric Neuro-ICU",
        "tier3_cath_ecmo": 1
    },
    {
        "id": "H6",
        "name": "Narayana Health City",
        "zone": "Electronic City (14 km)",
        "x": 650,
        "y": 430,
        "icu_beds_total": 18,
        "icu_beds_ready": 4,
        "nurse_ratio_ok": 1,
        "o2_hours_left": 36.0,
        "specialist": "24x7 Cardiac Cath & ECMO",
        "tier3_cath_ecmo": 1
    }
]

# Note: H1 has 6/6 portable_vent in_use and 4/4 oneg_blood in_use (0 idle),
# and H2 has 2/2 ped_defib in_use (0 idle) so Case 1 and Case 2 trigger live dispatches!
SEED_EQUIPMENT = [
    # H1 (Victoria Trauma Center — Deficit in Portable Vent, O-Neg Blood, Ped Defib, Full ICU Vent)
    {"hospital_id": "H1", "resource_key": "portable_vent", "name": "Portable Transport Ventilator (Hamilton-T1)", "tier": 1, "total_units": 6, "in_use_units": 6, "safety_par": 1, "lease_rate": 4500, "setup_mins": 3, "transport_mode": "Green-Corridor Bike Responder"},
    {"hospital_id": "H1", "resource_key": "oneg_blood", "name": "O-Negative Packed RBC (2 Units)", "tier": 1, "total_units": 4, "in_use_units": 4, "safety_par": 1, "lease_rate": 3200, "setup_mins": 2, "transport_mode": "ICMR i-DRONE Cold-Chain Pod"},
    {"hospital_id": "H1", "resource_key": "ped_defib", "name": "Pediatric Defibrillator & Syringe Pump Kit", "tier": 1, "total_units": 3, "in_use_units": 3, "safety_par": 1, "lease_rate": 3800, "setup_mins": 2, "transport_mode": "ICMR i-DRONE Medical Sortie"},
    {"hospital_id": "H1", "resource_key": "antivenom", "name": "Polyvalent Snake Antivenom (10 Vials)", "tier": 1, "total_units": 5, "in_use_units": 2, "safety_par": 1, "lease_rate": 2900, "setup_mins": 1, "transport_mode": "ICMR i-DRONE Sortie"},
    {"hospital_id": "H1", "resource_key": "icu_vent", "name": "Full-Size Servo-U ICU Mechanical Ventilator", "tier": 2, "total_units": 14, "in_use_units": 14, "safety_par": 2, "lease_rate": 8500, "setup_mins": 5, "transport_mode": "Green-Corridor Biomedical Van"},

    # H2 (Bowring & Lady Curzon — Surplus Portable Vents & Blood; Deficit in Ped Defib)
    {"hospital_id": "H2", "resource_key": "portable_vent", "name": "Portable Transport Ventilator (Hamilton-T1)", "tier": 1, "total_units": 7, "in_use_units": 3, "safety_par": 2, "lease_rate": 4500, "setup_mins": 3, "transport_mode": "Green-Corridor Bike Responder"},
    {"hospital_id": "H2", "resource_key": "oneg_blood", "name": "O-Negative Packed RBC (2 Units)", "tier": 1, "total_units": 9, "in_use_units": 2, "safety_par": 2, "lease_rate": 3200, "setup_mins": 2, "transport_mode": "ICMR i-DRONE Cold-Chain Pod"},
    {"hospital_id": "H2", "resource_key": "ped_defib", "name": "Pediatric Defibrillator & Syringe Pump Kit", "tier": 1, "total_units": 2, "in_use_units": 2, "safety_par": 1, "lease_rate": 3800, "setup_mins": 2, "transport_mode": "ICMR i-DRONE Medical Sortie"},
    {"hospital_id": "H2", "resource_key": "antivenom", "name": "Polyvalent Snake Antivenom (10 Vials)", "tier": 1, "total_units": 8, "in_use_units": 1, "safety_par": 2, "lease_rate": 2900, "setup_mins": 1, "transport_mode": "ICMR i-DRONE Sortie"},
    {"hospital_id": "H2", "resource_key": "icu_vent", "name": "Full-Size Servo-U ICU Mechanical Ventilator", "tier": 2, "total_units": 10, "in_use_units": 6, "safety_par": 2, "lease_rate": 8500, "setup_mins": 5, "transport_mode": "Green-Corridor Biomedical Van"},

    # H3 (St. John's Medical College — Surplus across all tiers + Fixed Cath/ECMO)
    {"hospital_id": "H3", "resource_key": "portable_vent", "name": "Portable Transport Ventilator (Hamilton-T1)", "tier": 1, "total_units": 10, "in_use_units": 4, "safety_par": 2, "lease_rate": 4500, "setup_mins": 3, "transport_mode": "Green-Corridor Bike Responder"},
    {"hospital_id": "H3", "resource_key": "oneg_blood", "name": "O-Negative Packed RBC (2 Units)", "tier": 1, "total_units": 11, "in_use_units": 4, "safety_par": 2, "lease_rate": 3200, "setup_mins": 2, "transport_mode": "ICMR i-DRONE Cold-Chain Pod"},
    {"hospital_id": "H3", "resource_key": "ped_defib", "name": "Pediatric Defibrillator & Syringe Pump Kit", "tier": 1, "total_units": 6, "in_use_units": 2, "safety_par": 1, "lease_rate": 3800, "setup_mins": 2, "transport_mode": "ICMR i-DRONE Medical Sortie"},
    {"hospital_id": "H3", "resource_key": "antivenom", "name": "Polyvalent Snake Antivenom (10 Vials)", "tier": 1, "total_units": 6, "in_use_units": 2, "safety_par": 1, "lease_rate": 2900, "setup_mins": 1, "transport_mode": "ICMR i-DRONE Sortie"},
    {"hospital_id": "H3", "resource_key": "icu_vent", "name": "Full-Size Servo-U ICU Mechanical Ventilator", "tier": 2, "total_units": 16, "in_use_units": 10, "safety_par": 2, "lease_rate": 8500, "setup_mins": 5, "transport_mode": "Green-Corridor Biomedical Van"},

    # H4 (Manipal Hospital)
    {"hospital_id": "H4", "resource_key": "portable_vent", "name": "Portable Transport Ventilator (Hamilton-T1)", "tier": 1, "total_units": 9, "in_use_units": 4, "safety_par": 2, "lease_rate": 4500, "setup_mins": 3, "transport_mode": "Green-Corridor Bike Responder"},
    {"hospital_id": "H4", "resource_key": "oneg_blood", "name": "O-Negative Packed RBC (2 Units)", "tier": 1, "total_units": 8, "in_use_units": 3, "safety_par": 2, "lease_rate": 3200, "setup_mins": 2, "transport_mode": "ICMR i-DRONE Cold-Chain Pod"},
    {"hospital_id": "H4", "resource_key": "ped_defib", "name": "Pediatric Defibrillator & Syringe Pump Kit", "tier": 1, "total_units": 5, "in_use_units": 1, "safety_par": 1, "lease_rate": 3800, "setup_mins": 2, "transport_mode": "ICMR i-DRONE Medical Sortie"},
    {"hospital_id": "H4", "resource_key": "antivenom", "name": "Polyvalent Snake Antivenom (10 Vials)", "tier": 1, "total_units": 4, "in_use_units": 1, "safety_par": 1, "lease_rate": 2900, "setup_mins": 1, "transport_mode": "ICMR i-DRONE Sortie"},
    {"hospital_id": "H4", "resource_key": "icu_vent", "name": "Full-Size Servo-U ICU Mechanical Ventilator", "tier": 2, "total_units": 15, "in_use_units": 9, "safety_par": 2, "lease_rate": 8500, "setup_mins": 5, "transport_mode": "Green-Corridor Biomedical Van"},

    # H5 (Aster CMI Hospital)
    {"hospital_id": "H5", "resource_key": "portable_vent", "name": "Portable Transport Ventilator (Hamilton-T1)", "tier": 1, "total_units": 8, "in_use_units": 3, "safety_par": 2, "lease_rate": 4500, "setup_mins": 3, "transport_mode": "Green-Corridor Bike Responder"},
    {"hospital_id": "H5", "resource_key": "oneg_blood", "name": "O-Negative Packed RBC (2 Units)", "tier": 1, "total_units": 7, "in_use_units": 2, "safety_par": 2, "lease_rate": 3200, "setup_mins": 2, "transport_mode": "ICMR i-DRONE Cold-Chain Pod"},
    {"hospital_id": "H5", "resource_key": "ped_defib", "name": "Pediatric Defibrillator & Syringe Pump Kit", "tier": 1, "total_units": 7, "in_use_units": 2, "safety_par": 1, "lease_rate": 3800, "setup_mins": 2, "transport_mode": "ICMR i-DRONE Medical Sortie"},
    {"hospital_id": "H5", "resource_key": "antivenom", "name": "Polyvalent Snake Antivenom (10 Vials)", "tier": 1, "total_units": 5, "in_use_units": 1, "safety_par": 1, "lease_rate": 2900, "setup_mins": 1, "transport_mode": "ICMR i-DRONE Sortie"},
    {"hospital_id": "H5", "resource_key": "icu_vent", "name": "Full-Size Servo-U ICU Mechanical Ventilator", "tier": 2, "total_units": 12, "in_use_units": 7, "safety_par": 2, "lease_rate": 8500, "setup_mins": 5, "transport_mode": "Green-Corridor Biomedical Van"},

    # H6 (Narayana Health City)
    {"hospital_id": "H6", "resource_key": "portable_vent", "name": "Portable Transport Ventilator (Hamilton-T1)", "tier": 1, "total_units": 11, "in_use_units": 5, "safety_par": 2, "lease_rate": 4500, "setup_mins": 3, "transport_mode": "Green-Corridor Bike Responder"},
    {"hospital_id": "H6", "resource_key": "oneg_blood", "name": "O-Negative Packed RBC (2 Units)", "tier": 1, "total_units": 12, "in_use_units": 4, "safety_par": 2, "lease_rate": 3200, "setup_mins": 2, "transport_mode": "ICMR i-DRONE Cold-Chain Pod"},
    {"hospital_id": "H6", "resource_key": "ped_defib", "name": "Pediatric Defibrillator & Syringe Pump Kit", "tier": 1, "total_units": 5, "in_use_units": 2, "safety_par": 1, "lease_rate": 3800, "setup_mins": 2, "transport_mode": "ICMR i-DRONE Medical Sortie"},
    {"hospital_id": "H6", "resource_key": "antivenom", "name": "Polyvalent Snake Antivenom (10 Vials)", "tier": 1, "total_units": 6, "in_use_units": 2, "safety_par": 1, "lease_rate": 2900, "setup_mins": 1, "transport_mode": "ICMR i-DRONE Sortie"},
    {"hospital_id": "H6", "resource_key": "icu_vent", "name": "Full-Size Servo-U ICU Mechanical Ventilator", "tier": 2, "total_units": 18, "in_use_units": 11, "safety_par": 2, "lease_rate": 8500, "setup_mins": 5, "transport_mode": "Green-Corridor Biomedical Van"}
]

SEED_AMBULANCES = [
    {"code": "EMS-108-BLR42", "current_x": 145, "current_y": 335, "status": "EN_ROUTE", "patient_condition": "34M Crush Trauma • SpO2 81% • Needs ICU Bed + Portable Vent + 2u O-Neg Blood", "target_hospital_id": "H1", "eta_mins": 9},
    {"code": "EMS-108-BLR19", "current_x": 210, "current_y": 135, "status": "EN_ROUTE", "patient_condition": "7F High-Velocity RTA • Needs PICU Bed + Pediatric Defibrillator/Pump + Tele-ICU", "target_hospital_id": "H2", "eta_mins": 10},
    {"code": "EMS-108-BLR88", "current_x": 235, "current_y": 395, "status": "DIVERTED", "patient_condition": "58M STEMI Shock • Needs Fixed Cath Lab & ECMO (Tier 3 Immobile)", "target_hospital_id": "H3", "eta_mins": 16},
    {"code": "MCI-COMMAND-01", "current_x": 155, "current_y": 225, "status": "SURGE_ACTIVE", "patient_condition": "Highway Pile-Up (8 Critical Victims) • Multi-Hospital Ventilator & Blood Pooling", "target_hospital_id": "H1", "eta_mins": 11}
]

SEED_TRANSFERS = [
    {"token_id": "MCV-4812", "ambulance_code": "EMS-108-BLR42", "resource_key": "portable_vent", "donor_hospital_id": "H2", "target_hospital_id": "H1", "transport_mode": "Green-Corridor Bike Responder", "transit_mins": 4, "setup_mins": 3, "status": "IN_FLIGHT"},
    {"token_id": "MCV-4819", "ambulance_code": "EMS-108-BLR42", "resource_key": "oneg_blood", "donor_hospital_id": "H3", "target_hospital_id": "H1", "transport_mode": "ICMR i-DRONE Cold-Chain Pod", "transit_mins": 4, "setup_mins": 2, "status": "IN_FLIGHT"}
]

SEED_LEDGER = [
    {"token_id": "MCV-4812", "donor_hospital_id": "H2", "target_hospital_id": "H1", "resource_name": "Portable Transport Ventilator (Hamilton-T1)", "hourly_rate": 4500, "hours_billed": 1.0, "total_credit": 4500, "status": "ACTIVE_ESCROW"},
    {"token_id": "MCV-4819", "donor_hospital_id": "H3", "target_hospital_id": "H1", "resource_name": "O-Negative Packed RBC (2 Units)", "hourly_rate": 3200, "hours_billed": 1.0, "total_credit": 3200, "status": "ACTIVE_ESCROW"},
    {"token_id": "MCV-3105", "donor_hospital_id": "H4", "target_hospital_id": "H3", "resource_name": "Full-Size Servo-U ICU Mechanical Ventilator", "hourly_rate": 8500, "hours_billed": 4.0, "total_credit": 34000, "status": "SETTLED"}
]


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS hospitals (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        zone TEXT NOT NULL,
        x INTEGER NOT NULL,
        y INTEGER NOT NULL,
        icu_beds_total INTEGER NOT NULL,
        icu_beds_ready INTEGER NOT NULL,
        nurse_ratio_ok INTEGER NOT NULL DEFAULT 1,
        o2_hours_left REAL NOT NULL,
        specialist TEXT NOT NULL,
        tier3_cath_ecmo INTEGER NOT NULL DEFAULT 0
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS equipment (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        hospital_id TEXT NOT NULL,
        resource_key TEXT NOT NULL,
        name TEXT NOT NULL,
        tier INTEGER NOT NULL,
        total_units INTEGER NOT NULL,
        in_use_units INTEGER NOT NULL,
        safety_par INTEGER NOT NULL,
        lease_rate INTEGER NOT NULL,
        setup_mins INTEGER NOT NULL,
        transport_mode TEXT NOT NULL,
        FOREIGN KEY (hospital_id) REFERENCES hospitals(id) ON DELETE CASCADE,
        UNIQUE(hospital_id, resource_key)
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS ambulances (
        code TEXT PRIMARY KEY,
        current_x INTEGER NOT NULL,
        current_y INTEGER NOT NULL,
        status TEXT NOT NULL,
        patient_condition TEXT NOT NULL,
        target_hospital_id TEXT,
        eta_mins INTEGER NOT NULL,
        FOREIGN KEY (target_hospital_id) REFERENCES hospitals(id)
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS transfers (
        token_id TEXT PRIMARY KEY,
        ambulance_code TEXT,
        resource_key TEXT NOT NULL,
        donor_hospital_id TEXT NOT NULL,
        target_hospital_id TEXT NOT NULL,
        transport_mode TEXT NOT NULL,
        transit_mins INTEGER NOT NULL,
        setup_mins INTEGER NOT NULL,
        status TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (donor_hospital_id) REFERENCES hospitals(id),
        FOREIGN KEY (target_hospital_id) REFERENCES hospitals(id)
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS ledger (
        token_id TEXT PRIMARY KEY,
        donor_hospital_id TEXT NOT NULL,
        target_hospital_id TEXT NOT NULL,
        resource_name TEXT NOT NULL,
        hourly_rate INTEGER NOT NULL,
        hours_billed REAL NOT NULL DEFAULT 1.0,
        total_credit INTEGER NOT NULL,
        status TEXT NOT NULL,
        settled_at TIMESTAMP,
        FOREIGN KEY (donor_hospital_id) REFERENCES hospitals(id),
        FOREIGN KEY (target_hospital_id) REFERENCES hospitals(id)
    );
    """)

    conn.commit()
    conn.close()


def reset_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM ledger;")
    cur.execute("DELETE FROM transfers;")
    cur.execute("DELETE FROM ambulances;")
    cur.execute("DELETE FROM equipment;")
    cur.execute("DELETE FROM hospitals;")

    for h in SEED_HOSPITALS:
        cur.execute("""
        INSERT INTO hospitals (id, name, zone, x, y, icu_beds_total, icu_beds_ready, nurse_ratio_ok, o2_hours_left, specialist, tier3_cath_ecmo)
        VALUES (:id, :name, :zone, :x, :y, :icu_beds_total, :icu_beds_ready, :nurse_ratio_ok, :o2_hours_left, :specialist, :tier3_cath_ecmo);
        """, h)

    for eq in SEED_EQUIPMENT:
        cur.execute("""
        INSERT INTO equipment (hospital_id, resource_key, name, tier, total_units, in_use_units, safety_par, lease_rate, setup_mins, transport_mode)
        VALUES (:hospital_id, :resource_key, :name, :tier, :total_units, :in_use_units, :safety_par, :lease_rate, :setup_mins, :transport_mode);
        """, eq)

    for amb in SEED_AMBULANCES:
        cur.execute("""
        INSERT INTO ambulances (code, current_x, current_y, status, patient_condition, target_hospital_id, eta_mins)
        VALUES (:code, :current_x, :current_y, :status, :patient_condition, :target_hospital_id, :eta_mins);
        """, amb)

    for tr in SEED_TRANSFERS:
        cur.execute("""
        INSERT INTO transfers (token_id, ambulance_code, resource_key, donor_hospital_id, target_hospital_id, transport_mode, transit_mins, setup_mins, status)
        VALUES (:token_id, :ambulance_code, :resource_key, :donor_hospital_id, :target_hospital_id, :transport_mode, :transit_mins, :setup_mins, :status);
        """, tr)

    for ld in SEED_LEDGER:
        cur.execute("""
        INSERT INTO ledger (token_id, donor_hospital_id, target_hospital_id, resource_name, hourly_rate, hours_billed, total_credit, status)
        VALUES (:token_id, :donor_hospital_id, :target_hospital_id, :resource_name, :hourly_rate, :hours_billed, :total_credit, :status);
        """, ld)

    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
    reset_db()
    print("Database (medconverge.db) initialized and seeded successfully!")