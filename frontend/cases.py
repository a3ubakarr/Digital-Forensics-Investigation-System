import customtkinter as ctk
from backend.case_service import (
    get_all_cases, gen_case_number, create_case,
    update_case_status, get_investigators
)

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
ORANGE    = "#fb923c"

STATUSES = ["open", "under_investigation", "pending_review", "closed", "archived"]
PRIORITIES = ["critical", "high", "medium", "low"]
CASE_TYPES = ["ransomware", "phishing", "data_breach", "insider_threat",
              "fraud", "ddos", "identity_theft", "malware", "other"]
JURISDICTIONS = [
    "Punjab, Pakistan", "Sindh, Pakistan", "KPK, Pakistan",
    "Balochistan, Pakistan", "Federal / Islamabad",
    "Azad Kashmir", "Gilgit-Baltistan", "International"
]


class CasesFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, session, mode="list", **kwargs):
        super().__init__(master, **kwargs)
        self.session = session
        self.mode    = mode
        self.configure(scrollbar_button_color=BG_DARK)
        self._build()

    def _build(self):
        if self.mode == "list":
            self._build_list()
        else:
            self._build_new()

    def _build_list(self):
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.pack(fill="x", padx=28, pady=(22, 0))
        ctk.CTkLabel(hdr, text="Case Management",
                     font=ctk.CTkFont(size=22, weight="bold"), text_color="#ffffff").pack(anchor="w")
        ctk.CTkLabel(hdr, text="Filter, view and manage all investigation cases",
                     font=ctk.CTkFont(size=12), text_color=TEXT_DIM).pack(anchor="w")
        ctk.CTkFrame(self, fg_color=SEP_COLOR, height=1).pack(fill="x", padx=28, pady=14)

        filter_row = ctk.CTkFrame(self, fg_color="transparent")
        filter_row.pack(fill="x", padx=28, pady=(0, 12))

        status_col = ctk.CTkFrame(filter_row, fg_color="transparent")
        status_col.pack(side="left", fill="x", expand=True, padx=(0, 6))
        ctk.CTkLabel(status_col, text="FILTER BY STATUS",
                     font=ctk.CTkFont(size=10, weight="bold"), text_color=TEXT_DIM).pack(anchor="w")
        self.status_var = ctk.StringVar(value="All")
        ctk.CTkOptionMenu(status_col, values=["All"] + STATUSES, variable=self.status_var,
                          fg_color=BG_CARD, button_color=PURPLE, button_hover_color=PURPLE2,
                          text_color=TEXT_MAIN, command=lambda _: self._reload_list()
                          ).pack(fill="x", pady=(4, 0))

        priority_col = ctk.CTkFrame(filter_row, fg_color="transparent")
        priority_col.pack(side="left", fill="x", expand=True, padx=(6, 0))
        ctk.CTkLabel(priority_col, text="FILTER BY PRIORITY",
                     font=ctk.CTkFont(size=10, weight="bold"), text_color=TEXT_DIM).pack(anchor="w")
        self.priority_var = ctk.StringVar(value="All")
        ctk.CTkOptionMenu(priority_col, values=["All"] + PRIORITIES, variable=self.priority_var,
                          fg_color=BG_CARD, button_color=PURPLE, button_hover_color=PURPLE2,
                          text_color=TEXT_MAIN, command=lambda _: self._reload_list()
                          ).pack(fill="x", pady=(4, 0))

        self.list_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.list_frame.pack(fill="x", padx=28, pady=(8, 28))
        self._reload_list()

    def _reload_list(self):
        for w in self.list_frame.winfo_children():
            w.destroy()
        rows = get_all_cases(self.status_var.get(), self.priority_var.get())
        if not rows:
            ctk.CTkLabel(self.list_frame, text="No cases found.", text_color=TEXT_DIM).pack(pady=30)
            return
        for row in rows:
            self._case_card(self.list_frame, row)

    def _case_card(self, parent, row):
        pri_colors = {"critical": RED, "high": ORANGE, "medium": "#facc15", "low": GREEN}
        clr = pri_colors.get(row["priority"], TEXT_MAIN)

        card = ctk.CTkFrame(parent, fg_color=BG_CARD,
                             border_color=PURPLE_DIM, border_width=1, corner_radius=12)
        card.pack(fill="x", pady=5)
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=18, pady=14)

        top = ctk.CTkFrame(inner, fg_color="transparent")
        top.pack(fill="x")
        ctk.CTkLabel(top, text=row["case_number"],
                     font=ctk.CTkFont(size=14, weight="bold"), text_color="#ffffff").pack(side="left")
        ctk.CTkLabel(top, text=f"  {row['priority'].upper()}  ",
                     font=ctk.CTkFont(size=9, weight="bold"),
                     fg_color=TEXT_GHOST, text_color=clr, corner_radius=10).pack(side="left", padx=8)
        ctk.CTkLabel(top, text=row["case_type"],
                     font=ctk.CTkFont(size=10), text_color=TEXT_FAINT).pack(side="left")

        ctk.CTkLabel(inner, text=row["title"], font=ctk.CTkFont(size=13),
                     text_color=TEXT_DIM, wraplength=700, justify="left").pack(anchor="w", pady=(4, 2))
        meta = (f"Org: {row['affected_org']}  |  Jurisdiction: {row['jurisdiction']}  |  "
                f"Lead: {row['lead_investigator']}  |  Evidence: {row['evidence_count']}")
        ctk.CTkLabel(inner, text=meta, font=ctk.CTkFont(size=10), text_color=TEXT_FAINT).pack(anchor="w")

        if self.session["role"] in ("admin", "investigator"):
            bot = ctk.CTkFrame(inner, fg_color="transparent")
            bot.pack(fill="x", pady=(10, 0))
            status_var = ctk.StringVar(value=row["status"])
            ctk.CTkOptionMenu(bot, values=STATUSES, variable=status_var, width=200,
                              fg_color=BG_INPUT, button_color=PURPLE,
                              button_hover_color=PURPLE2, text_color=TEXT_MAIN).pack(side="left")
            case_id = row["case_id"]
            def _update(cid=case_id, sv=status_var):
                update_case_status(cid, sv.get())
                self._reload_list()
            ctk.CTkButton(bot, text="Update", width=90, height=32,
                          fg_color=PURPLE, hover_color=PURPLE2,
                          font=ctk.CTkFont(size=12), command=_update).pack(side="left", padx=8)

    def _build_new(self):
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.pack(fill="x", padx=28, pady=(22, 0))
        ctk.CTkLabel(hdr, text="Register New Case",
                     font=ctk.CTkFont(size=22, weight="bold"), text_color="#ffffff").pack(anchor="w")
        ctk.CTkLabel(hdr, text="All fields marked * are required",
                     font=ctk.CTkFont(size=12), text_color=TEXT_DIM).pack(anchor="w")
        ctk.CTkFrame(self, fg_color=SEP_COLOR, height=1).pack(fill="x", padx=28, pady=14)

        form = ctk.CTkFrame(self, fg_color=BG_CARD,
                             border_color=PURPLE_DIM, border_width=1, corner_radius=16)
        form.pack(fill="x", padx=28, pady=(0, 28))
        inner = ctk.CTkFrame(form, fg_color="transparent")
        inner.pack(fill="x", padx=28, pady=24)

        auto_cn = gen_case_number()
        self._lbl(inner, "CASE NUMBER")
        ctk.CTkEntry(inner, textvariable=ctk.StringVar(value=auto_cn), state="disabled",
                     fg_color=BG_INPUT, text_color="#a5b4fc", border_color=PURPLE_DIM,
                     height=40, corner_radius=10).pack(fill="x", pady=(4, 14))

        self._lbl(inner, "CASE TITLE *")
        self.title_entry = self._entry(inner, "e.g. HBL Ransomware Attack 2026")

        r1 = ctk.CTkFrame(inner, fg_color="transparent")
        r1.pack(fill="x", pady=(0, 14))
        type_col = ctk.CTkFrame(r1, fg_color="transparent")
        type_col.pack(side="left", fill="x", expand=True, padx=(0, 6))
        self._lbl(type_col, "CASE TYPE *")
        self.type_var = ctk.StringVar(value=CASE_TYPES[0])
        ctk.CTkOptionMenu(type_col, values=CASE_TYPES, variable=self.type_var,
                          fg_color=BG_INPUT, button_color=PURPLE,
                          button_hover_color=PURPLE2, text_color=TEXT_MAIN).pack(fill="x", pady=(4, 0))
        pri_col = ctk.CTkFrame(r1, fg_color="transparent")
        pri_col.pack(side="left", fill="x", expand=True, padx=(6, 0))
        self._lbl(pri_col, "PRIORITY *")
        self.priority_var2 = ctk.StringVar(value="medium")
        ctk.CTkOptionMenu(pri_col, values=PRIORITIES, variable=self.priority_var2,
                          fg_color=BG_INPUT, button_color=PURPLE,
                          button_hover_color=PURPLE2, text_color=TEXT_MAIN).pack(fill="x", pady=(4, 0))

        invs = get_investigators()
        self.inv_map = {r["full_name"]: r["investigator_id"] for r in invs}
        inv_names = list(self.inv_map.keys())

        r2 = ctk.CTkFrame(inner, fg_color="transparent")
        r2.pack(fill="x", pady=(0, 14))
        inv_col = ctk.CTkFrame(r2, fg_color="transparent")
        inv_col.pack(side="left", fill="x", expand=True, padx=(0, 6))
        self._lbl(inv_col, "LEAD INVESTIGATOR *")
        self.inv_var = ctk.StringVar(value=inv_names[0] if inv_names else "")
        ctk.CTkOptionMenu(inv_col, values=inv_names, variable=self.inv_var,
                          fg_color=BG_INPUT, button_color=PURPLE,
                          button_hover_color=PURPLE2, text_color=TEXT_MAIN).pack(fill="x", pady=(4, 0))
        jur_col = ctk.CTkFrame(r2, fg_color="transparent")
        jur_col.pack(side="left", fill="x", expand=True, padx=(6, 0))
        self._lbl(jur_col, "JURISDICTION *")
        self.jur_var = ctk.StringVar(value=JURISDICTIONS[0])
        ctk.CTkOptionMenu(jur_col, values=JURISDICTIONS, variable=self.jur_var,
                          fg_color=BG_INPUT, button_color=PURPLE,
                          button_hover_color=PURPLE2, text_color=TEXT_MAIN).pack(fill="x", pady=(4, 0))

        self._lbl(inner, "AFFECTED ORGANIZATION *")
        self.org_entry = self._entry(inner, "e.g. HBL Karachi, NADRA Islamabad")

        self.msg_label = ctk.CTkLabel(inner, text="", font=ctk.CTkFont(size=12), text_color=GREEN)
        self.msg_label.pack(pady=(4, 0))

        ctk.CTkButton(inner, text="Register Case", height=46,
                      fg_color=PURPLE, hover_color=PURPLE2,
                      font=ctk.CTkFont(size=15, weight="bold"), corner_radius=10,
                      command=lambda cn=auto_cn: self._submit(cn)).pack(fill="x", pady=(12, 0))

    def _submit(self, case_number):
        title = self.title_entry.get().strip()
        org   = self.org_entry.get().strip()
        if not title or not org:
            self.msg_label.configure(text="Please fill all required (*) fields.", text_color=RED)
            return
        try:
            create_case(case_number, title, self.type_var.get(), self.priority_var2.get(),
                        self.inv_map[self.inv_var.get()], org, self.jur_var.get())
            self.msg_label.configure(text=f"Case {case_number} registered successfully.", text_color=GREEN)
            self.title_entry.delete(0, "end")
            self.org_entry.delete(0, "end")
        except Exception as e:
            self.msg_label.configure(text=f"Error: {e}", text_color=RED)

    def _lbl(self, parent, text):
        ctk.CTkLabel(parent, text=text, font=ctk.CTkFont(size=10, weight="bold"),
                     text_color=TEXT_DIM).pack(anchor="w")

    def _entry(self, parent, placeholder):
        e = ctk.CTkEntry(parent, placeholder_text=placeholder,
                         fg_color=BG_INPUT, border_color=PURPLE_DIM,
                         text_color=TEXT_MAIN, placeholder_text_color=TEXT_FAINT,
                         height=40, corner_radius=10)
        e.pack(fill="x", pady=(4, 14))
        return e