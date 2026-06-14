import sqlite3
import hashlib
from datetime import datetime

DB_PATH = "dfis.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def run_query(sql, params=()):
    """Run SELECT query, returns list of Row objects."""
    conn = get_connection()
    try:
        return conn.execute(sql, params).fetchall()
    finally:
        conn.close()


def execute_command(sql, params=()):
    """Run INSERT/UPDATE/DELETE, returns lastrowid."""
    conn = get_connection()
    try:
        cursor = conn.execute(sql, params)
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS users (
    user_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    username      TEXT    NOT NULL UNIQUE,
    password_hash TEXT    NOT NULL,
    role          TEXT    NOT NULL CHECK(role IN ('admin','investigator','analyst')),
    is_active     INTEGER DEFAULT 1,
    created_at    TEXT    DEFAULT (datetime('now')),
    last_login    TEXT
);

CREATE TABLE IF NOT EXISTS investigators (
    investigator_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id         INTEGER NOT NULL UNIQUE,
    full_name       TEXT    NOT NULL,
    badge_number    TEXT    NOT NULL UNIQUE,
    specialization  TEXT,
    contact_email   TEXT    NOT NULL,
    department      TEXT,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS cases (
    case_id              INTEGER PRIMARY KEY AUTOINCREMENT,
    case_number          TEXT    NOT NULL UNIQUE,
    title                TEXT    NOT NULL,
    case_type            TEXT    NOT NULL CHECK(case_type IN (
                             'ransomware','phishing','data_breach',
                             'insider_threat','fraud','ddos',
                             'identity_theft','malware','other')),
    status               TEXT    DEFAULT 'open' CHECK(status IN (
                             'open','under_investigation',
                             'pending_review','closed','archived')),
    priority             TEXT    DEFAULT 'medium' CHECK(priority IN (
                             'critical','high','medium','low')),
    lead_investigator_id INTEGER NOT NULL,
    opened_date          TEXT    NOT NULL,
    closed_date          TEXT,
    description          TEXT,
    affected_org         TEXT,
    jurisdiction         TEXT,
    FOREIGN KEY (lead_investigator_id) REFERENCES investigators(investigator_id)
);

CREATE TABLE IF NOT EXISTS evidence (
    evidence_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    case_id          INTEGER NOT NULL,
    evidence_number  TEXT    NOT NULL UNIQUE,
    evidence_type    TEXT    NOT NULL CHECK(evidence_type IN (
                         'usb_drive','hard_disk','email','log_file',
                         'ip_trace','screenshot','network_capture',
                         'mobile_device','document','memory_dump','other')),
    description      TEXT    NOT NULL,
    storage_location TEXT,
    collected_at     TEXT    NOT NULL,
    collected_by     INTEGER NOT NULL,
    status           TEXT    DEFAULT 'collected' CHECK(status IN (
                         'collected','in_analysis','verified',
                         'compromised','released')),
    file_size_bytes  INTEGER,
    source_ip        TEXT,
    notes            TEXT,
    FOREIGN KEY (case_id)      REFERENCES cases(case_id) ON DELETE CASCADE,
    FOREIGN KEY (collected_by) REFERENCES investigators(investigator_id)
);

CREATE TABLE IF NOT EXISTS evidence_integrity (
    integrity_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    evidence_id    INTEGER NOT NULL,
    sha256_hash    TEXT    NOT NULL,
    verified_at    TEXT    DEFAULT (datetime('now')),
    verified_by    INTEGER NOT NULL,
    is_tampered    INTEGER DEFAULT 0,
    notes          TEXT,
    FOREIGN KEY (evidence_id) REFERENCES evidence(evidence_id) ON DELETE CASCADE,
    FOREIGN KEY (verified_by) REFERENCES investigators(investigator_id)
);

CREATE TABLE IF NOT EXISTS chain_of_custody (
    custody_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    evidence_id  INTEGER NOT NULL,
    handled_by   INTEGER NOT NULL,
    action_time  TEXT    DEFAULT (datetime('now')),
    action_type  TEXT    NOT NULL CHECK(action_type IN (
                     'collected','transferred','analyzed',
                     'stored','returned','destroyed','released_to_court')),
    location     TEXT,
    reason       TEXT,
    witness_name TEXT,
    FOREIGN KEY (evidence_id) REFERENCES evidence(evidence_id) ON DELETE CASCADE,
    FOREIGN KEY (handled_by)  REFERENCES investigators(investigator_id)
);

CREATE TABLE IF NOT EXISTS case_reports (
    report_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    case_id         INTEGER NOT NULL,
    authored_by     INTEGER NOT NULL,
    report_title    TEXT    NOT NULL,
    findings        TEXT    NOT NULL,
    recommendations TEXT,
    verdict         TEXT    DEFAULT 'pending' CHECK(verdict IN (
                        'guilty','not_guilty','inconclusive','referred','pending')),
    created_at      TEXT    DEFAULT (datetime('now')),
    submitted_at    TEXT,
    is_final        INTEGER DEFAULT 0,
    FOREIGN KEY (case_id)     REFERENCES cases(case_id) ON DELETE CASCADE,
    FOREIGN KEY (authored_by) REFERENCES investigators(investigator_id)
);

CREATE TABLE IF NOT EXISTS access_logs (
    log_id            INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id           INTEGER NOT NULL,
    action            TEXT    NOT NULL,
    resource_accessed TEXT,
    action_time       TEXT    DEFAULT (datetime('now')),
    ip_address        TEXT,
    success           INTEGER DEFAULT 1,
    failure_reason    TEXT,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
"""


def _hash(password):
    return hashlib.sha256(password.encode()).hexdigest().upper()


def seed_sample_data(conn):
    """Insert sample data on first run."""
    cur = conn.cursor()

    cur.executemany(
        "INSERT INTO users (username, password_hash, role) VALUES (?,?,?)",
        [
            ("admin",  _hash("Admin123"), "admin"),
            ("khalid", _hash("khalid11"), "investigator"),
            ("ayesha", _hash("ayesha11"), "investigator"),
            ("omar",   _hash("omar11"),   "analyst"),
        ],
    )

    cur.executemany(
        "INSERT INTO investigators (user_id,full_name,badge_number,specialization,contact_email,department) VALUES (?,?,?,?,?,?)",
        [
            (2, "Khalid Mahmood", "FIA-CW-001", "Network Forensics", "k.mahmood@fia.gov.pk",  "Cyber Crime Wing"),
            (3, "Ayesha Raza",    "FIA-DF-014", "Malware Analysis",  "a.raza@fia.gov.pk",     "Digital Forensics Lab"),
            (4, "Omar Siddiqui",  "FIA-DF-007", "Data Recovery",     "o.siddiqui@fia.gov.pk", "Digital Forensics Lab"),
        ],
    )

    cur.executemany(
        "INSERT INTO cases (case_number,title,case_type,status,priority,lead_investigator_id,opened_date,description,affected_org,jurisdiction) VALUES (?,?,?,?,?,?,?,?,?,?)",
        [
            ("CYB-2024-0001","BankAlfalah Ransomware Attack",      "ransomware",     "under_investigation","critical",1,"2024-01-15","LockBit 3.0 encrypted 3TB customer data. $500K Bitcoin demand.",          "Bank Alfalah Lahore",        "Punjab, Pakistan"),
            ("CYB-2024-0002","NADRA Citizen Database Breach",      "data_breach",    "open",               "critical",2,"2024-02-01","SQL injection on NADRA citizen portal. 2000+ malicious requests.",        "NADRA HQ Islamabad",         "Federal / Islamabad"),
            ("CYB-2024-0003","TeleNor Pakistan Phishing Campaign", "phishing",       "closed",             "high",    1,"2024-03-10","Spear phishing targeting 412 employees. Raccoon Stealer v2 deployed.",    "TeleNor Pakistan Karachi",   "Sindh, Pakistan"),
            ("CYB-2024-0004","FBR Insider Data Exfiltration",      "insider_threat", "open",               "high",    2,"2024-04-05","Employee copied 50,000 taxpayer records to personal USB drive.",          "FBR Islamabad",              "Federal / Islamabad"),
            ("CYB-2024-0005","HBL Internet Banking DDoS Attack",   "ddos",           "pending_review",     "medium",  3,"2024-05-20","Botnet of 4000+ IPs knocked HBL online banking offline for 6 hours.",    "Habib Bank Limited Karachi", "Sindh, Pakistan"),
        ],
    )

    cur.executemany(
        "INSERT INTO evidence (case_id,evidence_number,evidence_type,description,storage_location,collected_at,collected_by,status,file_size_bytes,source_ip) VALUES (?,?,?,?,?,?,?,?,?,?)",
        [
            (1,"EV-2024-0001-001","hard_disk",       "Infected server HDD 2TB — LockBit payload found",              "FIA Lab Cabinet A Slot 3",          "2024-01-16 09:30:00",1,"in_analysis",2000000000000,None),
            (1,"EV-2024-0001-002","network_capture", "FortiGate PCAP — C2 communication via Tor exit node port 443", "NAS Server /evidence/cyb2024-0001", "2024-01-16 11:00:00",1,"verified",    4500000,      "185.220.101.45"),
            (2,"EV-2024-0002-001","log_file",        "Apache logs — 2000+ SQL injection strings on NADRA portal",    "NAS Server /evidence/cyb2024-0002", "2024-02-02 14:00:00",2,"collected",   890000,       "103.248.10.78"),
            (3,"EV-2024-0003-001","email",           "Phishing email — spoofed hr@telenor.com.pk, Raccoon Stealer",  "Email Forensics Server",            "2024-03-11 10:00:00",3,"verified",    85000,        "91.108.4.202"),
            (4,"EV-2024-0004-001","usb_drive",       "32GB Kingston USB — encrypted partition, taxpayer records",    "FIA Lab Cabinet B Slot 1",          "2024-04-06 09:00:00",2,"in_analysis", 32000000000, None),
            (5,"EV-2024-0005-001","ip_trace",        "Botnet traffic — 4000+ IPs traced to Russian/Romanian hosting","NAS Server /evidence/cyb2024-0005", "2024-05-21 08:00:00",3,"collected",   120000,       "45.142.212.100"),
        ],
    )

    cur.executemany(
        "INSERT INTO evidence_integrity (evidence_id,sha256_hash,verified_by,is_tampered,notes) VALUES (?,?,?,?,?)",
        [
            (1,"a3f1c2e9b847d65f0a1b2c3d4e5f6789a3f1c2e9b847d65f0a1b2c3d4e5f678",1,0,"Hash verified on acquisition — clean"),
            (2,"b7e2d3f0c958e76a1b2c3d4e5f6789a0b7e2d3f0c958e76a1b2c3d4e5f6789a",1,0,"PCAP hash matches FortiGate export"),
            (3,"c9f3e4a1d069f87b2c3d4e5f6789a1b0c9f3e4a1d069f87b2c3d4e5f6789a1b",2,0,"Apache log verified clean"),
            (4,"d1e4f5a2b170a98c3d4e5f6789a2b1c0d1e4f5a2b170a98c3d4e5f6789a2b1c",3,0,"Email file hash confirmed"),
            (5,"e2f5a6b3c281ba9d4e5f6789a3c2d1e0e2f5a6b3c281ba9d4e5f6789a3c2d1e",2,1,"TAMPERED — hash mismatch on second verification"),
            (6,"f3a6b7c4d392cb0e5f6789a4d3e2f1a0f3a6b7c4d392cb0e5f6789a4d3e2f1a",3,0,"IP trace log verified clean"),
        ],
    )

    cur.executemany(
        "INSERT INTO chain_of_custody (evidence_id,handled_by,action_time,action_type,location,reason,witness_name) VALUES (?,?,?,?,?,?,?)",
        [
            (1,1,"2024-01-16 09:30:00","collected",  "BankAlfalah Server Room B2",  "Seized under FIA warrant FIA-W-2024-001",       "Bank Manager Mr. Tariq Ali"),
            (1,1,"2024-01-16 15:00:00","transferred","FIA Forensics Lab Lahore",    "Transported in sealed anti-static evidence bag", None),
            (1,2,"2024-01-17 09:00:00","analyzed",   "FIA Lab Workstation 3",       "Disk imaging via FTK Imager, write-blocker used",None),
            (1,1,"2024-01-25 16:00:00","stored",     "FIA Evidence Store Cabinet A","Analysis complete, stored pending court date",   "Lab Supervisor Mr. Bilal"),
            (2,1,"2024-01-16 11:30:00","collected",  "BankAlfalah NOC Room",        "PCAP exported from FortiGate 600E",              "IT Manager Mr. Hassan Raza"),
            (5,2,"2024-04-06 09:00:00","collected",  "FBR Office Workstation 14",   "Seized under warrant FIA-W-2024-008",            "HR Officer Ms. Nadia Hussain"),
            (5,2,"2024-04-06 14:00:00","transferred","FIA Forensics Lab Islamabad", "Transported for forensic imaging",               None),
        ],
    )

    cur.execute(
        "INSERT INTO case_reports (case_id,authored_by,report_title,findings,recommendations,verdict,submitted_at,is_final) VALUES (?,?,?,?,?,?,?,?)",
        (3,3,
         "Final Report — TeleNor Phishing Campaign CYB-2024-0003",
         "Spear phishing from spoofed domain hr-telenor.com.pk. Raccoon Stealer v2 harvested 12 credentials. Attacker IP traced to Selectel hosting Russia.",
         "Implement DMARC DKIM SPF. Quarterly phishing simulation. Deploy EDR on all endpoints.",
         "guilty","2024-04-20 10:00:00",1),
    )

    cur.executemany(
        "INSERT INTO access_logs (user_id,action,resource_accessed,ip_address,success,failure_reason) VALUES (?,?,?,?,?,?)",
        [
            (2,"LOGIN",          "dashboard",     "192.168.10.45",1,None),
            (2,"VIEW_EVIDENCE",  "evidence_id=1", "192.168.10.45",1,None),
            (3,"ADD_EVIDENCE",   "case_id=2",     "192.168.10.67",1,None),
            (4,"VIEW_CASE",      "case_id=1",     "192.168.10.88",1,None),
            (4,"DELETE_EVIDENCE","evidence_id=2", "192.168.10.88",0,"Permission denied — analyst cannot delete evidence"),
            (4,"CLOSE_CASE",     "case_id=3",     "192.168.10.88",0,"Permission denied — analyst cannot close cases"),
            (2,"LOGIN",          "dashboard",     "203.101.55.12",0,"Failed login — wrong password suspicious IP"),
        ],
    )
    conn.commit()


def init_db():
    """Create schema and seed sample data on first launch."""
    conn = get_connection()
    conn.executescript(SCHEMA_SQL)
    conn.commit()
    if conn.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 0:
        seed_sample_data(conn)
    conn.close()