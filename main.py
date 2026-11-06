"""
FILE 2 OF 3: FASTAPI BACKEND SERVER (main.py)
=============================================
Save this file as: main.py (in the SAME folder as database.py and index.html)
Role: Connects to database.py (SQLite medconverge.db) and serves:
      - GET  /hospitals
      - GET  /equipment
      - POST /broadcast  (Runs T_converge = max(ETA_Amb->A, ETA_Equip_B->A + Setup) vs. ETA_Amb->B)
      - GET  /transfers
      - GET  /ledger
      - POST /reset
      - WS   /ws
Run command: uvicorn main:app --reload --port 8000
"""

import math
import random
from typing import List, Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import database

app = FastAPI(
    title="MedConverge FastAPI + SQLite Backend",
    description="Real-Time Critical Care Resource & Inter-Hospital Equipment Convergence API",
    version="2.4.0"
)

# Enable CORS so index.html can call http://localhost:8000 from any browser or port
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast_json(self, message: dict):
        for conn in self.active_connections:
            try:
                await conn.send_json(message)
            except Exception:
                pass


manager = ConnectionManager()


class BroadcastRequest(BaseModel):
    ambulance_code: str
    target_hospital_id: str
    ambulance_eta_mins: int
    direct_alt_hospital_id: Optional[str] = "H3"
    direct_alt_eta_mins: Optional[int] = 27
    needed_resource_keys: List[str]
    patient_condition: Optional[str] = "Critical Emergency Case"


@app.on_event("startup")
def on_startup():
    database.init_db()
    conn = database.get_connection()
    cnt = conn.execute("SELECT COUNT(*) as c FROM hospitals").fetchone()["c"]
    conn.close()
    if cnt == 0:
        database.reset_db()


def _format_hospital_row(conn, h_row) -> dict:
    h = dict(h_row)
    eq_rows = conn.execute("SELECT * FROM equipment WHERE hospital_id = ?", (h["id"],)).fetchall()
    eq_map = {}
    for eq in eq_rows:
        idle = max(0, eq["total_units"] - eq["in_use_units"])
        lendable = max(0, idle - eq["safety_par"])
        key_Map = {
            "portable_vent": "tier1_portable_vent",
            "oneg_blood": "tier1_oneg_blood",
            "ped_defib": "tier1_ped_defib",
            "antivenom": "tier1_antivenom",
            "icu_vent": "tier2_icu_vent"
        }
        mapped_key = key_Map.get(eq["resource_key"], eq["resource_key"])
        eq_map[mapped_key] = {
            "total": eq["total_units"],
            "in_use": eq["in_use_units"],
            "safety_par": eq["safety_par"],
            "idle": idle,
            "lendable_surplus": lendable
        }
    return {
        "id": h["id"],
        "name": h["name"],
        "zone": h["zone"],
        "x": h["x"],
        "y": h["y"],
        "icu_beds_total": h["icu_beds_total"],
        "icu_beds_ready": h["icu_beds_ready"],
        "nurse_ratio_ok": bool(h["nurse_ratio_ok"]),
        "o2_hours_left": h["o2_hours_left"],
        "specialist": h["specialist"],
        **eq_map,
        "tier3_cath_ecmo": {"available": bool(h["tier3_cath_ecmo"])}
    }


@app.get("/hospitals")
def get_hospitals():
    """Reads all 6 partner hospitals and their equipment counts from SQLite."""
    conn = database.get_connection()
    rows = conn.execute("SELECT * FROM hospitals ORDER BY id").fetchall()
    result = [_format_hospital_row(conn, r) for r in rows]
    conn.close()
    return result


@app.get("/equipment")
def get_equipment():
    """Returns all equipment records from SQLite with computed idle and lendable surplus."""
    conn = database.get_connection()
    rows = conn.execute("SELECT * FROM equipment ORDER BY hospital_id, tier").fetchall()
    result = []
    for r in rows:
        d = dict(r)
        idle = max(0, d["total_units"] - d["in_use_units"])
        d["idle_units"] = idle
        d["lendable_surplus"] = max(0, idle - d["safety_par"])
        result.append(d)
    conn.close()
    return result


@app.post("/broadcast")
async def evaluate_broadcast(req: BroadcastRequest):
    """
    Evaluates the Convergence Equation against live SQLite data:
    T_converge = max(ETA_Amb->A, ETA_Equip_B->A + Setup) vs. ETA_Amb->B
    Writes any new transfers and escrow tokens directly into SQLite.
    """
    conn = database.get_connection()
    target = conn.execute("SELECT * FROM hospitals WHERE id = ?", (req.target_hospital_id,)).fetchone()
    alt = conn.execute("SELECT * FROM hospitals WHERE id = ?", (req.direct_alt_hospital_id,)).fetchone()

    if not target or not alt:
        conn.close()
        raise HTTPException(status_code=404, detail="Target or Alternate hospital not found.")

    requires_immobile_reroute = False
    if "cath_ecmo" in req.needed_resource_keys and not bool(target["tier3_cath_ecmo"]):
        requires_immobile_reroute = True

    new_dispatches = []
    max_equip_arrival_with_setup = 0

    if not requires_immobile_reroute:
        for idx, res_key in enumerate(req.needed_resource_keys):
            if res_key == "cath_ecmo":
                continue

            target_eq = conn.execute(
                "SELECT * FROM equipment WHERE hospital_id = ? AND resource_key = ?",
                (req.target_hospital_id, res_key)
            ).fetchone()

            target_idle = max(0, target_eq["total_units"] - target_eq["in_use_units"]) if target_eq else 0
            force_pool = req.ambulance_code.startswith("MCI")

            if target_idle == 0 or force_pool:
                donors = conn.execute("""
                    SELECT h.id, h.name, h.x, h.y, eq.name as eq_name, eq.lease_rate, eq.setup_mins, eq.transport_mode,
                           (eq.total_units - eq.in_use_units - eq.safety_par) as lendable
                    FROM equipment eq
                    JOIN hospitals h ON eq.hospital_id = h.id
                    WHERE eq.resource_key = ? AND eq.hospital_id != ?
                      AND (eq.total_units - eq.in_use_units - eq.safety_par) > 0
                """, (res_key, req.target_hospital_id)).fetchall()

                candidates = []
                for d in donors:
                    dx = target["x"] - d["x"]
                    dy = target["y"] - d["y"]
                    px = math.sqrt(dx * dx + dy * dy)
                    transit = max(3, round(px / 38)) if "DRONE" in d["transport_mode"] else (
                        max(4, round(px / 28)) if "Bike" in d["transport_mode"] else max(7, round(px / 20))
                    )
                    candidates.append((transit + d["setup_mins"], transit, d))

                candidates.sort(key=lambda x: x[0])
                if candidates:
                    pick_i = min(idx, len(candidates) - 1)
                    total_time, transit_mins, chosen = candidates[pick_i]
                    max_equip_arrival_with_setup = max(max_equip_arrival_with_setup, total_time)

                    token_id = f"MCV-{random.randint(1000, 9999)}"
                    conn.execute("""
                        INSERT OR REPLACE INTO transfers
                        (token_id, ambulance_code, resource_key, donor_hospital_id, target_hospital_id, transport_mode, transit_mins, setup_mins, status)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'IN_FLIGHT')
                    """, (token_id, req.ambulance_code, res_key, chosen["id"], target["id"], chosen["transport_mode"], transit_mins, chosen["setup_mins"]))

                    conn.execute("""
                        INSERT OR REPLACE INTO ledger
                        (token_id, donor_hospital_id, target_hospital_id, resource_name, hourly_rate, hours_billed, total_credit, status)
                        VALUES (?, ?, ?, ?, ?, 1.0, ?, 'ACTIVE_ESCROW')
                    """, (token_id, chosen["id"], target["id"], chosen["eq_name"], chosen["lease_rate"], chosen["lease_rate"]))

                    new_dispatches.append({
                        "token_id": token_id,
                        "resource_key": res_key,
                        "resource_name": chosen["eq_name"],
                        "donor_id": chosen["id"],
                        "donor_name": chosen["name"],
                        "target_id": target["id"],
                        "target_name": target["name"],
                        "transport_mode": chosen["transport_mode"],
                        "transit_mins": transit_mins,
                        "setup_mins": chosen["setup_mins"],
                        "total_mins": total_time,
                        "lease_rate": chosen["lease_rate"],
                        "status": "IN-FLIGHT (LOCKED)"
                    })

    conn.commit()
    conn.close()

    converge_total_time = max(req.ambulance_eta_mins, max_equip_arrival_with_setup)
    time_saved = max(0, req.direct_alt_eta_mins - converge_total_time)

    payload = {
        "verdict": "AUTO_REROUTE_AMBULANCE" if requires_immobile_reroute else "CONVERGE_AT_NEAREST_HOSPITAL",
        "receiving_hospital": {
            "id": alt["id"] if requires_immobile_reroute else target["id"],
            "name": alt["name"] if requires_immobile_reroute else target["name"]
        },
        "formula": {
            "path_a_converge_mins": None if requires_immobile_reroute else converge_total_time,
            "path_b_reroute_mins": req.direct_alt_eta_mins,
            "max_equip_eta_with_setup_mins": max_equip_arrival_with_setup,
            "ambulance_eta_to_target_mins": req.ambulance_eta_mins,
            "golden_hour_mins_saved": 0 if requires_immobile_reroute else time_saved
        },
        "immobile_tier3_triggered": requires_immobile_reroute,
        "dispatches": new_dispatches
    }

    await manager.broadcast_json({"event": "NEW_EMERGENCY_BROADCAST", "ambulance_code": req.ambulance_code, "verdict": payload})
    return payload


@app.get("/transfers")
def get_transfers():
    """Reads all equipment transfers from SQLite."""
    conn = database.get_connection()
    rows = conn.execute("""
        SELECT t.*, d.name as donor_name, trg.name as target_name
        FROM transfers t
        JOIN hospitals d ON t.donor_hospital_id = d.id
        JOIN hospitals trg ON t.target_hospital_id = trg.id
        ORDER BY t.created_at DESC
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


@app.get("/ledger")
def get_ledger():
    """Reads the B2B custody token ledger from SQLite."""
    conn = database.get_connection()
    rows = conn.execute("""
        SELECT l.*, d.name as donor_name, trg.name as target_name
        FROM ledger l
        JOIN hospitals d ON l.donor_hospital_id = d.id
        JOIN hospitals trg ON l.target_hospital_id = trg.id
        ORDER BY l.token_id DESC
    """).fetchall()
    settled = conn.execute("SELECT SUM(total_credit) as s FROM ledger WHERE status = 'SETTLED'").fetchone()["s"] or 0
    conn.close()
    return {"total_settled_inr": settled, "entries": [dict(r) for r in rows]}


@app.post("/reset")
async def reset_demo():
    """Restores SQLite database to the initial seed state for demos."""
    database.reset_db()
    await manager.broadcast_json({"event": "SYSTEM_RESET"})
    return {"status": "success", "message": "SQLite database restored to initial seed data."}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        await websocket.send_json({"event": "CONNECTED", "message": "MedConverge WebSocket Live"})
        while True:
            msg = await websocket.receive_text()
            await websocket.send_json({"event": "PONG", "echo": msg})
    except WebSocketDisconnect:
        manager.disconnect(websocket)