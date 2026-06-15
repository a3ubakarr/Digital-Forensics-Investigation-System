from backend.database import run_query


def get_all_evidence_numbers():
    """Return list of all evidence numbers for dropdown."""
    rows = run_query("SELECT evidence_number FROM evidence ORDER BY evidence_number")
    return [r["evidence_number"] for r in rows]


def get_custody_trail(evidence_number):
    """Return full chain of custody for a given evidence item."""
    return run_query(
        """SELECT cc.action_type, cc.action_time, i.full_name AS handled_by,
                  cc.location, cc.reason, cc.witness_name
           FROM chain_of_custody cc
           JOIN evidence e ON cc.evidence_id = e.evidence_id
           JOIN investigators i ON cc.handled_by = i.investigator_id
           WHERE e.evidence_number = ?
           ORDER BY cc.action_time""",
        (evidence_number,)
    )


def get_integrity_records():
    """Return all integrity records sorted by tampered first."""
    return run_query(
        """SELECT e.evidence_number, e.evidence_type, c.case_number,
                  ei.sha256_hash, ei.verified_at, ei.is_tampered,
                  ei.notes, i.full_name AS verified_by
           FROM evidence_integrity ei
           JOIN evidence e ON ei.evidence_id = e.evidence_id
           JOIN cases c    ON e.case_id = c.case_id
           JOIN investigators i ON ei.verified_by = i.investigator_id
           ORDER BY ei.is_tampered DESC, ei.verified_at DESC"""
    )