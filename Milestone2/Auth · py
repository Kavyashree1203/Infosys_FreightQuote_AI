"""
auth.py
Login / Signup / Forgot-Password logic for FreightQuote AI — Milestone 2.
Implements:
  - Section 5: Progressive account lockout (3rd/4th/5th failed attempt)
  - Section 5.1: OTP resend cooldown (60s / 180s / 300s / 1hr)
  - Section 6: Password strength policy (Weak/Average/Good)
  - JWT session issuing (signed with JWT_SECRET_KEY from Colab Secrets / env)
"""

import os
import random
import smtplib
import ssl
from email.mime.text import MIMEText
from datetime import datetime, timedelta

import bcrypt
import jwt
import streamlit as st

import db

JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "dev-only-change-me")
JWT_ALGO = "HS256"
JWT_EXP_MINUTES = 60

EMAIL_ID = os.environ.get("EMAIL_ID")          # sender gmail address (optional)
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")  # gmail app password (optional)

LOCKOUT_RULES = {
    3: (300, "⏳ Account temporarily locked for 5 minutes due to 3 failed attempts."),
    4: (900, "⏳ Account temporarily locked for 15 minutes due to 4 failed attempts."),
}
PERMANENT_LOCK_AT = 5

OTP_COOLDOWNS = {
    1: (60, "⏳ Please wait 60 seconds before requesting another OTP."),
    2: (180, "⏳ Please wait 3 minutes before requesting another OTP."),
    3: (300, "⏳ Please wait 5 minutes before requesting another OTP."),
}
OTP_COOLDOWN_MAX = (3600, "⚠️ Too many OTP requests. Please wait 1 hour before trying again.")


# ---------------------------------------------------------------------------
# JWT session helpers
# ---------------------------------------------------------------------------

def issue_token(user_row) -> str:
    payload = {
        "sub": user_row["id"],
        "username": user_row["username"],
        "role": user_row["role"],
        "exp": datetime.utcnow() + timedelta(minutes=JWT_EXP_MINUTES),
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGO)


def verify_token(token: str):
    try:
        return jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGO])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


# ---------------------------------------------------------------------------
# Section 5 — Progressive account lockout
# ---------------------------------------------------------------------------

def is_locked(user_row) -> tuple[bool, str]:
    """Returns (locked?, message) based on account_status / lock_until."""
    if user_row["account_status"] == "locked":
        return True, ("❌ Account permanently locked due to 5 failed attempts. "
                       "Only the System Administrator can unlock this account via the Admin Dashboard.")

    lock_until = user_row["lock_until"]
    if lock_until:
        lock_until_dt = datetime.fromisoformat(lock_until)
        if datetime.utcnow() < lock_until_dt:
            remaining = int((lock_until_dt - datetime.utcnow()).total_seconds())
            return True, f"⏳ Account temporarily locked. Try again in {remaining} seconds."
        else:
            # lock window has passed -> auto reset (spec: on successful login now()>=lock_until)
            _reset_lockout(user_row["id"])
    return False, ""


def _reset_lockout(user_id: int):
    conn = db.get_conn()
    conn.execute(
        "UPDATE users SET failed_attempts = 0, lock_until = NULL WHERE id = ?", (user_id,)
    )
    conn.commit()
    conn.close()


def register_failed_attempt(user_row) -> str:
    """Increments failed_attempts and applies the lockout ladder. Returns user-facing message."""
    conn = db.get_conn()
    attempts = user_row["failed_attempts"] + 1

    if attempts >= PERMANENT_LOCK_AT:
        conn.execute(
            """UPDATE users SET failed_attempts = ?, account_status = 'locked', lock_until = NULL
               WHERE id = ?""",
            (attempts, user_row["id"]),
        )
        msg = ("❌ Account permanently locked due to 5 failed attempts. "
               "Only the System Administrator can unlock this account via the Admin Dashboard.")
    elif attempts in LOCKOUT_RULES:
        seconds, msg = LOCKOUT_RULES[attempts]
        lock_until = (datetime.utcnow() + timedelta(seconds=seconds)).isoformat()
        conn.execute(
            "UPDATE users SET failed_attempts = ?, lock_until = ? WHERE id = ?",
            (attempts, lock_until, user_row["id"]),
        )
    else:
        conn.execute(
            "UPDATE users SET failed_attempts = ? WHERE id = ?", (attempts, user_row["id"])
        )
        msg = f"❌ Incorrect credentials. {attempts} failed attempt(s) recorded."

    conn.commit()
    conn.close()
    return msg


def register_successful_login(user_id: int):
    _reset_lockout(user_id)


# ---------------------------------------------------------------------------
# Section 6 — Password strength policy
# ---------------------------------------------------------------------------

def check_password_strength(password: str) -> tuple[bool, str]:
    """Returns (allowed_to_submit, message) per Section 6."""
    n = len(password)
    if n < 5:
        return False, "Password too weak (minimum 5 characters required)."
    elif n < 10:
        return True, "🟡 Average strength (10+ characters recommended for enterprise security)."
    else:
        return True, "🟢 Good password strength — proceed with bcrypt hashing."


# ---------------------------------------------------------------------------
# Section 5.1 — OTP generation, sending & resend cooldown
# ---------------------------------------------------------------------------

def generate_otp() -> str:
    return f"{random.randint(0, 999999):06d}"


def send_otp_email(to_email: str, otp: str) -> bool:
    """Sends OTP via Gmail SMTP if EMAIL_ID/EMAIL_PASSWORD secrets are set,
    otherwise falls back to printing to console (expected, not a bug)."""
    if not EMAIL_ID or not EMAIL_PASSWORD:
        print(f"[CONSOLE FALLBACK] OTP for {to_email}: {otp}")
        return False

    msg = MIMEText(f"Your FreightQuote AI verification code is: {otp}\nThis code expires in 10 minutes.")
    msg["Subject"] = "FreightQuote AI — Your OTP Code"
    msg["From"] = EMAIL_ID
    msg["To"] = to_email

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(EMAIL_ID, EMAIL_PASSWORD)
            server.sendmail(EMAIL_ID, to_email, msg.as_string())
        return True
    except Exception as e:
        print(f"[EMAIL ERROR] {e} — falling back to console OTP: {otp}")
        return False


def can_resend_otp(user_row) -> tuple[bool, str]:
    """Checks otp_next_allowed. Returns (allowed?, message-if-blocked)."""
    next_allowed = user_row["otp_next_allowed"]
    if next_allowed:
        next_allowed_dt = datetime.fromisoformat(next_allowed)
        if datetime.utcnow() < next_allowed_dt:
            remaining = int((next_allowed_dt - datetime.utcnow()).total_seconds())
            return False, f"⏳ Please wait {remaining} seconds before requesting another OTP."
    return True, ""


def register_otp_resend(user_id: int):
    """Bumps otp_resend_count and sets the next-allowed cooldown per the ladder."""
    conn = db.get_conn()
    row = conn.execute("SELECT otp_resend_count FROM users WHERE id = ?", (user_id,)).fetchone()
    count = (row["otp_resend_count"] or 0) + 1

    if count in OTP_COOLDOWNS:
        seconds, _ = OTP_COOLDOWNS[count]
    else:
        seconds, _ = OTP_COOLDOWN_MAX

    next_allowed = (datetime.utcnow() + timedelta(seconds=seconds)).isoformat()
    conn.execute(
        "UPDATE users SET otp_resend_count = ?, otp_next_allowed = ? WHERE id = ?",
        (count, next_allowed, user_id),
    )
    conn.commit()
    conn.close()


def reset_otp_counter(user_id: int):
    conn = db.get_conn()
    conn.execute(
        "UPDATE users SET otp_resend_count = 0, otp_next_allowed = NULL WHERE id = ?", (user_id,)
    )
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# High-level flows called directly from the Streamlit tabs
# ---------------------------------------------------------------------------

def attempt_login(identifier: str, password: str):
    """Returns (success: bool, message: str, token_or_None)."""
    user = db.get_user_by_identifier(identifier)
    if not user:
        return False, "❌ No account found with that username/email.", None

    locked, lock_msg = is_locked(user)
    if locked:
        return False, lock_msg, None

    # re-fetch in case is_locked() auto-reset the row
    user = db.get_user_by_identifier(identifier)

    if bcrypt.checkpw(password.encode(), user["password_hash"].encode()):
        register_successful_login(user["id"])
        token = issue_token(user)
        return True, "✅ Login successful.", token
    else:
        msg = register_failed_attempt(user)
        return False, msg, None


def signup_user(username, email, password, confirm_password, security_question, security_answer):
    if password != confirm_password:
        return False, "❌ Passwords do not match."

    allowed, msg = check_password_strength(password)
    if not allowed:
        return False, msg

    existing = db.get_user_by_identifier(username) or db.get_user_by_identifier(email)
    if existing:
        return False, "❌ Username or email already registered."

    db.create_user(username, email, password, security_question, security_answer, role="User")
    return True, "✅ Account created successfully. You can now log in."
