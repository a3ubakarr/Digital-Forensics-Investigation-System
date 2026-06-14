import hashlib
from datetime import datetime
from backend.database import run_query, execute_command


def get_all_users():
    """Fetch all users with investigator profile info."""
    return run_query(
        """SELECT u.user_id, u.username, u.role, u.is_active,
                  u.created_at, u.last_login,
                  COALESCE(i.full_name,'N/A')    AS full_name,
                  COALESCE(i.badge_number,'N/A') AS badge_number,
                  COALESCE(i.department,'N/A')   AS department
           FROM users u
           LEFT JOIN investigators i ON u.user_id = i.user_id
           ORDER BY u.created_at DESC"""
    )


def gen_badge_number():
    """Generate next sequential badge number for current year."""
    year = datetime.now().year
    rows = run_query(f"SELECT COUNT(*) FROM investigators WHERE badge_number LIKE 'FIA-{year}-%'")
    n = (rows[0][0] if rows else 0) + 1
    return f"FIA-{year}-{str(n).zfill(3)}"


def create_user(username, password, role, full_name, badge, email):
    """Create new user and investigator profile."""
    pw_hash = hashlib.sha256(password.encode()).hexdigest().upper()
    uid = execute_command(
        "INSERT INTO users (username,password_hash,role) VALUES (?,?,?)",
        (username, pw_hash, role)
    )
    execute_command(
        "INSERT INTO investigators (user_id,full_name,badge_number,contact_email) VALUES (?,?,?,?)",
        (uid, full_name, badge, email)
    )


def delete_user(user_id):
    """
    Delete user safely.
    If they have an investigator profile, reassign all their records
    to another investigator first.
    Returns (True, None) on success or (False, error_message) on failure.
    """
    inv_rows = run_query(
        "SELECT investigator_id FROM investigators WHERE user_id=?", (user_id,))

    if not inv_rows:
        # No investigator profile — safe to delete directly
        execute_command("DELETE FROM access_logs WHERE user_id=?", (user_id,))
        execute_command("DELETE FROM users WHERE user_id=?", (user_id,))
        return True, None

    inv_id = inv_rows[0]["investigator_id"]

    # Check if any other investigator exists to take over records
    other = run_query(
        "SELECT investigator_id, full_name FROM investigators "
        "WHERE investigator_id != ? LIMIT 1",
        (inv_id,))

    if not other:
        # No other investigator — block deletion
        return False, "Cannot delete the last investigator. At least one must remain."

    fallback_id = other[0]["investigator_id"]

    # Reassign all linked records to fallback investigator
    execute_command(
        "UPDATE cases SET lead_investigator_id=? WHERE lead_investigator_id=?",
        (fallback_id, inv_id))
    execute_command(
        "UPDATE chain_of_custody SET handled_by=? WHERE handled_by=?",
        (fallback_id, inv_id))
    execute_command(
        "UPDATE evidence_integrity SET verified_by=? WHERE verified_by=?",
        (fallback_id, inv_id))
    execute_command(
        "UPDATE evidence SET collected_by=? WHERE collected_by=?",
        (fallback_id, inv_id))
    execute_command(
        "UPDATE case_reports SET authored_by=? WHERE authored_by=?",
        (fallback_id, inv_id))

    # Now safe to delete
    execute_command("DELETE FROM investigators WHERE user_id=?", (user_id,))
    execute_command("DELETE FROM access_logs WHERE user_id=?", (user_id,))
    execute_command("DELETE FROM users WHERE user_id=?", (user_id,))
    return True, None


def get_access_logs():
    """Fetch all access logs ordered by most recent."""
    return run_query(
        """SELECT u.username, u.role, al.action,
                  al.resource_accessed, al.action_time,
                  al.ip_address, al.success, al.failure_reason
           FROM access_logs al
           JOIN users u ON al.user_id = u.user_id
           ORDER BY al.action_time DESC"""
    )


def get_all_investigators():
    """Return all investigators for dropdowns."""
    return run_query("SELECT investigator_id, full_name FROM investigators")


def get_stat_counts():
    """Return dashboard stat counts."""
    from backend.database import run_query as rq
    return {
        "total_cases":    rq("SELECT COUNT(*) FROM cases")[0][0],
        "active_cases":   rq("SELECT COUNT(*) FROM cases WHERE status != 'closed'")[0][0],
        "critical_cases": rq("SELECT COUNT(*) FROM cases WHERE priority = 'critical'")[0][0],
        "total_evidence": rq("SELECT COUNT(*) FROM evidence")[0][0],
        "tampered":       rq("SELECT COUNT(*) FROM evidence_integrity WHERE is_tampered = 1")[0][0],
    }