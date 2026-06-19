from datetime import datetime
from backend.database import run_query, execute_command


def get_all_cases(status_filter=None, priority_filter=None):
    """Fetch all cases with optional filters."""
    sql = """SELECT c.case_id, c.case_number, c.title, c.case_type,
                    c.status, c.priority, c.opened_date,
                    c.affected_org, c.jurisdiction,
                    i.full_name AS lead_investigator,
                    COUNT(e.evidence_id) AS evidence_count
             FROM cases c
             JOIN investigators i ON c.lead_investigator_id = i.investigator_id
             LEFT JOIN evidence e ON c.case_id = e.case_id"""
    conds = []
    params = []
    if status_filter and status_filter != "All":
        conds.append("c.status=?")
        params.append(status_filter)
    if priority_filter and priority_filter != "All":
        conds.append("c.priority=?")
        params.append(priority_filter)
    if conds:
        sql += " WHERE " + " AND ".join(conds)
    sql += " GROUP BY c.case_id ORDER BY c.opened_date DESC"
    return run_query(sql, tuple(params))


def get_recent_cases(limit=5):
    """Fetch most recently opened cases."""
    return run_query(
        "SELECT case_number, title, status, priority FROM cases ORDER BY opened_date DESC LIMIT ?",
        (limit,)
    )


def gen_case_number():
    """Generate next sequential case number for current year."""
    year = datetime.now().year
    rows = run_query(f"SELECT COUNT(*) FROM cases WHERE case_number LIKE 'CYB-{year}-%'")
    n = (rows[0][0] if rows else 0) + 1
    return f"CYB-{year}-{str(n).zfill(4)}"


def create_case(case_number, title, case_type, priority, investigator_id, org, jurisdiction):
    """Insert a new case record."""
    execute_command(
        "INSERT INTO cases (case_number,title,case_type,priority,lead_investigator_id,opened_date,status,affected_org,jurisdiction) VALUES (?,?,?,?,?,?,?,?,?)",
        (case_number, title, case_type, priority, investigator_id,
         str(datetime.now().date()), "open", org, jurisdiction)
    )


def update_case_status(case_id, new_status):
    """
    Update case status. If closing, validate that the case has
    at least one piece of evidence and one final report submitted.
    Returns (True, None) on success or (False, error_message) on failure.
    """
    if new_status == "closed":
        evidence_check = run_query(
            "SELECT COUNT(*) FROM evidence WHERE case_id=?", (case_id,)
        )
        if not evidence_check or evidence_check[0][0] == 0:
            return False, "Cannot close case: no evidence has been submitted."

        report_check = run_query(
            "SELECT COUNT(*) FROM case_reports WHERE case_id=? AND is_final=1",
            (case_id,)
        )
        if not report_check or report_check[0][0] == 0:
            return False, "Cannot close case: no final investigation report found."

        execute_command(
            "UPDATE cases SET closed_date=? WHERE case_id=?",
            (str(datetime.now().date()), case_id)
        )

    execute_command("UPDATE cases SET status=? WHERE case_id=?", (new_status, case_id))
    return True, None


def get_cases_by_type():
    """Return case count grouped by type for charts."""
    return run_query(
        "SELECT case_type, COUNT(*) AS total FROM cases GROUP BY case_type ORDER BY total DESC"
    )


def get_cases_by_status():
    """Return case count grouped by status for charts."""
    return run_query("SELECT status, COUNT(*) AS total FROM cases GROUP BY status")


def get_investigators():
    """Return all investigators for dropdown menus."""
    return run_query("SELECT investigator_id, full_name FROM investigators")