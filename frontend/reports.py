import customtkinter as ctk
from backend.report_service import get_all_reports, submit_report, get_all_cases_for_report
from backend.user_service import get_all_users, gen_badge_number, create_user, delete_user, get_access_logs, get_all_investigators

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

    def _build_reports(self):
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.pack(fill="x", padx=28, pady=(22, 0))
        ctk.CTkLabel(hdr, text="Investigation Reports",
                     font=ctk.CTkFont(size=22, weight="bold"), text_color="#ffffff").pack(anchor="w")
        ctk.CTkFrame(self, fg_color=SEP_COLOR, height=1).pack(fill="x", padx=28, pady=14)

        rows = get_all_reports()
        if rows:
            for row in rows:
                self._report_card(row)
        else:
            ctk.CTkLabel(self, text="No reports submitted yet.",
                         font=ctk.CTkFont(size=13), text_color=TEXT_DIM).pack(pady=20)

        ctk.CTkFrame(self, fg_color=SEP_COLOR, height=1).pack(fill="x", padx=28, pady=14)
        ctk.CTkLabel(self, text="Write New Report",
                     font=ctk.CTkFont(size=16, weight="bold"),
                     text_color=TEXT_MAIN).pack(padx=28, anchor="w", pady=(0, 10))
        self._build_report_form()

    def _report_card(self, row):
        clr = GREEN if row["is_final"] else ORANGE
        lbl = "Final" if row["is_final"] else "Draft"
        card = ctk.CTkFrame(self, fg_color=BG_CARD,
                             border_color=PURPLE_DIM, border_width=1, corner_radius=12)
        card.pack(fill="x", padx=28, pady=4)
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=18, pady=14)

        top = ctk.CTkFrame(inner, fg_color="transparent")
        top.pack(fill="x")
        ctk.CTkLabel(top, text=f"  {lbl}  ",
                     font=ctk.CTkFont(size=9, weight="bold"),
                     fg_color=TEXT_GHOST, text_color=clr, corner_radius=8).pack(side="left")
        ctk.CTkLabel(top, text=f"  {row['report_title']}",
                     font=ctk.CTkFont(size=13, weight="bold"), text_color="#ffffff").pack(side="left")
        ctk.CTkLabel(top, text=row["case_number"],
                     font=ctk.CTkFont(size=10), text_color=TEXT_FAINT).pack(side="right")

        ctk.CTkLabel(inner,
                     text=f"Author: {row['authored_by']}  |  Verdict: {row['verdict'].upper()}  |  {row['created_at']}",
                     font=ctk.CTkFont(size=10), text_color=TEXT_FAINT).pack(anchor="w", pady=(6, 6))

        f_frame = ctk.CTkFrame(inner, fg_color=BG_INPUT,
                                border_color=PURPLE_DIM, border_width=1, corner_radius=8)
        f_frame.pack(fill="x", pady=(0, 6))
        ctk.CTkLabel(f_frame, text="FINDINGS", font=ctk.CTkFont(size=9, weight="bold"),
                     text_color=TEXT_DIM).pack(padx=12, pady=(8, 2), anchor="w")
        ctk.CTkLabel(f_frame, text=row["findings"], font=ctk.CTkFont(size=11),
                     text_color=TEXT_MAIN, wraplength=750, justify="left").pack(padx=12, pady=(0, 8), anchor="w")

        if row["recommendations"]:
            r_frame = ctk.CTkFrame(inner, fg_color=BG_INPUT,
                                    border_color=PURPLE_DIM, border_width=1, corner_radius=8)
            r_frame.pack(fill="x")
            ctk.CTkLabel(r_frame, text="RECOMMENDATIONS", font=ctk.CTkFont(size=9, weight="bold"),
                         text_color=TEXT_DIM).pack(padx=12, pady=(8, 2), anchor="w")
            ctk.CTkLabel(r_frame, text=row["recommendations"], font=ctk.CTkFont(size=11),
                         text_color=TEXT_MAIN, wraplength=750, justify="left").pack(padx=12, pady=(0, 8), anchor="w")

    def _build_report_form(self):
        form = ctk.CTkFrame(self, fg_color=BG_CARD,
                             border_color=PURPLE_DIM, border_width=1, corner_radius=16)
        form.pack(fill="x", padx=28, pady=(0, 28))
        inner = ctk.CTkFrame(form, fg_color="transparent")
        inner.pack(fill="x", padx=28, pady=24)

        cases = get_all_cases_for_report()
        self.case_map = {f"{r['case_number']} - {r['title']}": r["case_id"] for r in cases}
        invs = get_all_investigators()
        self.inv_map = {r["full_name"]: r["investigator_id"] for r in invs}

        self._lbl(inner, "CASE *")
        self.rpt_case_var = ctk.StringVar(value=list(self.case_map.keys())[0] if self.case_map else "")
        ctk.CTkOptionMenu(inner, values=list(self.case_map.keys()), variable=self.rpt_case_var,
                          fg_color=BG_INPUT, button_color=PURPLE,
                          button_hover_color=PURPLE2, text_color=TEXT_MAIN).pack(fill="x", pady=(4, 14))

        self._lbl(inner, "REPORT TITLE *")
        self.rpt_title = self._entry(inner, "e.g. Final Investigation Report - BankAlfalah Ransomware")

        r1 = ctk.CTkFrame(inner, fg_color="transparent")
        r1.pack(fill="x", pady=(0, 14))
        auth_col = ctk.CTkFrame(r1, fg_color="transparent")
        auth_col.pack(side="left", fill="x", expand=True, padx=(0, 6))
        self._lbl(auth_col, "AUTHORED BY *")
        inv_names = list(self.inv_map.keys())
        self.rpt_auth_var = ctk.StringVar(value=inv_names[0] if inv_names else "")
        ctk.CTkOptionMenu(auth_col, values=inv_names, variable=self.rpt_auth_var,
                          fg_color=BG_INPUT, button_color=PURPLE,
                          button_hover_color=PURPLE2, text_color=TEXT_MAIN).pack(fill="x", pady=(4, 0))
        verdict_col = ctk.CTkFrame(r1, fg_color="transparent")
        verdict_col.pack(side="left", fill="x", expand=True, padx=(6, 0))
        self._lbl(verdict_col, "VERDICT *")
        self.rpt_verdict_var = ctk.StringVar(value="pending")
        ctk.CTkOptionMenu(verdict_col, values=VERDICTS, variable=self.rpt_verdict_var,
                          fg_color=BG_INPUT, button_color=PURPLE,
                          button_hover_color=PURPLE2, text_color=TEXT_MAIN).pack(fill="x", pady=(4, 0))

        self._lbl(inner, "FINDINGS *")
        self.rpt_findings = ctk.CTkTextbox(inner, height=90, fg_color=BG_INPUT,
                                            border_color=PURPLE_DIM, border_width=1,
                                            text_color=TEXT_MAIN, corner_radius=10)
        self.rpt_findings.pack(fill="x", pady=(4, 14))

        self._lbl(inner, "RECOMMENDATIONS (OPTIONAL)")
        self.rpt_recs = ctk.CTkTextbox(inner, height=70, fg_color=BG_INPUT,
                                        border_color=PURPLE_DIM, border_width=1,
                                        text_color=TEXT_MAIN, corner_radius=10)
        self.rpt_recs.pack(fill="x", pady=(4, 14))

        self.is_final_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(inner, text="Mark as Final Report", variable=self.is_final_var,
                        fg_color=PURPLE, hover_color=PURPLE2, text_color=TEXT_MAIN).pack(anchor="w", pady=(0, 12))

        self.rpt_msg = ctk.CTkLabel(inner, text="", font=ctk.CTkFont(size=12), text_color=GREEN)
        self.rpt_msg.pack()
        ctk.CTkButton(inner, text="Submit Report", height=46,
                      fg_color=PURPLE, hover_color=PURPLE2,
                      font=ctk.CTkFont(size=15, weight="bold"),
                      corner_radius=10, command=self._submit_report).pack(fill="x", pady=(8, 0))

    def _submit_report(self):
        title    = self.rpt_title.get().strip()
        findings = self.rpt_findings.get("1.0", "end").strip()
        if not title or not findings:
            self.rpt_msg.configure(text="Please fill all required (*) fields.", text_color=RED)
            return
        try:
            submit_report(
                self.case_map[self.rpt_case_var.get()],
                self.inv_map[self.rpt_auth_var.get()],
                title, findings,
                self.rpt_recs.get("1.0", "end").strip(),
                self.rpt_verdict_var.get(),
                self.is_final_var.get()
            )
            self.rpt_msg.configure(text="Report submitted successfully.", text_color=GREEN)
            self.rpt_title.delete(0, "end")
            self.rpt_findings.delete("1.0", "end")
            self.rpt_recs.delete("1.0", "end")
        except Exception as e:
            self.rpt_msg.configure(text=f"Error: {e}", text_color=RED)

    def _build_users(self):
        if self.session["role"] != "admin":
            ctk.CTkLabel(self, text="Access Denied - Admin only",
                         font=ctk.CTkFont(size=16), text_color=RED).pack(pady=40)
            return

        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.pack(fill="x", padx=28, pady=(22, 0))
        ctk.CTkLabel(hdr, text="User Management",
                     font=ctk.CTkFont(size=22, weight="bold"), text_color="#ffffff").pack(anchor="w")
        ctk.CTkFrame(self, fg_color=SEP_COLOR, height=1).pack(fill="x", padx=28, pady=14)

        for row in get_all_users():
            card = ctk.CTkFrame(self, fg_color=BG_CARD,
                                 border_color=PURPLE_DIM, border_width=1, corner_radius=12)
            card.pack(fill="x", padx=28, pady=4)
            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(fill="x", padx=18, pady=12)

            top = ctk.CTkFrame(inner, fg_color="transparent")
            top.pack(fill="x")
            ctk.CTkLabel(top, text=row["username"],
                         font=ctk.CTkFont(size=14, weight="bold"), text_color="#ffffff").pack(side="left")
            role_clr = {"admin": RED, "investigator": PURPLE, "analyst": BLUE}.get(row["role"], TEXT_MAIN)
            ctk.CTkLabel(top, text=f"  {row['role'].upper()}  ",
                         font=ctk.CTkFont(size=9, weight="bold"),
                         fg_color=TEXT_GHOST, text_color=role_clr, corner_radius=8).pack(side="left", padx=8)
            ctk.CTkLabel(top, text="ACTIVE" if row["is_active"] else "INACTIVE",
                         font=ctk.CTkFont(size=9),
                         text_color=GREEN if row["is_active"] else RED).pack(side="right")

            ctk.CTkLabel(inner,
                         text=f"Name: {row['full_name']}  |  Badge: {row['badge_number']}  |  Dept: {row['department']}",
                         font=ctk.CTkFont(size=10), text_color=TEXT_FAINT).pack(anchor="w", pady=(4, 0))
            if row["last_login"]:
                ctk.CTkLabel(inner, text=f"Last login: {row['last_login']}",
                             font=ctk.CTkFont(size=10), text_color=TEXT_FAINT).pack(anchor="w")

            if row["username"] != self.session["username"]:
                uid   = row["user_id"]
                uname = row["username"]
                def _del(u_id=uid, u_name=uname):
                    self._confirm_delete_user(u_id, u_name)
                ctk.CTkButton(inner, text="Delete User", width=120, height=30,
                              fg_color=RED_DARK, hover_color=RED, text_color="#ffffff",
                              font=ctk.CTkFont(size=11, weight="bold"),
                              corner_radius=8, command=_del).pack(anchor="w", pady=(8, 0))

        ctk.CTkFrame(self, fg_color=SEP_COLOR, height=1).pack(fill="x", padx=28, pady=14)
        ctk.CTkLabel(self, text="Create New User",
                     font=ctk.CTkFont(size=16, weight="bold"),
                     text_color=TEXT_MAIN).pack(padx=28, anchor="w", pady=(0, 10))
        self._build_create_user()

    def _confirm_delete_user(self, user_id, username):
        """Show confirmation popup before deleting a user."""
        popup = ctk.CTkToplevel()
        popup.title("Confirm Delete")
        popup.geometry("360x180")
        popup.resizable(False, False)
        popup.configure(fg_color=BG_DARK)
        popup.grab_set()
        popup.update_idletasks()
        x = (popup.winfo_screenwidth()  - 360) // 2
        y = (popup.winfo_screenheight() - 180) // 2
        popup.geometry(f"360x180+{x}+{y}")

        ctk.CTkLabel(popup, text="Delete User?",
                     font=ctk.CTkFont(size=16, weight="bold"), text_color="#ffffff").pack(pady=(24, 6))
        ctk.CTkLabel(popup, text=f"This will permanently delete '{username}'.",
                     font=ctk.CTkFont(size=12), text_color=TEXT_DIM).pack()

        btn_row = ctk.CTkFrame(popup, fg_color="transparent")
        btn_row.pack(pady=20)

        def _do():
            success, err = delete_user(user_id)
            if not success:
                popup.destroy()
                # Show error popup
                err_popup = ctk.CTkToplevel()
                err_popup.title("Cannot Delete")
                err_popup.geometry("360x150")
                err_popup.resizable(False, False)
                err_popup.configure(fg_color=BG_DARK)
                err_popup.grab_set()
                err_popup.update_idletasks()
                x = (err_popup.winfo_screenwidth()  - 360) // 2
                y = (err_popup.winfo_screenheight() - 150) // 2
                err_popup.geometry(f"360x150+{x}+{y}")
                ctk.CTkLabel(err_popup, text="Cannot Delete User",
                             font=ctk.CTkFont(size=14, weight="bold"),
                             text_color=RED).pack(pady=(24, 8))
                ctk.CTkLabel(err_popup, text=err,
                             font=ctk.CTkFont(size=11),
                             text_color=TEXT_DIM, wraplength=300).pack()
                ctk.CTkButton(err_popup, text="OK", width=100, height=34,
                              fg_color=PURPLE_DIM, hover_color=PURPLE,
                              text_color=TEXT_MAIN, corner_radius=8,
                              command=err_popup.destroy).pack(pady=16)
                return
            popup.destroy()
            for w in self.winfo_children():
                w.destroy()
            self._build_users()

        ctk.CTkButton(btn_row, text="Delete", width=120, height=36,
                      fg_color=RED_DARK, hover_color=RED, text_color="#ffffff",
                      font=ctk.CTkFont(size=13, weight="bold"),
                      corner_radius=8, command=_do).pack(side="left", padx=8)
        ctk.CTkButton(btn_row, text="Cancel", width=120, height=36,
                      fg_color=BG_CARD, hover_color=PURPLE_DIM, text_color=TEXT_MAIN,
                      font=ctk.CTkFont(size=13), corner_radius=8,
                      command=popup.destroy).pack(side="left", padx=8)

    def _build_create_user(self):
        auto_badge = gen_badge_number()
        form = ctk.CTkFrame(self, fg_color=BG_CARD,
                             border_color=PURPLE_DIM, border_width=1, corner_radius=16)
        form.pack(fill="x", padx=28, pady=(0, 28))
        inner = ctk.CTkFrame(form, fg_color="transparent")
        inner.pack(fill="x", padx=28, pady=24)

        self._lbl(inner, "BADGE NUMBER (AUTO)")
        ctk.CTkEntry(inner, textvariable=ctk.StringVar(value=auto_badge), state="disabled",
                     fg_color=BG_INPUT, text_color="#a5b4fc", border_color=PURPLE_DIM,
                     height=40, corner_radius=10).pack(fill="x", pady=(4, 14))

        r1 = ctk.CTkFrame(inner, fg_color="transparent")
        r1.pack(fill="x", pady=(0, 14))
        u_col = ctk.CTkFrame(r1, fg_color="transparent")
        u_col.pack(side="left", fill="x", expand=True, padx=(0, 6))
        self._lbl(u_col, "USERNAME *")
        self.new_username = ctk.CTkEntry(u_col, placeholder_text="e.g. ali_hassan",
                                          fg_color=BG_INPUT, border_color=PURPLE_DIM,
                                          text_color=TEXT_MAIN, placeholder_text_color=TEXT_FAINT,
                                          height=40, corner_radius=10)
        self.new_username.pack(fill="x", pady=(4, 0))
        p_col = ctk.CTkFrame(r1, fg_color="transparent")
        p_col.pack(side="left", fill="x", expand=True, padx=(6, 0))
        self._lbl(p_col, "PASSWORD *")
        self.new_password = ctk.CTkEntry(p_col, placeholder_text="Min 6 characters", show="*",
                                          fg_color=BG_INPUT, border_color=PURPLE_DIM,
                                          text_color=TEXT_MAIN, placeholder_text_color=TEXT_FAINT,
                                          height=40, corner_radius=10)
        self.new_password.pack(fill="x", pady=(4, 0))

        r2 = ctk.CTkFrame(inner, fg_color="transparent")
        r2.pack(fill="x", pady=(14, 14))
        role_col = ctk.CTkFrame(r2, fg_color="transparent")
        role_col.pack(side="left", fill="x", expand=True, padx=(0, 6))
        self._lbl(role_col, "ROLE *")
        self.new_role_var = ctk.StringVar(value="investigator")
        ctk.CTkOptionMenu(role_col, values=ROLES, variable=self.new_role_var,
                          fg_color=BG_INPUT, button_color=PURPLE,
                          button_hover_color=PURPLE2, text_color=TEXT_MAIN).pack(fill="x", pady=(4, 0))
        name_col = ctk.CTkFrame(r2, fg_color="transparent")
        name_col.pack(side="left", fill="x", expand=True, padx=(6, 0))
        self._lbl(name_col, "FULL NAME *")
        self.new_fullname = ctk.CTkEntry(name_col, placeholder_text="e.g. Ali Hassan Khan",
                                          fg_color=BG_INPUT, border_color=PURPLE_DIM,
                                          text_color=TEXT_MAIN, placeholder_text_color=TEXT_FAINT,
                                          height=40, corner_radius=10)
        self.new_fullname.pack(fill="x", pady=(4, 0))

        self._lbl(inner, "CONTACT EMAIL *")
        self.new_email = self._entry(inner, "e.g. ali.hassan@fia.gov.pk")

        self.user_msg = ctk.CTkLabel(inner, text="", font=ctk.CTkFont(size=12), text_color=GREEN)
        self.user_msg.pack()
        ctk.CTkButton(inner, text="Create User", height=46,
                      fg_color=PURPLE, hover_color=PURPLE2,
                      font=ctk.CTkFont(size=15, weight="bold"), corner_radius=10,
                      command=lambda b=auto_badge: self._create_user(b)).pack(fill="x", pady=(8, 0))

    def _create_user(self, badge):
        uname = self.new_username.get().strip()
        pw    = self.new_password.get().strip()
        fname = self.new_fullname.get().strip()
        email = self.new_email.get().strip()
        if not all([uname, pw, fname, email]):
            self.user_msg.configure(text="Please fill all required (*) fields.", text_color=RED)
            return
        try:
            create_user(uname, pw, self.new_role_var.get(), fname, badge, email)
            self.user_msg.configure(text=f"User '{uname}' created with badge {badge}.", text_color=GREEN)
            self.new_username.delete(0, "end")
            self.new_password.delete(0, "end")
            self.new_fullname.delete(0, "end")
            self.new_email.delete(0, "end")
        except Exception as e:
            self.user_msg.configure(text=f"Error: {e}", text_color=RED)

    def _build_logs(self):
        if self.session["role"] != "admin":
            ctk.CTkLabel(self, text="Access Denied - Admin only",
                         font=ctk.CTkFont(size=16), text_color=RED).pack(pady=40)
            return

        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.pack(fill="x", padx=28, pady=(22, 0))
        ctk.CTkLabel(hdr, text="Security Audit - Access Logs",
                     font=ctk.CTkFont(size=22, weight="bold"), text_color="#ffffff").pack(anchor="w")
        ctk.CTkFrame(self, fg_color=SEP_COLOR, height=1).pack(fill="x", padx=28, pady=14)

        rows = get_access_logs()
        failed = [r for r in rows if not r["success"]]
        if failed:
            alert = ctk.CTkFrame(self, fg_color=RED_DARK, border_color=RED, border_width=1, corner_radius=10)
            alert.pack(fill="x", padx=28, pady=(0, 10))
            ctk.CTkLabel(alert, text=f"{len(failed)} failed access attempt(s) detected",
                         font=ctk.CTkFont(size=13, weight="bold"), text_color="#ffffff").pack(padx=16, pady=10)

        ctk.CTkLabel(self, text="Full Audit Log",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=TEXT_MAIN).pack(padx=28, anchor="w", pady=(0, 8))

        for row in rows:
            success = bool(row["success"])
            clr = GREEN if success else RED
            card = ctk.CTkFrame(self, fg_color=BG_CARD,
                                 border_color=PURPLE_DIM, border_width=1, corner_radius=10)
            card.pack(fill="x", padx=28, pady=3)
            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(fill="x", padx=16, pady=10)

            top = ctk.CTkFrame(inner, fg_color="transparent")
            top.pack(fill="x")
            ctk.CTkLabel(top, text=row["action"],
                         font=ctk.CTkFont(size=12, weight="bold"), text_color="#ffffff").pack(side="left")
            ctk.CTkLabel(top, text=f"  {'SUCCESS' if success else 'FAILED'}  ",
                         font=ctk.CTkFont(size=9, weight="bold"),
                         fg_color=TEXT_GHOST, text_color=clr, corner_radius=8).pack(side="left", padx=8)
            ctk.CTkLabel(top, text=str(row["action_time"]),
                         font=ctk.CTkFont(size=9), text_color=TEXT_FAINT).pack(side="right")

            ctk.CTkLabel(inner,
                         text=f"User: {row['username']} ({row['role']})  |  IP: {row['ip_address']}  |  Resource: {row['resource_accessed']}",
                         font=ctk.CTkFont(size=10), text_color=TEXT_FAINT).pack(anchor="w", pady=(2, 0))
            if row["failure_reason"]:
                ctk.CTkLabel(inner, text=f"Reason: {row['failure_reason']}",
                             font=ctk.CTkFont(size=10), text_color=ORANGE).pack(anchor="w")

        ctk.CTkFrame(self, fg_color="transparent", height=28).pack()

    def _lbl(self, parent, text):
        ctk.CTkLabel(parent, text=text, font=ctk.CTkFont(size=10, weight="bold"),
                     text_color=TEXT_DIM).pack(anchor="w")

    def _entry(self, parent, placeholder, pady=(4, 14)):
        e = ctk.CTkEntry(parent, placeholder_text=placeholder,
                         fg_color=BG_INPUT, border_color=PURPLE_DIM,
                         text_color=TEXT_MAIN, placeholder_text_color=TEXT_FAINT,
                         height=40, corner_radius=10)
        e.pack(fill="x", pady=pady)
        return e