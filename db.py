"""
db.py - SQLite Database manager for EcoAgent audit history and analytics.
Stores structured audit profiles, recommendations, and impact savings locally.
"""

import sqlite3
import json
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ecoagent.db")


def init_db():
    """Initialize SQLite database tables if they do not exist."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS audits (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        user_name TEXT,
        property_type TEXT,
        occupants INTEGER,
        city_state TEXT,
        monthly_kwh REAL,
        monthly_bill REAL,
        water_lpcd REAL,
        waste_kg_day REAL,
        segregates_waste INTEGER,
        has_solar INTEGER,
        profile_json TEXT,
        recommendations_json TEXT,
        impact_json TEXT,
        annual_savings_inr REAL,
        annual_co2_kg REAL
    )
    """)
    conn.commit()
    conn.close()


def save_audit(user_name: str, property_type: str, occupants: int, city_state: str,
               monthly_kwh: float, monthly_bill: float, water_lpcd: float, waste_kg_day: float,
               segregates_waste: bool, has_solar: bool, profile: dict,
               recommendations: list, impact: dict) -> int:
    """Save a complete sustainability audit run to SQLite."""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    annual_savings_inr = impact.get("summary", {}).get("total_annual_cost_savings_inr", 0.0)
    annual_co2_kg = impact.get("summary", {}).get("total_annual_co2_reduction_kg", 0.0)
    
    cursor.execute("""
    INSERT INTO audits (
        timestamp, user_name, property_type, occupants, city_state,
        monthly_kwh, monthly_bill, water_lpcd, waste_kg_day,
        segregates_waste, has_solar, profile_json, recommendations_json,
        impact_json, annual_savings_inr, annual_co2_kg
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        timestamp, user_name, property_type, occupants, city_state,
        monthly_kwh, monthly_bill, water_lpcd, waste_kg_day,
        1 if segregates_waste else 0,
        1 if has_solar else 0,
        json.dumps(profile),
        json.dumps(recommendations),
        json.dumps(impact),
        annual_savings_inr,
        annual_co2_kg
    ))
    audit_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return audit_id


def get_all_audits(limit: int = 50):
    """Retrieve historical audits from SQLite."""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
    SELECT id, timestamp, user_name, property_type, occupants, city_state,
           monthly_kwh, monthly_bill, annual_savings_inr, annual_co2_kg
    FROM audits ORDER BY id DESC LIMIT ?
    """, (limit,))
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows


def get_community_impact():
    """Aggregates total community impact across all stored audits."""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
    SELECT COUNT(*), SUM(annual_savings_inr), SUM(annual_co2_kg)
    FROM audits
    """)
    row = cursor.fetchone()
    conn.close()
    
    total_audits = row[0] if row and row[0] else 0
    total_savings = row[1] if row and row[1] else 0.0
    total_co2 = row[2] if row and row[2] else 0.0
    
    return {
        "total_audits": total_audits,
        "total_annual_savings_inr": total_savings,
        "total_annual_co2_kg": total_co2,
        "trees_equivalent": round(total_co2 / 21.77, 1)
    }


if __name__ == "__main__":
    init_db()
    print("Database initialized at", DB_PATH)
