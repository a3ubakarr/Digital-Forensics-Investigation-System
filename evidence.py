"""
DFIS - Digital Forensics Investigation System
File        : evidence.py
Description : Evidence Repository - list view + new evidence form
Developer   : Member 3
"""

import customtkinter as ctk
import hashlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
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

plt.rcParams.update({
    "figure.facecolor": BG_CARD, "axes.facecolor": BG_CARD,
    "axes.edgecolor": SEP_COLOR, "axes.labelcolor": TEXT_DIM,
    "xtick.color": TEXT_DIM, "ytick.color": TEXT_DIM,
    "text.color": TEXT_DIM, "grid.color": "#111827",
    "font.family": "Segoe UI",
})

EV_TYPES = ["usb_drive", "hard_disk", "email", "log_file", "ip_trace",
            "screenshot", "network_capture", "mobile_device",
            "document", "memory_dump", "other"]
EV_STATUSES  = ["collected", "in_analysis", "verified", "compromised", "released"]
STORAGE_LOCS = ["FIA Lab - Cabinet A", "FIA Lab - Cabinet B", "FIA Lab - Cabinet C",
                "NAS Server /evidence/", "Email Forensics Server",
                "Cloud Storage - Encrypted", "Physical Evidence Locker"]
COLLECT_LOCS = ["Server Room", "NOC Room", "Suspect Workstation", "Office Premises",
                "Crime Scene", "Remote / Network", "Email System",
                "Cloud Infrastructure", "Other"]


def _gen_evidence_number(case_number):
    rows = run_query(
        "SELECT COUNT(*) FROM evidence e "
        "JOIN cases c ON e.case_id=c.case_id WHERE c.case_number=?",
        (case_number,)
    )
    n = (rows[0][0] if rows else 0) + 1
    return f"EV-{case_number}-{str(n).zfill(3)}"


def _gen_sha256(ev_num, case_num):
    return hashlib.sha256(
        f"{ev_num}-{case_num}-{datetime.now().isoformat()}".encode()
    ).hexdigest()


class EvidenceFrame(ctk.CTkScrollableFrame):
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

    # --------------------------------------------------
    #  EVIDENCE LIST
    # --------------------------------------------------
    def _build_list(self):
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.pack(fill="x", padx=28, pady=(22, 0))
        ctk.CTkLabel(hdr, text="Evidence Repository",
                     font=ctk.CTkFont(size=22, weight="bold"),
                     text_color="#ffffff").pack(anchor="w")
        ctk.CTkLabel(hdr, text="All collected digital evidence items",
                     font=ctk.CTkFont(size=12), text_color=TEXT_DIM).pack(anchor="w")

        ctk.CTkFrame(self, fg_color=SEP_COLOR, height=1).pack(
            fill="x", padx=28, pady=14)

        rows = run_query(
            """SELECT e.evidence_number, c.case_number, e.evidence_type,
                      e.status, e.collected_at, i.full_name AS collected_by,
                      e.source_ip, e.description
               FROM evidence e
               JOIN cases c ON e.case_id = c.case_id
               JOIN investigators i ON e.collected_by = i.investigator_id
               ORDER BY e.collected_at DESC"""
        )

        for row in rows:
            s_colors = {"collected": BLUE, "in_analysis": ORANGE,
                        "verified": GREEN, "compromised": RED, "released": TEXT_DIM}
            clr = s_colors.get(row["status"], TEXT_MAIN)

            card = ctk.CTkFrame(self, fg_color=BG_CARD,
                                 border_color=PURPLE_DIM, border_width=1,
                                 corner_radius=12)
            card.pack(fill="x", padx=28, pady=4)
            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(fill="x", padx=18, pady=12)

            top = ctk.CTkFrame(inner, fg_color="transparent")
            top.pack(fill="x")
            ctk.CTkLabel(top, text=row["evidence_number"],
                         font=ctk.CTkFont(size=13, weight="bold"),
                         text_color="#ffffff").pack(side="left")
            ctk.CTkLabel(top, text=f"  {row['status'].upper()}  ",
                         font=ctk.CTkFont(size=9, weight="bold"),
                         fg_color=TEXT_GHOST, text_color=clr,
                         corner_radius=10).pack(side="left", padx=8)
            ctk.CTkLabel(top, text=row["evidence_type"],
                         font=ctk.CTkFont(size=10),
                         text_color=TEXT_FAINT).pack(side="left")

            meta = (f"Case: {row['case_number']}  |  "
                    f"By: {row['collected_by']}  |  {row['collected_at']}")
            if row["source_ip"]:
                meta += f"  |  IP: {row['source_ip']}"
            ctk.CTkLabel(inner, text=meta,
                         font=ctk.CTkFont(size=10),
                         text_color=TEXT_FAINT).pack(anchor="w", pady=(4, 2))
            ctk.CTkLabel(inner, text=row["description"],
                         font=ctk.CTkFont(size=11), text_color=TEXT_DIM,
                         wraplength=700, justify="left").pack(anchor="w")

        # Delete Evidence Section
        ctk.CTkFrame(self, fg_color=SEP_COLOR, height=1).pack(
            fill="x", padx=28, pady=14)

        del_card = ctk.CTkFrame(self, fg_color=BG_CARD,
                                 border_color=RED_DARK, border_width=1,
                                 corner_radius=14)
        del_card.pack(fill="x", padx=28, pady=(0, 6))

        del_inner = ctk.CTkFrame(del_card, fg_color="transparent")
        del_inner.pack(fill="x", padx=20, pady=18)

        ctk.CTkLabel(del_inner, text="Delete Evidence",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=RED).pack(anchor="w")
        ctk.CTkLabel(del_inner,
                     text="Select evidence item to permanently delete",
                     font=ctk.CTkFont(size=11), text_color=TEXT_DIM).pack(
                         anchor="w", pady=(2, 12))

        ev_rows = run_query(
            "SELECT e.evidence_number, c.case_number "
            "FROM evidence e JOIN cases c ON e.case_id=c.case_id "
            "ORDER BY e.evidence_number"
        )
        ev_options = [
            f"{r['evidence_number']}  ({r['case_number']})" for r in ev_rows
        ]
        ev_map = {
            f"{r['evidence_number']}  ({r['case_number']})": r["evidence_number"]
            for r in ev_rows
        }

        if ev_options:
            self.del_ev_var = ctk.StringVar(value=ev_options[0])
            ctk.CTkOptionMenu(del_inner, values=ev_options,
                              variable=self.del_ev_var,
                              fg_color=BG_INPUT, button_color=RED_DARK,
                              button_hover_color=RED, text_color=TEXT_MAIN,
                              width=400).pack(anchor="w", pady=(0, 12))

            self.del_ev_msg = ctk.CTkLabel(del_inner, text="",
                                            font=ctk.CTkFont(size=11),
                                            text_color=RED)
            self.del_ev_msg.pack(anchor="w")

            def _confirm_ev_delete():
                sel = self.del_ev_var.get()
                ev_num = ev_map.get(sel, "")
                if not ev_num:
                    return
                self._confirm_delete_evidence(ev_num, ev_map)

            ctk.CTkButton(del_inner, text="Delete Selected Evidence",
                          height=38, width=220,
                          fg_color=RED_DARK, hover_color=RED,
                          text_color="#ffffff",
                          font=ctk.CTkFont(size=12, weight="bold"),
                          corner_radius=8,
                          command=_confirm_ev_delete).pack(anchor="w")
        else:
            ctk.CTkLabel(del_inner, text="No evidence items found.",
                         font=ctk.CTkFont(size=12),
                         text_color=TEXT_DIM).pack(anchor="w")

        # Chart
        ctk.CTkFrame(self, fg_color=SEP_COLOR, height=1).pack(
            fill="x", padx=28, pady=14)
        ctk.CTkLabel(self, text="Evidence by Type",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=TEXT_MAIN).pack(padx=28, anchor="w")

        chart_card = ctk.CTkFrame(self, fg_color=BG_CARD,
                                   border_color=PURPLE_DIM, border_width=1,
                                   corner_radius=14)
        chart_card.pack(fill="x", padx=28, pady=(8, 28))

        type_data = run_query(
            "SELECT evidence_type, COUNT(*) AS total FROM evidence "
            "GROUP BY evidence_type ORDER BY total DESC"
        )
        if type_data:
            labels = [r["evidence_type"] for r in type_data]
            values = [r["total"]         for r in type_data]
            colors = [PURPLE, PURPLE2, "#a855f7", BLUE, GREEN,
                      ORANGE, RED, "#facc15", TEXT_MAIN, TEXT_DIM, "#c084fc"]

            fig, ax = plt.subplots(figsize=(9, 2.6))
            bars = ax.bar(labels, values, color=colors[:len(labels)],
                          width=0.5, zorder=3)
            ax.set_ylabel("Count", fontsize=9)
            ax.grid(axis="y", zorder=0)
            ax.tick_params(axis="x", labelsize=8, rotation=20)
            ax.tick_params(axis="y", labelsize=8)
            for bar, v in zip(bars, values):
                ax.text(bar.get_x() + bar.get_width()/2,
                        bar.get_height() + 0.03,
                        str(v), ha="center", va="bottom",
                        fontsize=8, color=TEXT_MAIN)
            fig.tight_layout()
            canvas = FigureCanvasTkAgg(fig, master=chart_card)
            canvas.draw()
            canvas.get_tk_widget().pack(padx=14, pady=14, fill="both")
            plt.close(fig)

    # --------------------------------------------------
    #  NEW EVIDENCE FORM
    # --------------------------------------------------
    def _build_new(self):
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.pack(fill="x", padx=28, pady=(22, 0))
        ctk.CTkLabel(hdr, text="Submit New Evidence",
                     font=ctk.CTkFont(size=22, weight="bold"),
                     text_color="#ffffff").pack(anchor="w")
        ctk.CTkLabel(hdr, text="All fields marked * are required",
                     font=ctk.CTkFont(size=12), text_color=TEXT_DIM).pack(anchor="w")

        ctk.CTkFrame(self, fg_color=SEP_COLOR, height=1).pack(
            fill="x", padx=28, pady=14)

        # Case selector
        cases = run_query(
            "SELECT case_id, case_number, title FROM cases WHERE status != 'closed'"
        )
        self.case_map = {
            f"{r['case_number']} - {r['title']}": (r["case_id"], r["case_number"])
            for r in cases
        }
        case_keys = list(self.case_map.keys())

        self._lbl_outer("SELECT CASE *")
        self.case_var = ctk.StringVar(value=case_keys[0] if case_keys else "")
        ctk.CTkOptionMenu(self, values=case_keys, variable=self.case_var,
                          fg_color=BG_CARD, button_color=PURPLE,
                          button_hover_color=PURPLE2, text_color=TEXT_MAIN,
                          command=self._refresh_auto
                          ).pack(fill="x", padx=28, pady=(4, 14))

        # Auto fields
        sel_key = self.case_var.get()
        case_no = self.case_map[sel_key][1] if sel_key in self.case_map else "N/A"
        auto_ev   = _gen_evidence_number(case_no)
        auto_hash = _gen_sha256(auto_ev, case_no)

        form = ctk.CTkFrame(self, fg_color=BG_CARD,
                             border_color=PURPLE_DIM, border_width=1,
                             corner_radius=16)
        form.pack(fill="x", padx=28, pady=(0, 28))
        inner = ctk.CTkFrame(form, fg_color="transparent")
        inner.pack(fill="x", padx=28, pady=24)

        # Evidence Number
        self._lbl(inner, "EVIDENCE NUMBER (AUTO)")
        self.ev_num_var = ctk.StringVar(value=auto_ev)
        ctk.CTkEntry(inner, textvariable=self.ev_num_var, state="disabled",
                     fg_color=BG_INPUT, text_color="#a5b4fc",
                     border_color=PURPLE_DIM, height=40, corner_radius=10
                     ).pack(fill="x", pady=(4, 14))

        # SHA-256
        self._lbl(inner, "SHA-256 HASH (AUTO)")
        self.hash_var = ctk.StringVar(value=auto_hash)
        ctk.CTkEntry(inner, textvariable=self.hash_var, state="disabled",
                     fg_color=BG_INPUT, text_color="#a5b4fc",
                     border_color=PURPLE_DIM, height=40, corner_radius=10
                     ).pack(fill="x", pady=(4, 14))

        # Row 1: type + collected by (pack side by side)
        invs = run_query("SELECT investigator_id, full_name FROM investigators")
        self.inv_map = {r["full_name"]: r["investigator_id"] for r in invs}
        inv_names = list(self.inv_map.keys())

        r1 = ctk.CTkFrame(inner, fg_color="transparent")
        r1.pack(fill="x", pady=(0, 14))

        type_col = ctk.CTkFrame(r1, fg_color="transparent")
        type_col.pack(side="left", fill="x", expand=True, padx=(0, 6))
        self._lbl(type_col, "EVIDENCE TYPE *")
        self.evtype_var = ctk.StringVar(value=EV_TYPES[0])
        ctk.CTkOptionMenu(type_col, values=EV_TYPES, variable=self.evtype_var,
                          fg_color=BG_INPUT, button_color=PURPLE,
                          button_hover_color=PURPLE2, text_color=TEXT_MAIN
                          ).pack(fill="x", pady=(4, 0))

        inv_col = ctk.CTkFrame(r1, fg_color="transparent")
        inv_col.pack(side="left", fill="x", expand=True, padx=(6, 0))
        self._lbl(inv_col, "COLLECTED BY *")
        self.inv_var = ctk.StringVar(value=inv_names[0] if inv_names else "")
        ctk.CTkOptionMenu(inv_col, values=inv_names, variable=self.inv_var,
                          fg_color=BG_INPUT, button_color=PURPLE,
                          button_hover_color=PURPLE2, text_color=TEXT_MAIN
                          ).pack(fill="x", pady=(4, 0))

        # Row 2: storage + collection location
        r2 = ctk.CTkFrame(inner, fg_color="transparent")
        r2.pack(fill="x", pady=(0, 14))

        stor_col = ctk.CTkFrame(r2, fg_color="transparent")
        stor_col.pack(side="left", fill="x", expand=True, padx=(0, 6))
        self._lbl(stor_col, "STORAGE LOCATION *")
        self.storage_var = ctk.StringVar(value=STORAGE_LOCS[0])
        ctk.CTkOptionMenu(stor_col, values=STORAGE_LOCS, variable=self.storage_var,
                          fg_color=BG_INPUT, button_color=PURPLE,
                          button_hover_color=PURPLE2, text_color=TEXT_MAIN
                          ).pack(fill="x", pady=(4, 0))

        col_col = ctk.CTkFrame(r2, fg_color="transparent")
        col_col.pack(side="left", fill="x", expand=True, padx=(6, 0))
        self._lbl(col_col, "COLLECTION LOCATION *")
        self.collect_var = ctk.StringVar(value=COLLECT_LOCS[0])
        ctk.CTkOptionMenu(col_col, values=COLLECT_LOCS, variable=self.collect_var,
                          fg_color=BG_INPUT, button_color=PURPLE,
                          button_hover_color=PURPLE2, text_color=TEXT_MAIN
                          ).pack(fill="x", pady=(4, 0))

        # Source IP
        self._lbl(inner, "SOURCE IP (OPTIONAL)")
        self.ip_entry = self._entry(inner, "e.g. 192.168.1.1", pady=(4, 14))

        # Description
        self._lbl(inner, "EVIDENCE DESCRIPTION *")
        self.desc_entry = ctk.CTkTextbox(
            inner, height=90, fg_color=BG_INPUT,
            border_color=PURPLE_DIM, border_width=1,
            text_color=TEXT_MAIN, corner_radius=10)
        self.desc_entry.pack(fill="x", pady=(4, 14))

        self.msg_label = ctk.CTkLabel(inner, text="",
                                       font=ctk.CTkFont(size=12),
                                       text_color=GREEN)
        self.msg_label.pack(pady=(0, 4))

        ctk.CTkButton(inner, text="Submit Evidence", height=46,
                      fg_color=PURPLE, hover_color=PURPLE2,
                      font=ctk.CTkFont(size=15, weight="bold"),
                      corner_radius=10, command=self._submit
                      ).pack(fill="x")

    def _confirm_delete_evidence(self, ev_num, ev_map):
        """Confirmation popup for evidence deletion."""
        popup = ctk.CTkToplevel()
        popup.title("Confirm Delete")
        popup.geometry("380x190")
        popup.resizable(False, False)
        popup.configure(fg_color=BG_DARK)
        popup.grab_set()

        popup.update_idletasks()
        x = (popup.winfo_screenwidth()  - 380) // 2
        y = (popup.winfo_screenheight() - 190) // 2
        popup.geometry(f"380x190+{x}+{y}")

        ctk.CTkLabel(popup, text="Delete Evidence?",
                     font=ctk.CTkFont(size=16, weight="bold"),
                     text_color="#ffffff").pack(pady=(24, 6))
        ctk.CTkLabel(popup,
                     text=f"Permanently delete '{ev_num}' and all related records?",
                     font=ctk.CTkFont(size=12), text_color=TEXT_DIM).pack()
        ctk.CTkLabel(popup,
                     text="Chain of custody and integrity records will also be deleted.",
                     font=ctk.CTkFont(size=10), text_color=TEXT_FAINT).pack(pady=(4, 0))

        btn_row = ctk.CTkFrame(popup, fg_color="transparent")
        btn_row.pack(pady=18)

        def _do_delete():
            try:
                rows = run_query(
                    "SELECT evidence_id FROM evidence WHERE evidence_number=?",
                    (ev_num,)
                )
                if rows:
                    ev_id = rows[0]["evidence_id"]
                    execute_command(
                        "DELETE FROM evidence_integrity WHERE evidence_id=?", (ev_id,))
                    execute_command(
                        "DELETE FROM chain_of_custody WHERE evidence_id=?", (ev_id,))
                    execute_command(
                        "DELETE FROM evidence WHERE evidence_id=?", (ev_id,))
            except Exception:
                pass
            popup.destroy()
            # Refresh page
            for w in self.winfo_children():
                w.destroy()
            self._build_list()

        ctk.CTkButton(btn_row, text="Delete", width=130, height=36,
                      fg_color=RED_DARK, hover_color=RED,
                      text_color="#ffffff",
                      font=ctk.CTkFont(size=13, weight="bold"),
                      corner_radius=8,
                      command=_do_delete).pack(side="left", padx=8)

        ctk.CTkButton(btn_row, text="Cancel", width=130, height=36,
                      fg_color=BG_CARD, hover_color=PURPLE_DIM,
                      text_color=TEXT_MAIN,
                      font=ctk.CTkFont(size=13),
                      corner_radius=8,
                      command=popup.destroy).pack(side="left", padx=8)

    def _refresh_auto(self, _=None):
        sel_key = self.case_var.get()
        if sel_key and sel_key in self.case_map:
            _, case_no = self.case_map[sel_key]
            new_ev   = _gen_evidence_number(case_no)
            new_hash = _gen_sha256(new_ev, case_no)
            self.ev_num_var.set(new_ev)
            self.hash_var.set(new_hash)

    def _submit(self):
        desc = self.desc_entry.get("1.0", "end").strip()
        if not desc:
            self.msg_label.configure(
                text="Please fill the description field.", text_color=RED)
            return

        sel_key = self.case_var.get()
        case_id, case_no = self.case_map[sel_key]
        ev_num    = self.ev_num_var.get()
        ev_hash   = self.hash_var.get()
        inv_id    = self.inv_map[self.inv_var.get()]
        source_ip = self.ip_entry.get().strip() or None

        try:
            new_ev_id = execute_command(
                "INSERT INTO evidence (case_id,evidence_number,evidence_type,"
                "description,collected_at,collected_by,storage_location,"
                "source_ip,status) VALUES (?,?,?,?,?,?,?,?,'collected')",
                (case_id, ev_num, self.evtype_var.get(), desc,
                 str(datetime.now()), inv_id, self.storage_var.get(), source_ip)
            )
            execute_command(
                "INSERT INTO chain_of_custody (evidence_id,handled_by,"
                "action_time,action_type,location,reason) "
                "VALUES (?,?,?,'collected',?,'Initial collection at scene')",
                (new_ev_id, inv_id, str(datetime.now()), self.collect_var.get())
            )
            execute_command(
                "INSERT INTO evidence_integrity (evidence_id,sha256_hash,"
                "verified_by,is_tampered,notes) "
                "VALUES (?,?,?,0,'Auto-generated hash on collection')",
                (new_ev_id, ev_hash, inv_id)
            )
            self.msg_label.configure(
                text=f"Evidence {ev_num} submitted. Chain of custody created.",
                text_color=GREEN)
            self.desc_entry.delete("1.0", "end")
            self.ip_entry.delete(0, "end")
            self._refresh_auto()
        except Exception as e:
            self.msg_label.configure(text=f"Error: {e}", text_color=RED)

    # Helpers
    def _lbl(self, parent, text):
        ctk.CTkLabel(parent, text=text,
                     font=ctk.CTkFont(size=10, weight="bold"),
                     text_color=TEXT_DIM).pack(anchor="w")

    def _lbl_outer(self, text):
        ctk.CTkLabel(self, text=text,
                     font=ctk.CTkFont(size=10, weight="bold"),
                     text_color=TEXT_DIM).pack(padx=28, anchor="w")

    def _entry(self, parent, placeholder, pady=(4, 14)):
        e = ctk.CTkEntry(parent, placeholder_text=placeholder,
                         fg_color=BG_INPUT, border_color=PURPLE_DIM,
                         text_color=TEXT_MAIN,
                         placeholder_text_color=TEXT_FAINT,
                         height=40, corner_radius=10)
        e.pack(fill="x", pady=pady)
        return e