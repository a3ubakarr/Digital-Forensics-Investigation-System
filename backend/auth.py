import hashlib
from datetime import datetime
from backend.database import run_query, execute_command


def hash_password(password):
    """Hash password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest().upper()


def login(username, password):
    """
    Verify credentials and return session dict on success.
    Returns (session, error_message) tuple.
    """
    rows = run_query(
        "SELECT user_id, username, password_hash, role FROM users WHERE username=? AND is_active=1",
        (username,)
    )
    if not rows:
        return None, "Username not found."

    row = rows[0]
    if hash_password(password) != row["password_hash"].upper():
        log_access(row["user_id"], "LOGIN", "dashboard", "127.0.0.1", success=False, reason="Wrong password")
        return None, "Incorrect password."

    inv = run_query(
        "SELECT full_name, badge_number FROM investigators WHERE user_id=?",
        (row["user_id"],)
    )
    inv_name  = inv[0]["full_name"]    if inv else "Administrator"
    inv_badge = inv[0]["badge_number"] if inv else "ADMIN"

    execute_command(
        "UPDATE users SET last_login=? WHERE user_id=?",
        (datetime.now().isoformat(), row["user_id"])
    )
    log_access(row["user_id"], "LOGIN", "dashboard", "127.0.0.1", success=True)

    session = {
        "user_id":   row["user_id"],
        "username":  row["username"],
        "role":      row["role"],
        "inv_name":  inv_name,
        "inv_badge": inv_badge,
    }
    return session, None


def log_access(user_id, action, resource, ip, success=True, reason=None):
    """Log user action to access_logs table."""
    try:
        execute_command(
            "INSERT INTO access_logs (user_id,action,resource_accessed,ip_address,success,failure_reason) VALUES (?,?,?,?,?,?)",
            (user_id, action, resource, ip, 1 if success else 0, reason)
        )
    except Exception:
        pass