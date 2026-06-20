# DFIS — Digital Forensics and Investigation System

A desktop-based Digital Forensics Investigation System built with **Python** and **CustomTkinter**, developed for the NIA Cyber Crime Division. The system supports role-based access control, SHA-256 evidence integrity verification, chain of custody tracking, and full case management workflows.

---

## Features

- **Secure Login** — SHA-256 password hashing with role-based access control (Admin / Investigator / Analyst)
- **Dashboard** — Real-time stat cards, bar chart of cases by type, donut chart of cases by status
- **Case Management** — Create, filter, and update investigation cases with auto-generated case numbers
- **Evidence Repository** — Submit and track digital evidence with automatic SHA-256 hash generation
- **Chain of Custody** — Full audit trail showing who handled each piece of evidence and when
- **Integrity Check** — Detect tampered evidence through hash verification
- **Investigation Reports** — Write and submit investigation reports with a verdict system
- **User Management** — Create and delete users (Admin only)
- **Access Logs** — Full security audit trail with failed login detection

---

## Screenshots

**Login Screen** — Secure access portal with username/password authentication and SHA-256 password verification.

<img width="1591" height="802" alt="image" src="https://github.com/user-attachments/assets/de50b5ea-162c-4bf7-8ecd-a20b04f25d3e" />




**Dashboard** — Real-time overview with stat cards, case-by-type bar chart, and case-by-status donut chart.

<img width="1586" height="871" alt="image" src="https://github.com/user-attachments/assets/dfd977ef-af1c-4f12-8763-7dbce2b53707" />




**Case Management** — Filterable case list with auto-generated case numbers and status updates.

<img width="1593" height="867" alt="image" src="https://github.com/user-attachments/assets/502c0576-5b35-4964-ba83-88073ed9015b" />




**User Management** — Admin-only screen to create and delete user accounts with role assignment.

<img width="1598" height="821" alt="image" src="https://github.com/user-attachments/assets/2eed046b-e620-407f-b7bb-16e7f1f478b7" />




**Access Logs** — Full security audit trail showing login attempts, actions, and failed access events.

<img width="1599" height="800" alt="image" src="https://github.com/user-attachments/assets/c228a980-d155-4b12-8440-a1fa56eb43eb" />




**Chain of Custody** — Step-by-step audit trail showing who handled each piece of evidence and when.

<img width="1598" height="762" alt="image" src="https://github.com/user-attachments/assets/ea8c8f00-af3b-4212-a7aa-34e9822543da" />


---

## Technology Stack

| Layer | Technology |
|---|---|
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
│   ├── database.py          # Schema, seed data, DB connection helpers
│   ├── auth.py               # Login logic, SHA-256 password verification
│   ├── case_service.py        # Case CRUD operations
│   ├── evidence_service.py    # Evidence CRUD + hash generation
│   ├── custody_service.py     # Chain of custody queries
│   ├── report_service.py      # Investigation report operations
│   └── user_service.py        # User management (create/delete/list)
├── frontend/
│   ├── app.py                 # Login window + main app window + sidebar
│   ├── dashboard.py           # Dashboard with stat cards and charts
│   ├── cases.py                # Case management UI (list + new case form)
│   ├── evidence.py             # Evidence repository UI (list + new evidence form)
│   ├── custody.py               # Chain of custody + integrity check UI
│   └── reports.py               # Reports + user management + access logs UI
├── main.py                     # Application entry point
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
pip install -r requirements.txt

# 3. Run the application
python main.py
```

The SQLite database (`dfis.db`) is created automatically on first run, along with sample data.

---

## Login Credentials

| Username | Password | Role |
|---|---|---|
| admin | Admin123 | Admin |
| khalid | khalid11 | Investigator |
| ayesha | ayesha11 | Investigator |
| omar | omar11 | Analyst |

---

## Backend and Database

SQLite is used as the local database, with all queries handled through a dedicated service layer in `backend/`. The schema includes:

- **8 tables** — `users`, `investigators`, `cases`, `evidence`, `evidence_integrity`, `chain_of_custody`, `case_reports`, `access_logs`
- **Sample data** — 5 realistic cybercrime cases (ransomware, data breach, phishing, insider threat, DDoS)
- **SHA-256 hashing** is used in two places: password storage during login, and evidence integrity verification

This separation between `frontend/` (UI) and `backend/` (data and business logic) keeps the codebase modular and easy to maintain.

---

## Team Contributions

| Member | Roll No. | GitHub | Module |
|---|---|---|---|
| Malik Abubakar (Lead) | F2024408134 | [@a3ubakarr](https://github.com/a3ubakarr) | Login, Dashboard, Database, Auth, User Service |
| Mohsan Raza | F2024408140 | [@mosh-roid](https://github.com/mosh-roid) | Case Management Module |
| Saad Iftikhar | F2024408050 | [@saadx911](https://github.com/saadx911) | Evidence Repository Module |
| Abdullah Baig | F2024408137 | [@MAB-22](https://github.com/MAB-22) | Custody, Reports, User Management |

---

## Pull Requests

| PR | Description | Author | Status |
|---|---|---|---|
| [#4](https://github.com/a3ubakarr/Digital-Forensics-Investigation-System/pull/4) | Login screen, dashboard module and database setup | a3ubakarr | Merged |
| [#5](https://github.com/a3ubakarr/Digital-Forensics-Investigation-System/pull/5) | Cases module | a3ubakarr | Merged |
| [#9](https://github.com/a3ubakarr/Digital-Forensics-Investigation-System/pull/9) | Custody and reports python files | MAB-22 | Merged |
| [#10](https://github.com/a3ubakarr/Digital-Forensics-Investigation-System/pull/10) | Evidence service and evidence UI module | saadx911 | Merged |
| [#11](https://github.com/a3ubakarr/Digital-Forensics-Investigation-System/pull/11) | Restructure cases into frontend/backend architecture | mosh-roid | Merged |

---

## GitHub Issues

- [#1 — Build Login and Dashboard](https://github.com/a3ubakarr/Digital-Forensics-Investigation-System/issues/1)
- [#2 — Build Cases Module](https://github.com/a3ubakarr/Digital-Forensics-Investigation-System/issues/2)
- [#3 — Build Evidence Module](https://github.com/a3ubakarr/Digital-Forensics-Investigation-System/issues/3)
- [#4 — Build Custody and Reports Module](https://github.com/a3ubakarr/Digital-Forensics-Investigation-System/issues/4)

---

## Troubleshooting

| Issue | Solution |
|---|---|
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` again after activating your virtual environment |
| Database not found | `dfis.db` is auto-created on first run — make sure you run `python main.py` from the project root folder |
| Charts not displaying | Reinstall matplotlib: `pip install matplotlib --upgrade` |
