"""
DFIS - Digital Forensics Investigation System
File        : reports.py
Description : Investigation Reports + User Management + Access Logs
Developer   : Member 4
"""

import customtkinter as ctk
import hashlib
from datetime import datetime
from database import run_query, execute_command

BG_DARK   = "#060a18"
BG_CARD   = "#0a0e1e"
BG_INPUT  = "#0f1428"
PURPLE    = "#6366f1"
PURPLE2   = "#8b5cf6"
PURPLE_DIM= "#312e81"
TEXT_MAIN = "#e2e8f0"
TEXT_DIM  = "#a0aec0"
TEXT_FAINT= "#4a5568"
TEXT_GHOST= "#2d3748"
SEP_COLOR = "#1a202c"
GREEN     = "#22c55e"
RED       = "#ef4444"
RED_DARK  = "#7f1d1d"
ORANGE    = "#fb923c"
BLUE      = "#60a5fa"

VERDICTS = ["pending", "guilty", "not_guilty", "inconclusive", "referred"]
ROLES    = ["investigator", "analyst"]


def _gen_badge():
    year = datetime.now().year
    rows = run_query(
        f"SELECT COUNT(*) FROM investigators WHERE badge_number LIKE 'FIA-{year}-%'"
    )
    n = (rows[0][0] if rows else 0) + 1
    return f"FIA-{year}-{str(n).zfill(3)}"


class ReportsFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, session, mode="reports", **kwargs):
        super().__init__(master, **kwargs)
        self.session = session
        self.mode    = mode
        self.configure(scrollbar_button_color=BG_DARK)
        self._build()

    def _build(self):
        if self.mode == "users":
            self._build_users()
        elif self.mode == "logs":
            self._build_logs()
        else:
            self._build_reports()

    # --------------------------------------------------
    #  REPORTS
    # --------------------------------------------------
    def _build_reports(self):
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.pack(fill="x", padx=28, pady=(22, 0))
        ctk.CTkLabel(hdr, text="Investigation Reports",
                     font=ctk.CTkFont(size=22, weight="bold"),
                     text_color="#ffffff").pack(anchor="w")

        ctk.CTkFrame(self, fg_color=SEP_COLOR, height=1).pack(
            fill="x", padx=28, pady=14)

        rows = run_query(
            """SELECT cr.report_title, c.case_number, i.full_name AS authored_by,
                      cr.verdict, cr.created_at, cr.is_final,
                      cr.findings, cr.recommendations
               FROM case_reports cr
               JOIN cases c ON cr.case_id = c.case_id
               JOIN investigators i ON cr.authored_by = i.investigator_id
               ORDER BY cr.created_at DESC"""
        )

        if rows:
            for row in rows:
                self._report_card(row)
        else:
            ctk.CTkLabel(self, text="No reports submitted yet.",
                         font=ctk.CTkFont(size=13),
                         text_color=TEXT_DIM).pack(pady=20)

        ctk.CTkFrame(self, fg_color=SEP_COLOR, height=1).pack(
            fill="x", padx=28, pady=14)
        ctk.CTkLabel(self, text="Write New Report",
                     font=ctk.CTkFont(size=16, weight="bold"),
                     text_color=TEXT_MAIN).pack(padx=28, anchor="w", pady=(0, 10))
        self._build_report_form()

    def _report_card(self, row):
        is_final = bool(row["is_final"])
        lbl      = "Final" if is_final else "Draft"
        clr      = GREEN if is_final else ORANGE

        card = ctk.CTkFrame(self, fg_color=BG_CARD,
                             border_color=PURPLE_DIM, border_width=1,
                             corner_radius=12)
        card.pack(fill="x", padx=28, pady=4)
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=18, pady=14)

        top = ctk.CTkFrame(inner, fg_color="transparent")
        top.pack(fill="x")
        ctk.CTkLabel(top, text=f"  {lbl}  ",
                     font=ctk.CTkFont(size=9, weight="bold"),
                     fg_color=TEXT_GHOST, text_color=clr,
                     corner_radius=8).pack(side="left")
        ctk.CTkLabel(top, text=f"  {row['report_title']}",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color="#ffffff").pack(side="left")
        ctk.CTkLabel(top, text=row["case_number"],
                     font=ctk.CTkFont(size=10),
                     text_color=TEXT_FAINT).pack(side="right")

        meta = (f"Author: {row['authored_by']}  |  "
                f"Verdict: {row['verdict'].upper()}  |  {row['created_at']}")
        ctk.CTkLabel(inner, text=meta,
                     font=ctk.CTkFont(size=10),
                     text_color=TEXT_FAINT).pack(anchor="w", pady=(6, 6))

        f_frame = ctk.CTkFrame(inner, fg_color=BG_INPUT,
                                border_color=PURPLE_DIM, border_width=1,
                                corner_radius=8)
        f_frame.pack(fill="x", pady=(0, 6))
        ctk.CTkLabel(f_frame, text="FINDINGS",
                     font=ctk.CTkFont(size=9, weight="bold"),
                     text_color=TEXT_DIM).pack(padx=12, pady=(8, 2), anchor="w")
        ctk.CTkLabel(f_frame, text=row["findings"],
                     font=ctk.CTkFont(size=11), text_color=TEXT_MAIN,
                     wraplength=750, justify="left").pack(padx=12, pady=(0, 8), anchor="w")

        if row["recommendations"]:
            r_frame = ctk.CTkFrame(inner, fg_color=BG_INPUT,
                                    border_color=PURPLE_DIM, border_width=1,
                                    corner_radius=8)
            r_frame.pack(fill="x")
            ctk.CTkLabel(r_frame, text="RECOMMENDATIONS",
                         font=ctk.CTkFont(size=9, weight="bold"),
                         text_color=TEXT_DIM).pack(padx=12, pady=(8, 2), anchor="w")
            ctk.CTkLabel(r_frame, text=row["recommendations"],
                         font=ctk.CTkFont(size=11), text_color=TEXT_MAIN,
                         wraplength=750, justify="left").pack(padx=12, pady=(0, 8), anchor="w")

    def _build_report_form(self):
        form = ctk.CTkFrame(self, fg_color=BG_CARD,
                             border_color=PURPLE_DIM, border_width=1,
                             corner_radius=16)
        form.pack(fill="x", padx=28, pady=(0, 28))
        inner = ctk.CTkFrame(form, fg_color="transparent")
        inner.pack(fill="x", padx=28, pady=24)

        cases = run_query("SELECT case_id, case_number, title FROM cases")
        self.case_map = {
            f"{r['case_number']} - {r['title']}": r["case_id"] for r in cases
        }
        invs = run_query("SELECT investigator_id, full_name FROM investigators")
        self.inv_map = {r["full_name"]: r["investigator_id"] for r in invs}

        self._lbl(inner, "CASE *")
        self.rpt_case_var = ctk.StringVar(
            value=list(self.case_map.keys())[0] if self.case_map else "")
        ctk.CTkOptionMenu(inner, values=list(self.case_map.keys()),
                          variable=self.rpt_case_var,
                          fg_color=BG_INPUT, button_color=PURPLE,
                          button_hover_color=PURPLE2, text_color=TEXT_MAIN
                          ).pack(fill="x", pady=(4, 14))

        self._lbl(inner, "REPORT TITLE *")
        self.rpt_title = self._entry(
            inner, "e.g. Final Investigation Report - BankAlfalah Ransomware")

        # Row: author + verdict (pack side by side)
        r1 = ctk.CTkFrame(inner, fg_color="transparent")
        r1.pack(fill="x", pady=(0, 14))

        auth_col = ctk.CTkFrame(r1, fg_color="transparent")
        auth_col.pack(side="left", fill="x", expand=True, padx=(0, 6))
        self._lbl(auth_col, "AUTHORED BY *")
        inv_names = list(self.inv_map.keys())
        self.rpt_auth_var = ctk.StringVar(value=inv_names[0] if inv_names else "")
        ctk.CTkOptionMenu(auth_col, values=inv_names, variable=self.rpt_auth_var,
                          fg_color=BG_INPUT, button_color=PURPLE,
                          button_hover_color=PURPLE2, text_color=TEXT_MAIN
                          ).pack(fill="x", pady=(4, 0))

        verdict_col = ctk.CTkFrame(r1, fg_color="transparent")
        verdict_col.pack(side="left", fill="x", expand=True, padx=(6, 0))
        self._lbl(verdict_col, "VERDICT *")
        self.rpt_verdict_var = ctk.StringVar(value="pending")
        ctk.CTkOptionMenu(verdict_col, values=VERDICTS,
                          variable=self.rpt_verdict_var,
                          fg_color=BG_INPUT, button_color=PURPLE,
                          button_hover_color=PURPLE2, text_color=TEXT_MAIN
                          ).pack(fill="x", pady=(4, 0))

        self._lbl(inner, "FINDINGS *")
        self.rpt_findings = ctk.CTkTextbox(
            inner, height=90, fg_color=BG_INPUT,
            border_color=PURPLE_DIM, border_width=1,
            text_color=TEXT_MAIN, corner_radius=10)
        self.rpt_findings.pack(fill="x", pady=(4, 14))

        self._lbl(inner, "RECOMMENDATIONS (OPTIONAL)")
        self.rpt_recs = ctk.CTkTextbox(
            inner, height=70, fg_color=BG_INPUT,
            border_color=PURPLE_DIM, border_width=1,
            text_color=TEXT_MAIN, corner_radius=10)
        self.rpt_recs.pack(fill="x", pady=(4, 14))

        self.is_final_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(inner, text="Mark as Final Report",
                        variable=self.is_final_var,
                        fg_color=PURPLE, hover_color=PURPLE2,
                        text_color=TEXT_MAIN).pack(anchor="w", pady=(0, 12))

        self.rpt_msg = ctk.CTkLabel(inner, text="",
                                     font=ctk.CTkFont(size=12),
                                     text_color=GREEN)
        self.rpt_msg.pack()

        ctk.CTkButton(inner, text="Submit Report", height=46,
                      fg_color=PURPLE, hover_color=PURPLE2,
                      font=ctk.CTkFont(size=15, weight="bold"),
                      corner_radius=10, command=self._submit_report
                      ).pack(fill="x", pady=(8, 0))

    def _submit_report(self):
        title    = self.rpt_title.get().strip()
        findings = self.rpt_findings.get("1.0", "end").strip()
        if not title or not findings:
            self.rpt_msg.configure(
                text="Please fill all required (*) fields.", text_color=RED)
            return
        try:
            execute_command(
                "INSERT INTO case_reports (case_id,authored_by,report_title,"
                "findings,recommendations,verdict,submitted_at,is_final)"
                " VALUES (?,?,?,?,?,?,?,?)",
                (self.case_map[self.rpt_case_var.get()],
                 self.inv_map[self.rpt_auth_var.get()],
                 title, findings,
                 self.rpt_recs.get("1.0", "end").strip(),
                 self.rpt_verdict_var.get(),
                 str(datetime.now()),
                 1 if self.is_final_var.get() else 0)
            )
            self.rpt_msg.configure(
                text="Report submitted successfully.", text_color=GREEN)
            self.rpt_title.delete(0, "end")
            self.rpt_findings.delete("1.0", "end")
            self.rpt_recs.delete("1.0", "end")
        except Exception as e:
            self.rpt_msg.configure(text=f"Error: {e}", text_color=RED)

    # --------------------------------------------------
    #  USER MANAGEMENT
    # --------------------------------------------------
    def _build_users(self):
        if self.session["role"] != "admin":
            ctk.CTkLabel(self, text="Access Denied - Admin only",
                         font=ctk.CTkFont(size=16),
                         text_color=RED).pack(pady=40)
            return

        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.pack(fill="x", padx=28, pady=(22, 0))
        ctk.CTkLabel(hdr, text="User Management",
                     font=ctk.CTkFont(size=22, weight="bold"),
                     text_color="#ffffff").pack(anchor="w")

        ctk.CTkFrame(self, fg_color=SEP_COLOR, height=1).pack(
            fill="x", padx=28, pady=14)

        rows = run_query(
            """SELECT u.user_id, u.username, u.role, u.is_active,
                      u.created_at, u.last_login,
                      COALESCE(i.full_name,'N/A')    AS full_name,
                      COALESCE(i.badge_number,'N/A') AS badge_number,
                      COALESCE(i.department,'N/A')   AS department
               FROM users u
               LEFT JOIN investigators i ON u.user_id = i.user_id
               ORDER BY u.created_at DESC"""
        )

        for row in rows:
            card = ctk.CTkFrame(self, fg_color=BG_CARD,
                                 border_color=PURPLE_DIM, border_width=1,
                                 corner_radius=12)
            card.pack(fill="x", padx=28, pady=4)
            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(fill="x", padx=18, pady=12)

            top = ctk.CTkFrame(inner, fg_color="transparent")
            top.pack(fill="x")
            ctk.CTkLabel(top, text=row["username"],
                         font=ctk.CTkFont(size=14, weight="bold"),
                         text_color="#ffffff").pack(side="left")
            role_clr = {
                "admin": RED, "investigator": PURPLE, "analyst": BLUE
            }.get(row["role"], TEXT_MAIN)
            ctk.CTkLabel(top, text=f"  {row['role'].upper()}  ",
                         font=ctk.CTkFont(size=9, weight="bold"),
                         fg_color=TEXT_GHOST, text_color=role_clr,
                         corner_radius=8).pack(side="left", padx=8)
            active_clr = GREEN if row["is_active"] else RED
            ctk.CTkLabel(top,
                         text="ACTIVE" if row["is_active"] else "INACTIVE",
                         font=ctk.CTkFont(size=9),
                         text_color=active_clr).pack(side="right")

            meta = (f"Name: {row['full_name']}  |  "
                    f"Badge: {row['badge_number']}  |  "
                    f"Dept: {row['department']}")
            ctk.CTkLabel(inner, text=meta,
                         font=ctk.CTkFont(size=10),
                         text_color=TEXT_FAINT).pack(anchor="w", pady=(4, 0))
            if row["last_login"]:
                ctk.CTkLabel(inner,
                             text=f"Last login: {row['last_login']}",
                             font=ctk.CTkFont(size=10),
                             text_color=TEXT_FAINT).pack(anchor="w")

            # Delete button - admin cannot delete themselves
            if row["username"] != self.session["username"]:
                uid   = row["user_id"]
                uname = row["username"]
                def _del_user(u_id=uid, u_name=uname):
                    self._confirm_delete_user(u_id, u_name)
                ctk.CTkButton(inner, text="Delete User",
                              width=120, height=30,
                              fg_color=RED_DARK, hover_color=RED,
                              text_color="#ffffff",
                              font=ctk.CTkFont(size=11, weight="bold"),
                              corner_radius=8,
                              command=_del_user).pack(anchor="w", pady=(8, 0))

        ctk.CTkFrame(self, fg_color=SEP_COLOR, height=1).pack(
            fill="x", padx=28, pady=14)
        ctk.CTkLabel(self, text="Create New User",
                     font=ctk.CTkFont(size=16, weight="bold"),
                     text_color=TEXT_MAIN).pack(padx=28, anchor="w", pady=(0, 10))
        self._build_create_user()

    def _confirm_delete_user(self, user_id, username):
        """Show confirmation popup before deleting user."""
        popup = ctk.CTkToplevel()
        popup.title("Confirm Delete")
        popup.geometry("360x180")
        popup.resizable(False, False)
        popup.configure(fg_color=BG_DARK)
        popup.grab_set()

        # Center popup
        popup.update_idletasks()
        x = (popup.winfo_screenwidth()  - 360) // 2
        y = (popup.winfo_screenheight() - 180) // 2
        popup.geometry(f"360x180+{x}+{y}")

        ctk.CTkLabel(popup, text="Delete User?",
                     font=ctk.CTkFont(size=16, weight="bold"),
                     text_color="#ffffff").pack(pady=(24, 6))
        ctk.CTkLabel(popup,
                     text=f"This will permanently delete '{username}'.",
                     font=ctk.CTkFont(size=12), text_color=TEXT_DIM).pack()

        btn_row = ctk.CTkFrame(popup, fg_color="transparent")
        btn_row.pack(pady=20)

        def _do_delete():
            try:
                execute_command(
                    "DELETE FROM investigators WHERE user_id=?", (user_id,))
                execute_command(
                    "DELETE FROM users WHERE user_id=?", (user_id,))
            except Exception:
                pass
            popup.destroy()
            # Refresh page
            for w in self.winfo_children():
                w.destroy()
            self._build_users()

        ctk.CTkButton(btn_row, text="Delete", width=120, height=36,
                      fg_color=RED_DARK, hover_color=RED,
                      text_color="#ffffff",
                      font=ctk.CTkFont(size=13, weight="bold"),
                      corner_radius=8,
                      command=_do_delete).pack(side="left", padx=8)

        ctk.CTkButton(btn_row, text="Cancel", width=120, height=36,
                      fg_color=BG_CARD, hover_color=PURPLE_DIM,
                      text_color=TEXT_MAIN,
                      font=ctk.CTkFont(size=13),
                      corner_radius=8,
                      command=popup.destroy).pack(side="left", padx=8)

    def _build_create_user(self):
        auto_badge = _gen_badge()

        form = ctk.CTkFrame(self, fg_color=BG_CARD,
                             border_color=PURPLE_DIM, border_width=1,
                             corner_radius=16)
        form.pack(fill="x", padx=28, pady=(0, 28))
        inner = ctk.CTkFrame(form, fg_color="transparent")
        inner.pack(fill="x", padx=28, pady=24)

        self._lbl(inner, "BADGE NUMBER (AUTO)")
        ctk.CTkEntry(inner, textvariable=ctk.StringVar(value=auto_badge),
                     state="disabled", fg_color=BG_INPUT,
                     text_color="#a5b4fc", border_color=PURPLE_DIM,
                     height=40, corner_radius=10).pack(fill="x", pady=(4, 14))

        # Row 1: username + password
        r1 = ctk.CTkFrame(inner, fg_color="transparent")
        r1.pack(fill="x", pady=(0, 14))

        u_col = ctk.CTkFrame(r1, fg_color="transparent")
        u_col.pack(side="left", fill="x", expand=True, padx=(0, 6))
        self._lbl(u_col, "USERNAME *")
        self.new_username = ctk.CTkEntry(
            u_col, placeholder_text="e.g. ali_hassan",
            fg_color=BG_INPUT, border_color=PURPLE_DIM,
            text_color=TEXT_MAIN, placeholder_text_color=TEXT_FAINT,
            height=40, corner_radius=10)
        self.new_username.pack(fill="x", pady=(4, 0))

        p_col = ctk.CTkFrame(r1, fg_color="transparent")
        p_col.pack(side="left", fill="x", expand=True, padx=(6, 0))
        self._lbl(p_col, "PASSWORD *")
        self.new_password = ctk.CTkEntry(
            p_col, placeholder_text="Min 6 characters", show="*",
            fg_color=BG_INPUT, border_color=PURPLE_DIM,
            text_color=TEXT_MAIN, placeholder_text_color=TEXT_FAINT,
            height=40, corner_radius=10)
        self.new_password.pack(fill="x", pady=(4, 0))

        # Row 2: role + full name
        r2 = ctk.CTkFrame(inner, fg_color="transparent")
        r2.pack(fill="x", pady=(14, 14))

        role_col = ctk.CTkFrame(r2, fg_color="transparent")
        role_col.pack(side="left", fill="x", expand=True, padx=(0, 6))
        self._lbl(role_col, "ROLE *")
        self.new_role_var = ctk.StringVar(value="investigator")
        ctk.CTkOptionMenu(role_col, values=ROLES, variable=self.new_role_var,
                          fg_color=BG_INPUT, button_color=PURPLE,
                          button_hover_color=PURPLE2, text_color=TEXT_MAIN
                          ).pack(fill="x", pady=(4, 0))

        name_col = ctk.CTkFrame(r2, fg_color="transparent")
        name_col.pack(side="left", fill="x", expand=True, padx=(6, 0))
        self._lbl(name_col, "FULL NAME *")
        self.new_fullname = ctk.CTkEntry(
            name_col, placeholder_text="e.g. Ali Hassan Khan",
            fg_color=BG_INPUT, border_color=PURPLE_DIM,
            text_color=TEXT_MAIN, placeholder_text_color=TEXT_FAINT,
            height=40, corner_radius=10)
        self.new_fullname.pack(fill="x", pady=(4, 0))

        self._lbl(inner, "CONTACT EMAIL *")
        self.new_email = self._entry(inner, "e.g. ali.hassan@fia.gov.pk")

        self.user_msg = ctk.CTkLabel(inner, text="",
                                      font=ctk.CTkFont(size=12),
                                      text_color=GREEN)
        self.user_msg.pack()

        ctk.CTkButton(inner, text="Create User", height=46,
                      fg_color=PURPLE, hover_color=PURPLE2,
                      font=ctk.CTkFont(size=15, weight="bold"),
                      corner_radius=10,
                      command=lambda b=auto_badge: self._create_user(b)
                      ).pack(fill="x", pady=(8, 0))

    def _create_user(self, badge):
        uname = self.new_username.get().strip()
        pw    = self.new_password.get().strip()
        fname = self.new_fullname.get().strip()
        email = self.new_email.get().strip()

        if not all([uname, pw, fname, email]):
            self.user_msg.configure(
                text="Please fill all required (*) fields.", text_color=RED)
            return
        try:
            pw_hash = hashlib.sha256(pw.encode()).hexdigest().upper()
            uid = execute_command(
                "INSERT INTO users (username,password_hash,role) VALUES (?,?,?)",
                (uname, pw_hash, self.new_role_var.get())
            )
            execute_command(
                "INSERT INTO investigators "
                "(user_id,full_name,badge_number,contact_email) VALUES (?,?,?,?)",
                (uid, fname, badge, email)
            )
            self.user_msg.configure(
                text=f"User '{uname}' created with badge {badge}.",
                text_color=GREEN)
            self.new_username.delete(0, "end")
            self.new_password.delete(0, "end")
            self.new_fullname.delete(0, "end")
            self.new_email.delete(0, "end")
        except Exception as e:
            self.user_msg.configure(text=f"Error: {e}", text_color=RED)

    # --------------------------------------------------
    #  ACCESS LOGS
    # --------------------------------------------------
    def _build_logs(self):
        if self.session["role"] != "admin":
            ctk.CTkLabel(self, text="Access Denied - Admin only",
                         font=ctk.CTkFont(size=16),
                         text_color=RED).pack(pady=40)
            return

        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.pack(fill="x", padx=28, pady=(22, 0))
        ctk.CTkLabel(hdr, text="Security Audit - Access Logs",
                     font=ctk.CTkFont(size=22, weight="bold"),
                     text_color="#ffffff").pack(anchor="w")

        ctk.CTkFrame(self, fg_color=SEP_COLOR, height=1).pack(
            fill="x", padx=28, pady=14)

        rows = run_query(
            """SELECT u.username, u.role, al.action,
                      al.resource_accessed, al.action_time,
                      al.ip_address, al.success, al.failure_reason
               FROM access_logs al
               JOIN users u ON al.user_id = u.user_id
               ORDER BY al.action_time DESC"""
        )

        failed = [r for r in rows if not r["success"]]
        if failed:
            alert = ctk.CTkFrame(self, fg_color=RED_DARK,
                                  border_color=RED, border_width=1,
                                  corner_radius=10)
            alert.pack(fill="x", padx=28, pady=(0, 10))
            ctk.CTkLabel(alert,
                         text=f"{len(failed)} failed access attempt(s) detected",
                         font=ctk.CTkFont(size=13, weight="bold"),
                         text_color="#ffffff").pack(padx=16, pady=10)

        ctk.CTkLabel(self, text="Full Audit Log",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=TEXT_MAIN).pack(padx=28, anchor="w", pady=(0, 8))

        for row in rows:
            success = bool(row["success"])
            clr = GREEN if success else RED

            card = ctk.CTkFrame(self, fg_color=BG_CARD,
                                 border_color=PURPLE_DIM, border_width=1,
                                 corner_radius=10)
            card.pack(fill="x", padx=28, pady=3)
            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(fill="x", padx=16, pady=10)

            top = ctk.CTkFrame(inner, fg_color="transparent")
            top.pack(fill="x")
            ctk.CTkLabel(top, text=row["action"],
                         font=ctk.CTkFont(size=12, weight="bold"),
                         text_color="#ffffff").pack(side="left")
            ctk.CTkLabel(top,
                         text=f"  {'SUCCESS' if success else 'FAILED'}  ",
                         font=ctk.CTkFont(size=9, weight="bold"),
                         fg_color=TEXT_GHOST, text_color=clr,
                         corner_radius=8).pack(side="left", padx=8)
            ctk.CTkLabel(top, text=str(row["action_time"]),
                         font=ctk.CTkFont(size=9),
                         text_color=TEXT_FAINT).pack(side="right")

            meta = (f"User: {row['username']} ({row['role']})  |  "
                    f"IP: {row['ip_address']}  |  "
                    f"Resource: {row['resource_accessed']}")
            ctk.CTkLabel(inner, text=meta,
                         font=ctk.CTkFont(size=10),
                         text_color=TEXT_FAINT).pack(anchor="w", pady=(2, 0))

            if row["failure_reason"]:
                ctk.CTkLabel(inner, text=f"Reason: {row['failure_reason']}",
                             font=ctk.CTkFont(size=10),
                             text_color=ORANGE).pack(anchor="w")

        ctk.CTkFrame(self, fg_color="transparent", height=28).pack()

    # Helpers
    def _lbl(self, parent, text):
        ctk.CTkLabel(parent, text=text,
                     font=ctk.CTkFont(size=10, weight="bold"),
                     text_color=TEXT_DIM).pack(anchor="w")

    def _entry(self, parent, placeholder, pady=(4, 14)):
        e = ctk.CTkEntry(parent, placeholder_text=placeholder,
                         fg_color=BG_INPUT, border_color=PURPLE_DIM,
                         text_color=TEXT_MAIN,
                         placeholder_text_color=TEXT_FAINT,
                         height=40, corner_radius=10)
        e.pack(fill="x", pady=pady)
        return e