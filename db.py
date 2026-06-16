# This is the db.py (Do not remove line)
# Shared database connection, auth helpers, session tracking, and audit log.

import hashlib
import secrets
import datetime

try:
    import mysql.connector
    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False

# ── Security constants ─────────────────────────────────────────────────────
PBKDF2_ITERS  = 200_000
SALT_BYTES    = 32
MAX_ATTEMPTS  = 5
LOCKOUT_SECS  = 300


def gen_salt() -> str:
    """64-character hex salt — 32 cryptographically random bytes."""
    return secrets.token_hex(SALT_BYTES)


def hash_password_pbkdf2(password: str, salt: str) -> str:
    """PBKDF2-HMAC-SHA256 with 200,000 iterations."""
    return hashlib.pbkdf2_hmac(
        "sha256", password.encode(), salt.encode(), PBKDF2_ITERS
    ).hex()


def verify_password(password: str, stored_hash: str, salt: str) -> bool:
    """Constant-time comparison — timing-attack safe."""
    computed = hash_password_pbkdf2(password, salt)
    return secrets.compare_digest(computed, stored_hash)


# Legacy plain SHA-256 — kept only for transparent migration on first login
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def get_db_connection():
    if not DB_AVAILABLE:
        raise RuntimeError(
            "mysql-connector-python is not installed. "
            "Run: pip install mysql-connector-python"
        )
    return mysql.connector.connect(
        host="localhost",
        port="3306",
        user="root",
        password="6789",
        database="pos_system",
        connection_timeout=5,
    )


# ── Logging / session / audit helpers ────────────────────────────────────

def log_login(db, username: str, success: bool,
              reason: str = None, session_id: str = None):
    cur = db.cursor()
    cur.execute(
        "INSERT INTO login_log (username, success, reason, session_id) "
        "VALUES (%s, %s, %s, %s)",
        (username, 1 if success else 0, reason, session_id),
    )


def start_session(db, user_id: int, username: str, session_id: str):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cur = db.cursor()
    cur.execute(
        "INSERT INTO session_log (user_id, username, session_id, login_at) "
        "VALUES (%s, %s, %s, %s)",
        (user_id, username, session_id, now),
    )


def end_session(db, session_id: str, logout_type: str = "manual"):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cur = db.cursor(dictionary=True)
    cur.execute(
        "SELECT login_at FROM session_log "
        "WHERE session_id = %s AND logout_at IS NULL",
        (session_id,),
    )
    row = cur.fetchone()
    if not row:
        return
    try:
        login_dt  = datetime.datetime.strptime(str(row["login_at"]), "%Y-%m-%d %H:%M:%S")
        logout_dt = datetime.datetime.strptime(now, "%Y-%m-%d %H:%M:%S")
        dur       = int((logout_dt - login_dt).total_seconds())
    except Exception:
        dur = None
    cur2 = db.cursor()
    cur2.execute(
        "UPDATE session_log "
        "SET logout_at=%s, duration_s=%s, logout_type=%s "
        "WHERE session_id=%s",
        (now, dur, logout_type, session_id),
    )


def audit(db, user_id, username: str, action: str, detail: str = None):
    cur = db.cursor()
    cur.execute(
        "INSERT INTO audit_log (user_id, username, action, detail) "
        "VALUES (%s, %s, %s, %s)",
        (user_id, username, action, detail),
    )