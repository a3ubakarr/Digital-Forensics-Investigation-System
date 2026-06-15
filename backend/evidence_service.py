import hashlib
from datetime import datetime
from backend.database import run_query, execute_command


def get_all_evidence():
    """Fetch all evidence with case and investigator info."""
    return run_query(
        """SELECT e.evidence_number, c.case_number, e.evidence_type,
                  e.status, e.collected_at, i.full_name AS collected_by,
                  e.source_ip, e.description
           FROM evidence e
           JOIN cases c ON e.case_id = c.case_id
           JOIN investigators i ON e.collected_by = i.investigator_id
           ORDER BY e.collected_at DESC"""
    )


def get_recent_evidence(limit=5):
    """Fetch most recently collected evidence."""
    return run_query(
        """SELECT e.evidence_number, e.evidence_type, e.status, c.case_number
           FROM evidence e JOIN cases c ON e.case_id=c.case_id
           ORDER BY e.collected_at DESC LIMIT ?""",
        (limit,)
    )


def get_evidence_by_type():
    """Return evidence count grouped by type for charts."""
    return run_query(
        "SELECT evidence_type, COUNT(*) AS total FROM evidence GROUP BY evidence_type ORDER BY total DESC"
    )


def get_open_cases():
    """Return open cases for evidence submission dropdown."""
    return run_query(
        "SELECT case_id, case_number, title FROM cases WHERE status != 'closed'"
    )


def get_all_evidence_for_delete():
    """Return evidence list for delete dropdown."""
    return run_query(
        "SELECT e.evidence_number, c.case_number FROM evidence e "
        "JOIN cases c ON e.case_id=c.case_id ORDER BY e.evidence_number"
    )


def gen_evidence_number(case_number):
    """Generate next sequential evidence number for a case."""
    rows = run_query(
        "SELECT COUNT(*) FROM evidence e JOIN cases c ON e.case_id=c.case_id WHERE c.case_number=?",
        (case_number,)
    )
    n = (rows[0][0] if rows else 0) + 1
    return f"EV-{case_number}-{str(n).zfill(3)}"


def gen_sha256(ev_num, case_num):
    """Generate SHA-256 hash for evidence integrity."""
    return hashlib.sha256(
        f"{ev_num}-{case_num}-{datetime.now().isoformat()}".encode()
    ).hexdigest()


def submit_evidence(case_id, ev_num, ev_type, description, collected_at,
                    inv_id, storage_loc, source_ip, ev_hash, collect_loc):
    """Insert evidence, custody record, and integrity hash."""
    new_ev_id = execute_command(
        "INSERT INTO evidence (case_id,evidence_number,evidence_type,description,"
        "collected_at,collected_by,storage_location,source_ip,status) VALUES (?,?,?,?,?,?,?,?,'collected')",
        (case_id, ev_num, ev_type, description, collected_at, inv_id, storage_loc, source_ip)
    )
    execute_command(
        "INSERT INTO chain_of_custody (evidence_id,handled_by,action_time,action_type,location,reason) "
        "VALUES (?,?,?,'collected',?,'Initial collection at scene')",
        (new_ev_id, inv_id, collected_at, collect_loc)
    )
    execute_command(
        "INSERT INTO evidence_integrity (evidence_id,sha256_hash,verified_by,is_tampered,notes) "
        "VALUES (?,?,?,0,'Auto-generated hash on collection')",
        (new_ev_id, ev_hash, inv_id)
    )
    return new_ev_id


def delete_evidence(ev_num):
    """Delete evidence and all related records."""
    rows = run_query("SELECT evidence_id FROM evidence WHERE evidence_number=?", (ev_num,))
    if rows:
        ev_id = rows[0]["evidence_id"]
        execute_command("DELETE FROM evidence_integrity WHERE evidence_id=?", (ev_id,))
        execute_command("DELETE FROM chain_of_custody WHERE evidence_id=?",   (ev_id,))
        execute_command("DELETE FROM evidence WHERE evidence_id=?",           (ev_id,))


def get_investigators():
    """Return all investigators for dropdown."""
    return run_query("SELECT investigator_id, full_name FROM investigators")