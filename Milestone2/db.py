"""
db.py — SQLite layer for FreightQuote AI (Milestone 2)
Handles: users table (with progressive lockout fields), otp table,
ml_models table (for the Admin > ML Model Card tab).
"""

import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "freightquote.db")


def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    cur = conn.cursor()

    # --- users table -------------------------------------------------
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'Logistics Manager',
            failed_attempts INTEGER DEFAULT 0,
            lock_until TIMESTAMP DEFAULT NULL,
            account_status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Migration-safe: add columns if an older Milestone1 DB is reused
    existing_cols = [r[1] for r in cur.execute("PRAGMA table_info(users)").fetchall()]
    for col, ddl in [
        ("failed_attempts", "ALTER TABLE users ADD COLUMN failed_attempts INTEGER DEFAULT 0"),
        ("lock_until", "ALTER TABLE users ADD COLUMN lock_until TIMESTAMP DEFAULT NULL"),
        ("account_status", "ALTER TABLE users ADD COLUMN account_status TEXT DEFAULT 'active'"),
        ("security_question", "ALTER TABLE users ADD COLUMN security_question TEXT DEFAULT NULL"),
        ("security_answer_hash", "ALTER TABLE users ADD COLUMN security_answer_hash TEXT DEFAULT NULL"),
    ]:
        if col not in existing_cols:
            cur.execute(ddl)

    # --- otp table (Gmail OTP + resend cooldown tracking) ------------
    cur.execute("""
        CREATE TABLE IF NOT EXISTS otp_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            otp_code TEXT NOT NULL,
            purpose TEXT DEFAULT 'reset',
            resend_count INTEGER DEFAULT 0,
            next_allowed TIMESTAMP DEFAULT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            verified INTEGER DEFAULT 0
        )
    """)

    # --- ml_models table (Admin > ML Model Card tab) ------------------
    cur.execute("""
        CREATE TABLE IF NOT EXISTS ml_models (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent_name TEXT NOT NULL,
            algorithm TEXT NOT NULL,
            metric_name TEXT NOT NULL,
            metric_value REAL NOT NULL,
            is_champion INTEGER DEFAULT 0,
            trained_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # --- copilot query log (Admin > LLM Activity Monitor) -------------
    cur.execute("""
        CREATE TABLE IF NOT EXISTS copilot_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            prompt TEXT NOT NULL,
            response TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


def seed_admin(admin_email: str, admin_password_hash: str, username: str = "Administrator"):
    """Bootstrap the default Admin account on first run (Section 9)."""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id FROM users WHERE email = ?", (admin_email,))
    if cur.fetchone() is None:
        cur.execute(
            "INSERT INTO users (username, email, password_hash, role, account_status) "
            "VALUES (?, ?, ?, 'Admin', 'active')",
            (username, admin_email, admin_password_hash),
        )
        conn.commit()
    conn.close()


def log_copilot_query(username: str, prompt: str, response: str):
    conn = get_conn()
    conn.execute(
        "INSERT INTO copilot_logs (username, prompt, response) VALUES (?, ?, ?)",
        (username, prompt, response),
    )
    conn.commit()
    conn.close()


def save_ml_metric(agent_name: str, algorithm: str, metric_name: str, metric_value: float, is_champion: bool = False):
    conn = get_conn()
    conn.execute(
        "INSERT INTO ml_models (agent_name, algorithm, metric_name, metric_value, is_champion) "
        "VALUES (?, ?, ?, ?, ?)",
        (agent_name, algorithm, metric_name, metric_value, int(is_champion)),
    )
    conn.commit()
    conn.close()
