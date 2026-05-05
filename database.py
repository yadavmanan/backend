from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

DB_PATH = Path(__file__).resolve().parent / "patients.db"


def _connect() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db() -> None:
    with _connect() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS patients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                age INTEGER,
                sex TEXT,
                life_stage TEXT,
                phone TEXT,
                status TEXT DEFAULT 'pending',
                resting_blood_pressure REAL,
                cholestoral REAL,
                oldpeak REAL,
                max_heart_rate REAL,
                chest_pain_type TEXT,
                fasting_blood_sugar TEXT,
                rest_ecg TEXT,
                exercise_induced_angina TEXT,
                slope TEXT,
                vessels TEXT,
                thalassemia TEXT,
                hdl REAL,
                ldl REAL,
                triglycerides REAL,
                hba1c REAL,
                hs_crp REAL,
                serum_creatinine REAL,
                tsh REAL,
                bmi REAL,
                waist_circumference REAL,
                spo2 REAL,
                resting_pulse_rate REAL,
                smoking_status TEXT,
                family_history TEXT,
                current_medications TEXT,
                risk_score REAL,
                risk_level TEXT,
                gap_count INTEGER,
                analysis_json TEXT,
                call_sid TEXT,
                call_status TEXT,
                symptom_report_json TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        connection.commit()


def _row_to_dict(row: sqlite3.Row | None) -> dict[str, Any] | None:
    if row is None:
        return None
    data = dict(row)
    for key in ["analysis_json", "symptom_report_json"]:
        if data.get(key):
            try:
                data[key] = json.loads(data[key])
            except json.JSONDecodeError:
                pass
    return data


def add_patient(data: dict[str, Any]) -> int:
    with _connect() as connection:
        cursor = connection.execute(
            """
            INSERT INTO patients (name, age, sex, life_stage, phone, status)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                data["name"],
                data.get("age"),
                data.get("sex"),
                data.get("life_stage"),
                data.get("phone"),
                data.get("status", "pending"),
            ),
        )
        connection.commit()
        return int(cursor.lastrowid)


def get_patients() -> list[dict[str, Any]]:
    with _connect() as connection:
        rows = connection.execute(
            """
            SELECT id, name, age, sex, phone, status, risk_score, risk_level,
                   gap_count, call_status, created_at
            FROM patients
            ORDER BY created_at DESC, id DESC
            """
        ).fetchall()
    return [dict(row) for row in rows]


def get_patient(patient_id: int) -> dict[str, Any] | None:
    with _connect() as connection:
        row = connection.execute(
            "SELECT * FROM patients WHERE id = ?",
            (patient_id,),
        ).fetchone()
    return _row_to_dict(row)


def update_patient(patient_id: int, data: dict[str, Any]) -> None:
    if not data:
        return

    payload = dict(data)
    for key in ["analysis_json", "symptom_report_json"]:
        if key in payload and payload[key] is not None and not isinstance(payload[key], str):
            payload[key] = json.dumps(payload[key])

    columns = [f"{key} = ?" for key in payload]
    values = list(payload.values())
    values.append(patient_id)
    query = (
        f"UPDATE patients SET {', '.join(columns)}, updated_at = CURRENT_TIMESTAMP "
        "WHERE id = ?"
    )
    with _connect() as connection:
        connection.execute(query, values)
        connection.commit()