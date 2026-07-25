"""
auth.py — Authentication, JWT sessions, progressive lockout,
OTP resend cooldown, and password strength policy (Sections 5 & 6).
"""

import bcrypt
import jwt
import random
import smtplib
import ssl
from email.mime.text import MIMEText
from datetime import datetime, timedelta

import db

# ---------------------------------------------------------------------
# These are read from Colab Secrets in the notebook and passed in here,
# e.g.:
#   from google.colab import userdata
#   JWT_SECRET_KEY = userdata.get('JWT_SECRET_KEY')
#   EMAIL_ID       = userdata.get('EMAIL_ID')
#   EMAIL_PASSWORD = userdata.get('EMAIL_PASSWORD')
# auth.py never hard-codes secrets — the notebook injects them.
# ---------------------------------------------------------------------
JWT_SECRET_KEY = None
EMAIL_ID = None
EMAIL_PASSWORD = None


def configure(jwt_secret: str, email_id: str = None, email_password: str = None):
    """Call once from the notebook after reading Colab Secrets."""
    global JWT_SECRET_KEY, EMAIL_ID, EMAIL_PASSWORD
    JWT_SECRET_KEY = jwt_secret
    EMAIL_ID = email_id
    EMAIL_PASSWORD = email_password


# ------------------------- password hashing ---------------------------

def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


# ------------------------- password strength (Section 6) ---------------

def check_password_strength(password: str):
    """
    Returns (allowed: bool, badge: str, message: str)
    < 5 chars   -> Weak, BLOCKED
    5-9 chars   -> Average, ALLOWED
    10+ chars   -> Good, ALLOWED
    """
    length = len(password)
    if length < 5:
        return False, "🔴 Weak", "Password too weak (minimum 5 characters required)."
    elif length < 10:
        return True, "🟡 Average", "🟡 Average strength (10+ characters recommended for enterprise security)."
    else:
        return True, "🟢 Good", "🟢 Good password strength — proceed with bcrypt hashing."


# ------------------------- JWT session ----------------------------------

def create_session_token(username: str, role: str, expires_minutes: int = 120) -> str:
    payload = {
        "username": username,
        "role": role,
        "exp": datetime.utcnow() + timedelta(minutes=expires_minutes),
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm="HS256")


def decode_session_token(token: str):
    try:
        return jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


# ------------------------- registration ----------------------------------

SECURITY_QUESTIONS = [
    "What is your favourite pet's name?",
    "What is your mother's maiden name?",
    "What city were you born in?",
    "What was the name of your first school?",
    "What is your favourite book?",
]


def register_user(username: str, email: str, password: str, role: str = "Logistics Manager",
                   security_question: str = None, security_answer: str = None):
    allowed, badge, msg = check_password_strength(password)
    if not allowed:
        return False, msg

    conn = db.get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id FROM users WHERE username = ? OR email = ?", (username, email))
    if cur.fetchone():
        conn.close()
        return False, "Username or email already registered."

    answer_hash = hash_password(security_answer.strip().lower()) if security_answer else None
    cur.execute(
        "INSERT INTO users (username, email, password_hash, role, security_question, security_answer_hash) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (username, email, hash_password(password), role, security_question, answer_hash),
    )
    conn.commit()
    conn.close()
    return True, f"Account created. {msg}"


# ------------------------- security-question recovery ----------------------

def get_security_question(username: str):
    conn = db.get_conn()
    cur = conn.cursor()
    cur.execute("SELECT security_question FROM users WHERE username = ?", (username,))
    row = cur.fetchone()
    conn.close()
    if row is None:
        return None, "No account found with that username."
    if not row["security_question"]:
        return None, "This account has no security question set. Use Email OTP instead."
    return row["security_question"], None


def verify_security_answer(username: str, answer: str):
    conn = db.get_conn()
    cur = conn.cursor()
    cur.execute("SELECT security_answer_hash FROM users WHERE username = ?", (username,))
    row = cur.fetchone()
    conn.close()
    if row is None or not row["security_answer_hash"]:
        return False, "Security question not available for this account."
    if verify_password(answer.strip().lower(), row["security_answer_hash"]):
        return True, "Security answer verified."
    return False, "Incorrect answer. Please try again."


def reset_password_by_username(username: str, new_password: str):
    allowed, badge, msg = check_password_strength(new_password)
    if not allowed:
        return False, msg
    conn = db.get_conn()
    conn.execute(
        "UPDATE users SET password_hash = ?, failed_attempts = 0, lock_until = NULL, "
        "account_status = 'active' WHERE username = ?",
        (hash_password(new_password), username),
    )
    conn.commit()
    conn.close()
    return True, f"Password reset successfully. {msg}"


# ------------------------- progressive lockout (Section 5) ---------------

LOCKOUT_RULES = {
    3: (300, "⏳ Account temporarily locked for 5 minutes due to 3 failed attempts."),
    4: (900, "⏳ Account temporarily locked for 15 minutes due to 4 failed attempts."),
    5: (None, "❌ Account permanently locked due to 5 failed attempts. Only the System "
              "Administrator can unlock this account via the Admin Dashboard."),
}


def _get_user_by_login_id(cur, login_id):
    """login_id can be either a username or an email address."""
    cur.execute("SELECT * FROM users WHERE email = ? OR username = ?", (login_id, login_id))
    return cur.fetchone()


def login_user(login_id: str, password: str):
    """
    login_id: username or email (Section 5 lockout applies either way).
    Returns (success: bool, message: str, token_or_None)
    Implements the full progressive lockout state machine.
    """
    conn = db.get_conn()
    cur = conn.cursor()
    user = _get_user_by_login_id(cur, login_id)

    if user is None:
        conn.close()
        return False, "No account found with that username/email.", None

    now = datetime.utcnow()

    # permanently locked
    if user["account_status"] == "locked":
        conn.close()
        return False, ("❌ Account permanently locked. Only the System Administrator "
                        "can unlock this account via the Admin Dashboard."), None

    # temporarily locked and still within window
    if user["lock_until"]:
        lock_until = datetime.fromisoformat(user["lock_until"])
        if now < lock_until:
            remaining = int((lock_until - now).total_seconds())
            conn.close()
            return False, f"⏳ Account temporarily locked. Try again in {remaining} seconds.", None
        else:
            # lock window expired -> reset on next check
            cur.execute(
                "UPDATE users SET failed_attempts = 0, lock_until = NULL WHERE id = ?",
                (user["id"],),
            )
            conn.commit()

    # verify password
    if verify_password(password, user["password_hash"]):
        cur.execute(
            "UPDATE users SET failed_attempts = 0, lock_until = NULL WHERE id = ?",
            (user["id"],),
        )
        conn.commit()
        token = create_session_token(user["username"], user["role"])
        conn.close()
        return True, f"Welcome, {user['username']}!", token

    # --- failed attempt: apply progressive lockout ---
    attempts = user["failed_attempts"] + 1
    if attempts in LOCKOUT_RULES:
        seconds, msg = LOCKOUT_RULES[attempts]
        if attempts == 5:
            cur.execute(
                "UPDATE users SET failed_attempts = ?, account_status = 'locked', lock_until = NULL WHERE id = ?",
                (attempts, user["id"]),
            )
        else:
            lock_until = (now + timedelta(seconds=seconds)).isoformat()
            cur.execute(
                "UPDATE users SET failed_attempts = ?, lock_until = ? WHERE id = ?",
                (attempts, lock_until, user["id"]),
            )
        conn.commit()
        conn.close()
        return False, msg, None
    else:
        cur.execute("UPDATE users SET failed_attempts = ? WHERE id = ?", (attempts, user["id"]))
        conn.commit()
        conn.close()
        remaining_before_lock = 3 - attempts
        return False, f"Incorrect password. {remaining_before_lock} attempt(s) remaining before lockout.", None


# ------------------------- OTP: generation + email -------------------------

def generate_otp() -> str:
    return f"{random.randint(0, 999999):06d}"


def send_otp_email(to_email: str, otp_code: str):
    """Sends OTP via Gmail SMTP. Falls back to console print if creds missing."""
    if not EMAIL_ID or not EMAIL_PASSWORD:
        print(f"[OTP FALLBACK - no email creds configured] OTP for {to_email}: {otp_code}")
        return True, "OTP generated (console fallback — no EMAIL_ID/EMAIL_PASSWORD secret set)."

    try:
        msg = MIMEText(f"Your FreightQuote AI verification code is: {otp_code}\nThis code expires in 10 minutes.")
        msg["Subject"] = "FreightQuote AI — OTP Verification"
        msg["From"] = EMAIL_ID
        msg["To"] = to_email

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(EMAIL_ID, EMAIL_PASSWORD)
            server.sendmail(EMAIL_ID, to_email, msg.as_string())
        return True, "OTP sent to your email."
    except Exception as e:
        print(f"[OTP EMAIL FAILED] {e}. OTP for {to_email}: {otp_code}")
        return True, "OTP generated (email send failed — check server console)."


# ------------------------- OTP resend cooldown (Section 5.1) ---------------

RESEND_COOLDOWNS = {
    1: (60, "⏳ Please wait 60 seconds before requesting another OTP."),
    2: (180, "⏳ Please wait 3 minutes before requesting another OTP."),
    3: (300, "⏳ Please wait 5 minutes before requesting another OTP."),
}
RESEND_COOLDOWN_MAX = (3600, "⚠️ Too many OTP requests. Please wait 1 hour before trying again.")


def request_otp(email: str, purpose: str = "reset"):
    """
    Handles OTP generation + enforces resend cooldown from otp_requests table.
    Returns (success: bool, message: str)
    """
    conn = db.get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM otp_requests WHERE email = ? AND purpose = ? ORDER BY id DESC LIMIT 1",
        (email, purpose),
    )
    last = cur.fetchone()
    now = datetime.utcnow()

    resend_count = 0
    if last and last["next_allowed"]:
        next_allowed = datetime.fromisoformat(last["next_allowed"])
        if now < next_allowed:
            remaining = int((next_allowed - now).total_seconds())
            conn.close()
            return False, f"⏳ Please wait {remaining} seconds before requesting another OTP."
        resend_count = last["resend_count"]

    resend_count += 1
    cooldown_seconds, msg = RESEND_COOLDOWNS.get(resend_count, RESEND_COOLDOWN_MAX)
    next_allowed_time = (now + timedelta(seconds=cooldown_seconds)).isoformat()

    otp_code = generate_otp()
    cur.execute(
        "INSERT INTO otp_requests (email, otp_code, purpose, resend_count, next_allowed) "
        "VALUES (?, ?, ?, ?, ?)",
        (email, otp_code, purpose, resend_count, next_allowed_time),
    )
    conn.commit()
    conn.close()

    send_otp_email(email, otp_code)
    return True, f"OTP sent. {msg}"


def verify_otp(email: str, otp_code: str, purpose: str = "reset"):
    conn = db.get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM otp_requests WHERE email = ? AND purpose = ? ORDER BY id DESC LIMIT 1",
        (email, purpose),
    )
    row = cur.fetchone()
    if row is None:
        conn.close()
        return False, "No OTP request found. Please request a new OTP."

    if row["otp_code"] != otp_code:
        conn.close()
        return False, "Incorrect OTP. Please try again."

    cur.execute("UPDATE otp_requests SET verified = 1 WHERE id = ?", (row["id"],))
    conn.commit()
    conn.close()
    return True, "OTP verified successfully."


def reset_password(email: str, new_password: str):
    allowed, badge, msg = check_password_strength(new_password)
    if not allowed:
        return False, msg
    conn = db.get_conn()
    conn.execute(
        "UPDATE users SET password_hash = ?, failed_attempts = 0, lock_until = NULL, "
        "account_status = 'active' WHERE email = ?",
        (hash_password(new_password), email),
    )
    conn.commit()
    conn.close()
    return True, f"Password reset successfully. {msg}"
