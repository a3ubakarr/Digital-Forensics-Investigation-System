"""
DFIS — Digital Forensics Investigation System
File        : custody.py
Description : Chain of Custody tracker + Integrity Check (SHA-256)
Developer   : Member 4
"""

import customtkinter as ctk
from database import run_query

BG_DARK   = "#060a18"
BG_CARD   = "#0a0e1e"
PURPLE    = "#6366f1"
PURPLE2   = "#8b5cf6"
TEXT_MAIN = "#e2e8f0"
TEXT_DIM  = "#a0aec0"
GREEN     = "#22c55e"
RED       = "#ef4444"
ORANGE    = "#fb923c"
BLUE      = "#60a5fa"


class CustodyFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, session, mode="custody", **kwargs):
        super().__init__(master, **kwargs)
        self.session = session
        self.mode    = mode
        self.configure(scrollbar_button_color=BG_DARK)
        self._build()

    def _build(self):
        if self.mode == "integrity":
            self._build_integrity()
        else:
            self._build_custody()

    # ────────────────────────────────────────────────────
    #  CHAIN OF CUSTODY
    # ────────────────────────────────────────────────────
    def _build_custody(self):
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.pack(fill="x", padx=28, pady=(22, 0))
        ctk.CTkLabel(hdr, text="Chain of Custody Tracker",
                     font=ctk.CTkFont(size=22, weight="bold"),
                     text_color="#ffffff").pack(anchor="w")
        ctk.CTkLabel(hdr, text="Full audit trail — who handled what, when, and where",
                     font=ctk.CTkFont(size=12), text_color=TEXT_DIM).pack(anchor="w")

        sep = ctk.CTkFrame(self, fg_color="#1a202c", height=1)
        sep.pack(fill="x", padx=28, pady=14)

        # Evidence selector
        ev_rows = run_query("SELECT evidence_number FROM evidence ORDER BY evidence_number")
        ev_list = [r["evidence_number"] for r in ev_rows]

        ctk.CTkLabel(self, text="SELECT EVIDENCE ITEM",
                     font=ctk.CTkFont(size=10, weight="bold"),
                     text_color=TEXT_DIM).pack(padx=28, anchor="w")

        self.ev_var = ctk.StringVar(value=ev_list[0] if ev_list else "")
        ctk.CTkOptionMenu(self, values=ev_list, variable=self.ev_var,
                          fg_color=BG_CARD, button_color=PURPLE,
                          button_hover_color=PURPLE2, text_color=TEXT_MAIN,
                          height=40,
                          command=lambda _: self._load_custody()
                          ).pack(fill="x", padx=28, pady=(4, 14))

        self.custody_container = ctk.CTkFrame(self, fg_color="transparent")
        self.custody_container.pack(fill="x", padx=28, pady=(0, 28))

        if ev_list:
            self._load_custody()

    def _load_custody(self):
        for w in self.custody_container.winfo_children():
            w.destroy()

        sel_ev = self.ev_var.get()
        rows = run_query(
            """SELECT cc.action_type, cc.action_time, i.full_name AS handled_by,
                      cc.location, cc.reason, cc.witness_name
               FROM chain_of_custody cc
               JOIN evidence e  ON cc.evidence_id = e.evidence_id
               JOIN investigators i ON cc.handled_by = i.investigator_id
               WHERE e.evidence_number = ?
               ORDER BY cc.action_time""",
            (sel_ev,)
        )

        if not rows:
            ctk.CTkLabel(self.custody_container,
                         text="⚠  No custody records found for this evidence item.",
                         font=ctk.CTkFont(size=13), text_color=ORANGE).pack(pady=20)
            return

        # Summary badge
        summary = ctk.CTkFrame(self.custody_container, fg_color="#0f2412",
                                border_color="#14532d", border_width=1,
                                corner_radius=10)
        summary.pack(fill="x", pady=(0, 12))
        ctk.CTkLabel(summary, text=f"✅  {len(rows)} custody record(s) found for {sel_ev}",
                     font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=GREEN).pack(padx=16, pady=10)

        action_icons = {
            "collected":       "📥",
            "transferred":     "🚚",
            "analyzed":        "🔬",
            "stored":          "🗄",
            "returned":        "↩",
            "destroyed":       "🔥",
            "released_to_court": "⚖",
        }

        for i, row in enumerate(rows):
            card = ctk.CTkFrame(self.custody_container, fg_color=BG_CARD,
                                 border_color="#141540", border_width=1,
                                 corner_radius=12)
            card.pack(fill="x", pady=4)

            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(fill="x", padx=18, pady=14)

            # Step indicator + action
            top = ctk.CTkFrame(inner, fg_color="transparent")
            top.pack(fill="x")

            step_badge = ctk.CTkLabel(top,
                                       text=f"  Step {i+1}  ",
                                       font=ctk.CTkFont(size=9, weight="bold"),
                                       fg_color="#232480",
                                       text_color=PURPLE,
                                       corner_radius=8)
            step_badge.pack(side="left")

            icon = action_icons.get(row["action_type"], "•")
            ctk.CTkLabel(top,
                         text=f"  {icon}  {row['action_type'].upper().replace('_',' ')}",
                         font=ctk.CTkFont(size=13, weight="bold"),
                         text_color="#ffffff").pack(side="left", padx=10)

            ctk.CTkLabel(top, text=str(row["action_time"]),
                         font=ctk.CTkFont(size=10), text_color="#64748b").pack(side="right")

            # Details grid
            details = ctk.CTkFrame(inner, fg_color="transparent")
            details.pack(fill="x", pady=(10, 0))
            details.columnconfigure((0, 1), weight=1)

            self._detail_item(details, "👤 Handled By", row["handled_by"], 0, 0)
            self._detail_item(details, "📍 Location", row["location"] or "—", 1, 0)
            self._detail_item(details, "📋 Reason", row["reason"] or "—", 0, 1)
            self._detail_item(details, "👁 Witness",
                              row["witness_name"] if row["witness_name"] else "None", 1, 1)

    def _detail_item(self, parent, label, value, row, col):
        frame = ctk.CTkFrame(parent, fg_color="#0d0e1a",
                              border_color="#12143a", border_width=1,
                              corner_radius=8)
        frame.grid(row=row, column=col, padx=4, pady=4, sticky="nsew")
        ctk.CTkLabel(frame, text=label,
                     font=ctk.CTkFont(size=9, weight="bold"),
                     text_color=TEXT_DIM).pack(padx=10, pady=(8, 2), anchor="w")
        ctk.CTkLabel(frame, text=value,
                     font=ctk.CTkFont(size=12), text_color=TEXT_MAIN,
                     wraplength=250, justify="left").pack(padx=10, pady=(0, 8), anchor="w")

    # ────────────────────────────────────────────────────
    #  INTEGRITY CHECK
    # ────────────────────────────────────────────────────
    def _build_integrity(self):
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.pack(fill="x", padx=28, pady=(22, 0))
        ctk.CTkLabel(hdr, text="Evidence Integrity Verification",
                     font=ctk.CTkFont(size=22, weight="bold"),
                     text_color="#ffffff").pack(anchor="w")

        # Info banner
        info = ctk.CTkFrame(self, fg_color="#0f1028",
                             border_color="#2a2b7a", border_width=1,
                             corner_radius=10)
        info.pack(fill="x", padx=28, pady=14)
        ctk.CTkLabel(info,
                     text="🛡  SHA-256 hash verification system — detects tampered evidence",
                     font=ctk.CTkFont(size=12), text_color="#c7d2fe").pack(padx=16, pady=10)

        rows = run_query(
            """SELECT e.evidence_number, e.evidence_type, c.case_number,
                      ei.sha256_hash, ei.verified_at, ei.is_tampered,
                      ei.notes, i.full_name AS verified_by
               FROM evidence_integrity ei
               JOIN evidence e ON ei.evidence_id = e.evidence_id
               JOIN cases c    ON e.case_id = c.case_id
               JOIN investigators i ON ei.verified_by = i.investigator_id
               ORDER BY ei.is_tampered DESC, ei.verified_at DESC"""
        )

        tampered = [r for r in rows if r["is_tampered"]]
        clean    = [r for r in rows if not r["is_tampered"]]

        # Tampered section
        if tampered:
            alert = ctk.CTkFrame(self, fg_color="#2a0a0a",
                                  border_color="#7f1d1d", border_width=1,
                                  corner_radius=10)
            alert.pack(fill="x", padx=28, pady=(0, 8))
            ctk.CTkLabel(alert,
                         text=f"🚨  {len(tampered)} tampered evidence item(s) detected!",
                         font=ctk.CTkFont(size=13, weight="bold"),
                         text_color=RED).pack(padx=16, pady=10)

            for r in tampered:
                self._integrity_card(r, tampered=True)

            sep = ctk.CTkFrame(self, fg_color="#1a202c", height=1)
            sep.pack(fill="x", padx=28, pady=10)

        # Clean section
        clean_banner = ctk.CTkFrame(self, fg_color="#0d2010",
                                     border_color="#14532d", border_width=1,
                                     corner_radius=10)
        clean_banner.pack(fill="x", padx=28, pady=(0, 8))
        ctk.CTkLabel(clean_banner,
                     text=f"✅  {len(clean)} evidence item(s) verified clean",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=GREEN).pack(padx=16, pady=10)

        for r in clean:
            self._integrity_card(r, tampered=False)

        # Bottom padding
        ctk.CTkFrame(self, fg_color="transparent", height=28).pack()

    def _integrity_card(self, row, tampered):
        clr = RED if tampered else GREEN
        card = ctk.CTkFrame(self, fg_color=BG_CARD,
                             border_color=clr, border_width=1,
                             corner_radius=12)
        card.pack(fill="x", padx=28, pady=4)

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=18, pady=14)

        top = ctk.CTkFrame(inner, fg_color="transparent")
        top.pack(fill="x")
        ctk.CTkLabel(top, text=row["evidence_number"],
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color="#ffffff").pack(side="left")
        ctk.CTkLabel(top,
                     text=f"  {'⚠ TAMPERED' if tampered else '✓ CLEAN'}  ",
                     font=ctk.CTkFont(size=9, weight="bold"),
                     fg_color="#0d2010" if clr == "#22c55e" else "#2a0a0a", text_color=clr,
                     corner_radius=10).pack(side="left", padx=8)
        ctk.CTkLabel(top, text=row["evidence_type"],
                     font=ctk.CTkFont(size=10), text_color="#64748b").pack(side="left")

        meta = f"📁 Case: {row['case_number']}   |   👤 Verified by: {row['verified_by']}   |   🕐 {row['verified_at']}"
        ctk.CTkLabel(inner, text=meta,
                     font=ctk.CTkFont(size=10), text_color="#4a5568").pack(anchor="w", pady=(4, 4))

        # Hash
        hash_frame = ctk.CTkFrame(inner, fg_color="#0d0e1a",
                                   border_color="#12143a", border_width=1,
                                   corner_radius=8)
        hash_frame.pack(fill="x", pady=(0, 6))
        ctk.CTkLabel(hash_frame, text="SHA-256",
                     font=ctk.CTkFont(size=9, weight="bold"),
                     text_color=TEXT_DIM).pack(padx=12, pady=(6, 2), anchor="w")
        ctk.CTkLabel(hash_frame, text=row["sha256_hash"],
                     font=ctk.CTkFont(family="Courier New", size=10),
                     text_color=BLUE).pack(padx=12, pady=(0, 6), anchor="w")

        if row["notes"]:
            ctk.CTkLabel(inner, text=f"📝  {row['notes']}",
                         font=ctk.CTkFont(size=11), text_color=TEXT_DIM).pack(anchor="w")