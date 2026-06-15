# DFIS — Digital Forensics and Investigation System

A desktop-based Digital Forensics Investigation System built with **Python** and **CustomTkinter**, developed for the NIA Cyber Crime Division. Features role-based access control, SHA-256 evidence integrity verification, chain of custody tracking, and full case management.

---

## Features

- **Secure Login** — SHA-256 password hashing, role-based access control (Admin / Investigator / Analyst)
- **Dashboard** — Real-time stat cards, bar chart (cases by type), donut chart (cases by status)
- **Case Management** — Create, filter, and update investigation cases with auto-generated case numbers
- **Evidence Repository** — Submit and track digital evidence with auto SHA-256 hash generation
- **Chain of Custody** — Full audit trail for every evidence item
- **Integrity Check** — Detect tampered evidence through hash verification
- **Investigation Reports** — Write and submit investigation reports with verdict system
- **User Management** — Create and delete users (Admin only)
- **Access Logs** — Full security audit trail with failed login detection

---

## Technology Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Python, CustomTkinter |
| Backend | Python (service layer) |
| Database | SQLite |
| Charts | Matplotlib |
| Hashing | SHA-256 (hashlib) |
| Version Control | Git / GitHub |

---

## Project Structure

```
Digital-Forensics-Investigation-System/
├── backend/
│   ├── database.py          # Schema, seed data, DB helpers
│   ├── auth.py              # Login, SHA-256 password verification
│   ├── case_service.py      # Case CRUD operations
│   ├── evidence_service.py  # Evidence CRUD + hash generation
│   ├── custody_service.py   # Chain of custody queries
│   ├── report_service.py    # Report operations
│   └── user_service.py      # User management
├── frontend/
│   ├── app.py               # Login window + main app window
│   ├── dashboard.py         # Dashboard with charts
│   ├── cases.py             # Case management UI
│   ├── evidence.py          # Evidence repository UI
│   ├── custody.py           # Chain of custody + integrity check UI
│   └── reports.py           # Reports + user management + access logs UI
├── main.py                  # Entry point
└── requirements.txt
```

---

## Setup and Installation

### Requirements
- Python 3.10 or 3.11 (recommended)
- pip

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/a3ubakarr/Digital-Forensics-Investigation-System.git
cd Digital-Forensics-Investigation-System

# 2. Install dependencies
pip install customtkinter matplotlib pillow

# 3. Run the application
python main.py
```

---

## Login Credentials

| Username | Password | Role |
|----------|----------|------|
| admin | Admin123 | Admin |
| khalid | khalid11 | Investigator |
| ayesha | ayesha11 | Investigator |
| omar | omar11 | Analyst |

---

## Backend / Database

SQLite is used as the database (`dfis.db` — auto-created on first run). The database includes:

- **7 tables** — users, investigators, cases, evidence, evidence_integrity, chain_of_custody, case_reports, access_logs
- **Sample data** — 5 real Pakistani cybercrime cases (BankAlfalah ransomware, NADRA breach, TeleNor phishing, FBR insider threat, HBL DDoS)
- **SHA-256 hashing** used in two places: password storage and evidence integrity verification

---

## Team Contributions

| Member | Roll No. | GitHub | Module |
|--------|----------|--------|--------|
| Malik Abubakar (Lead) | F2024408134 | [@a3ubakarr](https://github.com/a3ubakarr) | Login, Dashboard, Database, Auth, User Service |
| Mohsan Raza | F2024408140 | [@mosh-roid](https://github.com/mosh-roid) | Cases Module |
| Saad Iftikhar | F2024408050 | [@saadx911](https://github.com/saadx911) | Evidence Module |
| Abdullah Baig | F2024408137 | [@MAB-22](https://github.com/MAB-22) | Custody, Reports, User Management |

---

## Pull Requests

- [PR #4 — Login UI and Dashboard](https://github.com/a3ubakarr/Digital-Forensics-Investigation-System/pull/4)
- [PR #5 — Cases Module](https://github.com/a3ubakarr/Digital-Forensics-Investigation-System/pull/5)
- [PR #7 — Evidence Module](https://github.com/a3ubakarr/Digital-Forensics-Investigation-System/pull/7)
- [PR #8 — Full Project Restructure](https://github.com/a3ubakarr/Digital-Forensics-Investigation-System/pull/8)

---

## GitHub Issues

- [Issue #1 — Build Login and Dashboard](https://github.com/a3ubakarr/Digital-Forensics-Investigation-System/issues/1)
- [Issue #2 — Build Cases Module](https://github.com/a3ubakarr/Digital-Forensics-Investigation-System/issues/2)
- [Issue #3 — Build Evidence Module](https://github.com/a3ubakarr/Digital-Forensics-Investigation-System/issues/3)
- [Issue #4 — Build Custody and Reports Module](https://github.com/a3ubakarr/Digital-Forensics-Investigation-System/issues/4)
