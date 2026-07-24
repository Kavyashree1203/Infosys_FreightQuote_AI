"""
db.py
SQLite layer for FreightQuote AI — Milestone 2.
Extends the Milestone 1 `users` table with progressive-lockout columns
and adds the `ml_models` table used by the Admin -> ML Model Card tab.
"""

import sqlite3
import os
import bcrypt
from datetime import datetime, timedelta

DB_PATH = os.path.join(os.path.dirname(__file__), "freightquote.db")


def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id                INTEGER PRIMARY KEY AUTOINCREMENT,
            username          TEXT UNIQUE NOT NULL,
            email             TEXT UNIQUE NOT NULL,
            password_hash     TEXT NOT NULL,
            security_question TEXT,
            security_answer_hash TEXT,
            role              TEXT DEFAULT 'User',
            failed_attempts   INTEGER DEFAULT 0,
            lock_until        TIMESTAMP DEFAULT NULL,
            account_status    TEXT DEFAULT 'active',
            otp_resend_count  INTEGER DEFAULT 0,
            otp_next_allowed  TIMESTAMP DEFAULT NULL,
            created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS ml_models (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            agent_name   TEXT NOT NULL,
            algorithm    TEXT NOT NULL,
            metric_name  TEXT NOT NULL,
            metric_value REAL NOT NULL,
            is_champion  INTEGER DEFAULT 0,
            trained_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    conn.commit()

    # Bootstrap default admin if no admin exists yet
    cur.execute("SELECT COUNT(*) AS c FROM users WHERE role = 'Admin'")
    if cur.fetchone()["c"] == 0:
        admin_email = os.environ.get("ADMIN_EMAIL_ID", "infosys@ai")
        admin_password = os.environ.get("ADMIN_PASSWORD", "admin@123")
        pw_hash = bcrypt.hashpw(admin_password.encode(), bcrypt.gensalt()).decode()
        cur.execute(
            """INSERT INTO users (username, email, password_hash, role, account_status)
               VALUES (?, ?, ?, 'Admin', 'active')""",
            ("Administrator", admin_email, pw_hash),
        )
        conn.commit()

    conn.close()


# ---------------- User lookups ----------------

def get_user_by_identifier(identifier: str):
    conn = get_conn()
    row = conn.execute(
        "SELECT * FROM users WHERE username = ? OR email = ?", (identifier, identifier)
    ).fetchone()
    conn.close()
    return row


def get_all_users():
    conn = get_conn()
    rows = conn.execute("SELECT * FROM users ORDER BY id").fetchall()
    conn.close()
    return rows


# ---------------- Create / Delete / Unlock (used by auth.py & admin_dash.py) ----------------

def create_user(username, email, password, security_question, security_answer, role="User"):
    conn = get_conn()
    pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    ans_hash = bcrypt.hashpw(security_answer.strip().lower().encode(), bcrypt.gensalt()).decode()
    conn.execute(
        """INSERT INTO users (username, email, password_hash, security_question, security_answer_hash, role)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (username, email, pw_hash, security_question, ans_hash, role),
    )
    conn.commit()
    conn.close()


def delete_user(user_id: int):
    conn = get_conn()
    conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()


def unlock_user(user_id: int):
    conn = get_conn()
    conn.execute(
        """UPDATE users SET failed_attempts = 0, lock_until = NULL, account_status = 'active'
           WHERE id = ?""",
        (user_id,),
    )
    conn.commit()
    conn.close()


def reset_password(user_id: int, new_password: str):
    conn = get_conn()
    pw_hash = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
    conn.execute("UPDATE users SET password_hash = ? WHERE id = ?", (pw_hash, user_id))
    conn.commit()
    conn.close()


# ---------------- ML metrics logging (used by train_ml_freight.py) ----------------

def log_model_metric(agent_name, algorithm, metric_name, metric_value, is_champion=False):
    conn = get_conn()
    conn.execute(
        """INSERT INTO ml_models (agent_name, algorithm, metric_name, metric_value, is_champion)
           VALUES (?, ?, ?, ?, ?)""",
        (agent_name, algorithm, metric_name, metric_value, int(is_champion)),
    )
    conn.commit()
    conn.close()


def get_model_metrics(agent_name=None):
    conn = get_conn()
    if agent_name:
        rows = conn.execute(
            "SELECT * FROM ml_models WHERE agent_name = ? ORDER BY trained_at DESC", (agent_name,)
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM ml_models ORDER BY agent_name, trained_at DESC").fetchall()
    conn.close()
    return rows
