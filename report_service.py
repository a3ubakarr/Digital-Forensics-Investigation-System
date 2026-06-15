from datetime import datetime
from backend.database import run_query, execute_command


def get_all_reports():
    """Fetch all investigation reports with author and case info."""
    return run_query(
        """SELECT cr.report_title, c.case_number, i.full_name AS authored_by,
                  cr.verdict, cr.created_at, cr.is_final,
                  cr.findings, cr.recommendations
           FROM case_reports cr
           JOIN cases c ON cr.case_id = c.case_id
           JOIN investigators i ON cr.authored_by = i.investigator_id
           ORDER BY cr.created_at DESC"""
    )


def submit_report(case_id, author_id, title, findings, recommendations, verdict, is_final):
    """Insert a new investigation report."""
    execute_command(
        "INSERT INTO case_reports (case_id,authored_by,report_title,findings,"
        "recommendations,verdict,submitted_at,is_final) VALUES (?,?,?,?,?,?,?,?)",
        (case_id, author_id, title, findings, recommendations,
         verdict, str(datetime.now()), 1 if is_final else 0)
    )


def get_all_cases_for_report():
    """Return all cases for report dropdown."""
    return run_query("SELECT case_id, case_number, title FROM cases")