"""
DFIS — Digital Forensics Investigation System
File        : dashboard.py
Description : Dashboard screen — stat cards + charts + recent activity
Developer   : Malik Abubakar (Group Lead)
"""

import customtkinter as ctk
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from database import run_query

BG_DARK  = "#060a18"
BG_CARD  = "#0a0e1e"
PURPLE   = "#6366f1"
PURPLE2  = "#8b5cf6"
TEXT_MAIN = "#e2e8f0"
TEXT_DIM  = "#a0aec0"
GREEN    = "#22c55e"
RED      = "#ef4444"
ORANGE   = "#fb923c"
BLUE     = "#60a5fa"

plt.rcParams.update({
    "figure.facecolor":  BG_CARD,
    "axes.facecolor":    BG_CARD,
    "axes.edgecolor":    "#1a202c",
    "axes.labelcolor":   TEXT_DIM,
    "xtick.color":       TEXT_DIM,
    "ytick.color":       TEXT_DIM,
    "text.color":        TEXT_DIM,
    "grid.color":        "#111827",
    "font.family":       "Segoe UI",
})


class DashboardFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, session, **kwargs):
        super().__init__(master, **kwargs)
        self.session = session
        self.configure(scrollbar_button_color=BG_DARK)
        self._build()

    def _build(self):
        # ── Header ──────────────────────────────────────
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.pack(fill="x", padx=28, pady=(22, 0))

        ctk.CTkLabel(hdr, text="Investigation Command Center",
                     font=ctk.CTkFont(size=22, weight="bold"),
                     text_color="#ffffff").pack(anchor="w")
        ctk.CTkLabel(hdr, text="Real-time overview — NIA Cyber Crime Division",
                     font=ctk.CTkFont(size=12), text_color=TEXT_DIM).pack(anchor="w")

        sep = ctk.CTkFrame(self, fg_color="#1a202c", height=1)
        sep.pack(fill="x", padx=28, pady=14)

        # ── Stat Cards ──────────────────────────────────
        tc = self._q("SELECT COUNT(*) FROM cases")
        oc = self._q("SELECT COUNT(*) FROM cases WHERE status != 'closed'")
        cc = self._q("SELECT COUNT(*) FROM cases WHERE priority = 'critical'")
        te = self._q("SELECT COUNT(*) FROM evidence")
        tm = self._q("SELECT COUNT(*) FROM evidence_integrity WHERE is_tampered = 1")

        cards_data = [
            ("Total Cases",    tc, PURPLE, "📁"),
            ("Active Cases",   oc, GREEN,  "🔓"),
            ("Critical",       cc, RED,    "🚨"),
            ("Evidence Items", te, BLUE,   "🔒"),
            ("Tampered",       tm, ORANGE, "⚠"),
        ]

        cards_row = ctk.CTkFrame(self, fg_color="transparent")
        cards_row.pack(fill="x", padx=28, pady=(0, 14))
        for i in range(5):
            cards_row.columnconfigure(i, weight=1)

        for i, (label, value, color, icon) in enumerate(cards_data):
            card = ctk.CTkFrame(cards_row, fg_color=BG_CARD,
                                 border_color=color, border_width=1,
                                 corner_radius=14)
            card.grid(row=0, column=i, padx=6, sticky="nsew", ipady=10)

            ctk.CTkLabel(card, text=f"{icon}  {label}",
                         font=ctk.CTkFont(size=10, weight="bold"),
                         text_color=color).pack(padx=18, pady=(14, 4), anchor="w")
            ctk.CTkLabel(card, text=str(value),
                         font=ctk.CTkFont(size=36, weight="bold"),
                         text_color=color).pack(padx=18, pady=(0, 14), anchor="w")

        sep2 = ctk.CTkFrame(self, fg_color="#1a202c", height=1)
        sep2.pack(fill="x", padx=28, pady=(0, 14))

        # ── Charts Row ──────────────────────────────────
        charts_row = ctk.CTkFrame(self, fg_color="transparent")
        charts_row.pack(fill="x", padx=28, pady=(0, 14))
        charts_row.columnconfigure(0, weight=1)
        charts_row.columnconfigure(1, weight=1)

        # Bar chart — Cases by Type
        bar_card = ctk.CTkFrame(charts_row, fg_color=BG_CARD,
                                 border_color="#1e1f5e", border_width=1,
                                 corner_radius=14)
        bar_card.grid(row=0, column=0, padx=(0, 8), sticky="nsew")

        ctk.CTkLabel(bar_card, text="Cases by Type",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=TEXT_MAIN).pack(padx=18, pady=(14, 8), anchor="w")

        type_data = run_query(
            "SELECT case_type, COUNT(*) AS total FROM cases GROUP BY case_type ORDER BY total DESC"
        )
        if type_data:
            labels = [r["case_type"] for r in type_data]
            values = [r["total"]     for r in type_data]
            colors = [PURPLE, PURPLE2, "#a855f7", "#60a5fa", "#34d399",
                      "#fb923c", "#f87171", "#facc15", "#e2e8f0"]

            fig, ax = plt.subplots(figsize=(5, 2.8))
            bars = ax.bar(labels, values,
                          color=colors[:len(labels)], width=0.55, zorder=3)
            ax.set_ylabel("Cases", fontsize=9)
            ax.grid(axis="y", zorder=0)
            ax.tick_params(axis="x", labelsize=8, rotation=15)
            ax.tick_params(axis="y", labelsize=8)
            for bar, v in zip(bars, values):
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
                        str(v), ha="center", va="bottom", fontsize=8, color=TEXT_MAIN)
            fig.tight_layout()

            canvas = FigureCanvasTkAgg(fig, master=bar_card)
            canvas.draw()
            canvas.get_tk_widget().pack(padx=14, pady=(0, 14), fill="both", expand=True)
            plt.close(fig)

        # Pie chart — Cases by Status
        pie_card = ctk.CTkFrame(charts_row, fg_color=BG_CARD,
                                 border_color="#1e1f5e", border_width=1,
                                 corner_radius=14)
        pie_card.grid(row=0, column=1, padx=(8, 0), sticky="nsew")

        ctk.CTkLabel(pie_card, text="Cases by Status",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=TEXT_MAIN).pack(padx=18, pady=(14, 8), anchor="w")

        status_data = run_query(
            "SELECT status, COUNT(*) AS total FROM cases GROUP BY status"
        )
        if status_data:
            slabels = [r["status"] for r in status_data]
            svalues = [r["total"]  for r in status_data]
            pie_colors = [PURPLE, PURPLE2, "#a855f7", "#ec4899", "#14b8a6"]

            fig2, ax2 = plt.subplots(figsize=(5, 2.8))
            wedges, texts, autotexts = ax2.pie(
                svalues, labels=None,
                colors=pie_colors[:len(slabels)],
                autopct="%1.0f%%", pctdistance=0.75,
                wedgeprops=dict(width=0.55)   # donut
            )
            for at in autotexts:
                at.set_color("#ffffff")
                at.set_fontsize(8)
            ax2.legend(wedges, slabels, loc="lower center",
                       fontsize=8, ncol=3, frameon=False,
                       labelcolor=TEXT_DIM,
                       bbox_to_anchor=(0.5, -0.12))
            fig2.tight_layout()

            canvas2 = FigureCanvasTkAgg(fig2, master=pie_card)
            canvas2.draw()
            canvas2.get_tk_widget().pack(padx=14, pady=(0, 14), fill="both", expand=True)
            plt.close(fig2)

        sep3 = ctk.CTkFrame(self, fg_color="#1a202c", height=1)
        sep3.pack(fill="x", padx=28, pady=(0, 14))

        # ── Recent Activity Row ──────────────────────────
        recent_row = ctk.CTkFrame(self, fg_color="transparent")
        recent_row.pack(fill="x", padx=28, pady=(0, 28))
        recent_row.columnconfigure(0, weight=1)
        recent_row.columnconfigure(1, weight=1)

        # Recent Cases
        rc_card = ctk.CTkFrame(recent_row, fg_color=BG_CARD,
                                border_color="#1e1f5e", border_width=1,
                                corner_radius=14)
        rc_card.grid(row=0, column=0, padx=(0, 8), sticky="nsew")

        ctk.CTkLabel(rc_card, text="Recent Cases",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=TEXT_MAIN).pack(padx=18, pady=(14, 8), anchor="w")

        recent_cases = run_query(
            "SELECT case_number, title, status, priority FROM cases ORDER BY opened_date DESC LIMIT 5"
        )
        for row in recent_cases:
            pri_colors = {"critical": RED, "high": ORANGE, "medium": "#facc15", "low": GREEN}
            clr = pri_colors.get(row["priority"], TEXT_MAIN)
            item = ctk.CTkFrame(rc_card, fg_color="#0d0e1a",
                                 border_color="#141540", border_width=1,
                                 corner_radius=8)
            item.pack(fill="x", padx=14, pady=3)

            top = ctk.CTkFrame(item, fg_color="transparent")
            top.pack(fill="x", padx=12, pady=(8, 2))
            ctk.CTkLabel(top, text=row["case_number"],
                         font=ctk.CTkFont(size=12, weight="bold"),
                         text_color="#ffffff").pack(side="left")
            ctk.CTkLabel(top, text=row["priority"].upper(),
                         font=ctk.CTkFont(size=9, weight="bold"),
                         text_color=clr).pack(side="right")

            ctk.CTkLabel(item, text=row["title"],
                         font=ctk.CTkFont(size=11), text_color=TEXT_DIM,
                         wraplength=280, justify="left").pack(padx=12, pady=(0, 8), anchor="w")

        # Recent Evidence
        re_card = ctk.CTkFrame(recent_row, fg_color=BG_CARD,
                                border_color="#1e1f5e", border_width=1,
                                corner_radius=14)
        re_card.grid(row=0, column=1, padx=(8, 0), sticky="nsew")

        ctk.CTkLabel(re_card, text="Recent Evidence",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=TEXT_MAIN).pack(padx=18, pady=(14, 8), anchor="w")

        recent_ev = run_query(
            """SELECT e.evidence_number, e.evidence_type, e.status, c.case_number
               FROM evidence e JOIN cases c ON e.case_id=c.case_id
               ORDER BY e.collected_at DESC LIMIT 5"""
        )
        for row in recent_ev:
            s_colors = {"collected": BLUE, "in_analysis": ORANGE,
                        "verified": GREEN, "compromised": RED, "released": TEXT_DIM}
            clr = s_colors.get(row["status"], TEXT_MAIN)
            item = ctk.CTkFrame(re_card, fg_color="#0d0e1a",
                                 border_color="#141540", border_width=1,
                                 corner_radius=8)
            item.pack(fill="x", padx=14, pady=3)

            top = ctk.CTkFrame(item, fg_color="transparent")
            top.pack(fill="x", padx=12, pady=(8, 2))
            ctk.CTkLabel(top, text=row["evidence_number"],
                         font=ctk.CTkFont(size=12, weight="bold"),
                         text_color="#ffffff").pack(side="left")
            ctk.CTkLabel(top, text=row["status"].upper(),
                         font=ctk.CTkFont(size=9, weight="bold"),
                         text_color=clr).pack(side="right")

            ctk.CTkLabel(item,
                         text=f"{row['evidence_type']}  |  {row['case_number']}",
                         font=ctk.CTkFont(size=11), text_color=TEXT_DIM).pack(
                             padx=12, pady=(0, 8), anchor="w")

    def _q(self, sql):
        rows = run_query(sql)
        return rows[0][0] if rows else 0