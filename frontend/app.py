import customtkinter as ctk
import tkinter as tk
from backend.database import init_db
from backend.auth import login
from frontend.dashboard import DashboardFrame
from frontend.cases import CasesFrame
from frontend.evidence import EvidenceFrame
from frontend.custody import CustodyFrame
from frontend.reports import ReportsFrame

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

BG_DARK      = "#060a18"
BG_CARD      = "#0a0e1e"
BG_SIDEBAR   = "#04060f"
BG_INPUT     = "#0f1428"
PURPLE       = "#6366f1"
PURPLE_DARK  = "#4338ca"
PURPLE_DIM   = "#312e81"
PURPLE_HOVER = "#8b5cf6"
TEXT_MAIN    = "#e2e8f0"
TEXT_DIM     = "#a0aec0"
TEXT_FAINT   = "#4a5568"
SEP_COLOR    = "#1a202c"
GREEN        = "#22c55e"
RED          = "#ef4444"
RED_DARK     = "#7f1d1d"
ORANGE       = "#fb923c"
BLUE         = "#60a5fa"


def draw_logo(canvas, cx, cy, size=28):
    """Draw shield + magnifier logo on a Canvas."""
    s = size / 28
    pts = [cx, cy-14*s, cx+12*s, cy-8*s, cx+12*s, cy+2*s,
           cx, cy+14*s, cx-12*s, cy+2*s, cx-12*s, cy-8*s]
    canvas.create_polygon(pts, fill=PURPLE_DARK, outline=PURPLE, width=1)
    pts2 = [cx, cy-9*s, cx+7*s, cy-5*s, cx+7*s, cy+1*s,
            cx, cy+8*s, cx-7*s, cy+1*s, cx-7*s, cy-5*s]
    canvas.create_polygon(pts2, fill="#0a0e1e", outline="")
    canvas.create_oval(cx-2*s, cy-6*s, cx+8*s, cy+4*s, outline=PURPLE, width=round(1.5*s), fill="")
    canvas.create_line(cx+6*s, cy+2*s, cx+10*s, cy+7*s, fill=PURPLE, width=round(2*s), capstyle=tk.ROUND)


class LoginWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("DFIS - Digital Forensics Investigation System")
        self.configure(fg_color=BG_DARK)
        # Get screen dimensions and set window to full screen size
        self.update_idletasks()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        self.geometry(f"{sw}x{sh}+0+0")
        self._build_ui()

    def _build_ui(self):
        # Full canvas background
        self.update_idletasks()

        # Left 46% — branding
        left = ctk.CTkFrame(self, fg_color="transparent")
        left.place(relx=0, rely=0, relwidth=0.46, relheight=1)

        # Vertical separator
        ctk.CTkFrame(self, fg_color="#1e1b4b", width=1).place(
            relx=0.46, rely=0.06, relwidth=0, relheight=0.88)

        # Right 54% — login
        right = ctk.CTkFrame(self, fg_color="transparent")
        right.place(relx=0.46, rely=0, relwidth=0.54, relheight=1)

        # ── LEFT: centered at exact midpoint ────────────────────────
        left_inner = ctk.CTkFrame(left, fg_color="transparent")
        left_inner.place(relx=0.55, rely=0.5, anchor="center")

        logo_canvas = tk.Canvas(
            left_inner, width=180, height=180,
            bg=BG_DARK, highlightthickness=0)
        logo_canvas.pack()
        draw_logo(logo_canvas, 90, 90, size=82)

        ctk.CTkLabel(
            left_inner, text="DFIS",
            font=ctk.CTkFont(family="Segoe UI", size=76, weight="bold"),
            text_color="#ffffff"
        ).pack(pady=(14, 0))

        ctk.CTkLabel(
            left_inner,
            text="Digital Forensics Investigation System",
            font=ctk.CTkFont(size=14),
            text_color=TEXT_DIM
        ).pack(pady=(4, 0))

        ctk.CTkFrame(
            left_inner, fg_color=PURPLE,
            height=2, width=48
        ).pack(pady=16)

        ctk.CTkLabel(
            left_inner,
            text="National Investigation Agency",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=TEXT_FAINT
        ).pack()
        ctk.CTkLabel(
            left_inner,
            text="Cyber Crime Division",
            font=ctk.CTkFont(size=12),
            text_color=TEXT_FAINT
        ).pack(pady=(3, 0))

        # ── RIGHT: exact same vertical center as left ────────────────
        right_inner = ctk.CTkFrame(right, fg_color="transparent")
        right_inner.place(relx=0.48, rely=0.5, anchor="center")

        ctk.CTkLabel(
            right_inner, text="Secure Access Portal",
            font=ctk.CTkFont(family="Segoe UI", size=30, weight="bold"),
            text_color="#ffffff"
        ).pack(anchor="w")
        ctk.CTkLabel(
            right_inner,
            text="Enter your credentials to continue",
            font=ctk.CTkFont(size=13),
            text_color=TEXT_DIM
        ).pack(anchor="w", pady=(5, 0))

        # Card — height controlled by inner content, no fixed size
        card = ctk.CTkFrame(
            right_inner, fg_color=BG_CARD,
            border_color=PURPLE_DIM, border_width=1,
            corner_radius=18, width=460)
        card.pack(pady=20, anchor="w")

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(padx=44, pady=44, fill="x")

        # Username
        ctk.CTkLabel(
            inner, text="USERNAME",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=TEXT_DIM
        ).pack(anchor="w")
        self.username_entry = ctk.CTkEntry(
            inner, placeholder_text="Enter your username",
            fg_color=BG_INPUT, border_color=PURPLE_DIM,
            text_color=TEXT_MAIN, placeholder_text_color=TEXT_FAINT,
            height=52, corner_radius=10, width=372)
        self.username_entry.pack(fill="x", pady=(8, 24))

        # Password
        ctk.CTkLabel(
            inner, text="PASSWORD",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=TEXT_DIM
        ).pack(anchor="w")

        pw_row = ctk.CTkFrame(inner, fg_color="transparent")
        pw_row.pack(fill="x", pady=(8, 0))

        self.password_entry = ctk.CTkEntry(
            pw_row, placeholder_text="Enter your password", show="*",
            fg_color=BG_INPUT, border_color=PURPLE_DIM,
            text_color=TEXT_MAIN, placeholder_text_color=TEXT_FAINT,
            height=52, corner_radius=10)
        self.password_entry.pack(side="left", fill="x", expand=True)
        self.password_entry.bind("<Return>", lambda e: self._login())

        self._pw_visible = False
        self.eye_btn = ctk.CTkButton(
            pw_row, text="Show", width=86, height=52,
            fg_color=PURPLE_DIM, hover_color=PURPLE,
            text_color=TEXT_MAIN, font=ctk.CTkFont(size=12),
            corner_radius=10, command=self._toggle_password)
        self.eye_btn.pack(side="left", padx=(10, 0))

        self.error_label = ctk.CTkLabel(
            inner, text="",
            font=ctk.CTkFont(size=12), text_color=RED)
        self.error_label.pack(pady=(14, 0))

        ctk.CTkButton(
            inner, text="Sign In", height=54,
            fg_color=PURPLE, hover_color=PURPLE_HOVER,
            font=ctk.CTkFont(size=15, weight="bold"),
            corner_radius=10, command=self._login
        ).pack(fill="x", pady=(12, 0))

        ctk.CTkLabel(
            right_inner,
            text="Authorized personnel only  —  All access is logged",
            font=ctk.CTkFont(size=10),
            text_color=TEXT_FAINT
        ).pack(pady=(6, 0))

    def _toggle_password(self):
        self._pw_visible = not self._pw_visible
        self.password_entry.configure(show="" if self._pw_visible else "*")
        self.eye_btn.configure(text="Hide" if self._pw_visible else "Show")

    def _login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        if not username or not password:
            self.error_label.configure(text="Please enter both username and password.")
            return
        session, error = login(username, password)
        if error:
            self.error_label.configure(text=error)
            return
        self.destroy()
        MainApp(session).mainloop()


class MainApp(ctk.CTk):
    def __init__(self, session):
        super().__init__()
        self.session = session
        self.title("DFIS - Digital Forensics Investigation System")
        self.geometry("1280x780")
        self.minsize(1100, 650)
        self.configure(fg_color=BG_DARK)
        self._center()

        role = session["role"]
        if role == "admin":
            self.pages = ["Dashboard", "Cases", "New Case", "Evidence",
                          "New Evidence", "Chain of Custody", "Integrity Check",
                          "Reports", "User Management", "Access Logs"]
        elif role == "investigator":
            self.pages = ["Dashboard", "Cases", "New Case", "Evidence",
                          "New Evidence", "Chain of Custody", "Reports"]
        else:
            self.pages = ["Dashboard", "Cases", "Evidence", "Integrity Check", "Reports"]

        self._build_layout()
        self._show_page("Dashboard")

    def _center(self):
        self.update_idletasks()
        x = (self.winfo_screenwidth()  - 1280) // 2
        y = (self.winfo_screenheight() - 780)  // 2
        self.geometry(f"1280x780+{x}+{y}")

    def _build_layout(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self._build_sidebar()
        self.content = ctk.CTkFrame(self, fg_color=BG_DARK, corner_radius=0)
        self.content.grid(row=0, column=1, sticky="nsew")
        self.content.grid_rowconfigure(0, weight=1)
        self.content.grid_columnconfigure(0, weight=1)
        self.current_frame = None

    def _build_sidebar(self):
        sidebar = ctk.CTkFrame(self, fg_color=BG_SIDEBAR, width=220,
                                corner_radius=0, border_color=SEP_COLOR, border_width=1)
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_propagate(False)
        sidebar.grid_rowconfigure(2, weight=1)

        # Logo
        logo_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        logo_frame.grid(row=0, column=0, padx=16, pady=(16, 10), sticky="ew")
        logo_canvas = tk.Canvas(logo_frame, width=32, height=32, bg=BG_SIDEBAR, highlightthickness=0)
        logo_canvas.pack(side="left")
        draw_logo(logo_canvas, 16, 16, size=14)
        title_frame = ctk.CTkFrame(logo_frame, fg_color="transparent")
        title_frame.pack(side="left", padx=(8, 0))
        ctk.CTkLabel(title_frame, text="DFIS",
                     font=ctk.CTkFont(size=16, weight="bold"), text_color="#ffffff").pack(anchor="w")
        ctk.CTkLabel(title_frame, text="NIA Cyber Crime",
                     font=ctk.CTkFont(size=9), text_color=TEXT_FAINT).pack(anchor="w")

        # User card
        user_card = ctk.CTkFrame(sidebar, fg_color="#0c0f2a",
                                  border_color=PURPLE_DIM, border_width=1, corner_radius=10)
        user_card.grid(row=1, column=0, padx=12, pady=(0, 10), sticky="ew")
        uc_inner = ctk.CTkFrame(user_card, fg_color="transparent")
        uc_inner.pack(padx=14, pady=12, fill="x")

        # Online dot + name
        name_row = ctk.CTkFrame(uc_inner, fg_color="transparent")
        name_row.pack(fill="x")
        dot = tk.Canvas(name_row, width=8, height=8, bg="#0c0f2a", highlightthickness=0)
        dot.pack(side="left", pady=2)
        dot.create_oval(1, 1, 7, 7, fill=GREEN, outline="")
        ctk.CTkLabel(name_row, text=self.session["inv_name"],
                     font=ctk.CTkFont(size=12, weight="bold"),
                     text_color="#ffffff").pack(side="left", padx=(6, 0))

        # Badge — show username if badge is same as role (admin case)
        badge = self.session["inv_badge"]
        badge_display = f"@{self.session['username']}" if badge == "ADMIN" else badge
        ctk.CTkLabel(uc_inner, text=badge_display,
                     font=ctk.CTkFont(family="Courier New", size=9),
                     text_color="#6366f1").pack(anchor="w", pady=(4, 5))

        # Role pill
        role_colors = {
            "admin":        ("#3b0764", "#c4b5fd"),
            "investigator": ("#1e1b4b", "#a5b4fc"),
            "analyst":      ("#0c1a3a", "#93c5fd"),
        }
        pill_bg, pill_txt = role_colors.get(self.session["role"], ("#1e1b4b", "#a5b4fc"))
        role_pill = ctk.CTkFrame(uc_inner, fg_color=pill_bg, corner_radius=5)
        role_pill.pack(anchor="w")
        ctk.CTkLabel(role_pill,
                     text=f"  {self.session['role'].upper()}  ",
                     font=ctk.CTkFont(size=9, weight="bold"),
                     text_color=pill_txt).pack(padx=2, pady=3)

        # Nav buttons
        nav_frame = ctk.CTkScrollableFrame(sidebar, fg_color="transparent",
                                            scrollbar_button_color=BG_SIDEBAR)
        nav_frame.grid(row=2, column=0, padx=8, sticky="nsew")

        self.nav_buttons = {}
        for page in self.pages:
            btn = ctk.CTkButton(nav_frame, text=page, anchor="w", height=36,
                                fg_color="transparent", hover_color=PURPLE_DARK,
                                text_color=TEXT_DIM, font=ctk.CTkFont(size=13),
                                corner_radius=8, command=lambda p=page: self._show_page(p))
            btn.pack(fill="x", pady=2)
            self.nav_buttons[page] = btn

        ctk.CTkFrame(sidebar, fg_color=SEP_COLOR, height=1).grid(
            row=3, column=0, padx=0, sticky="ew")

        ctk.CTkButton(sidebar, text="Sign Out",
                      height=40,
                      fg_color="#7f1d1d",
                      hover_color="#991b1b",
                      text_color="#fca5a5",
                      font=ctk.CTkFont(size=12, weight="bold"),
                      corner_radius=8,
                      command=self._logout).grid(
                          row=4, column=0,
                          padx=12, pady=(10, 16),
                          sticky="ew")

    def _show_page(self, page_name):
        for name, btn in self.nav_buttons.items():
            btn.configure(fg_color=PURPLE_DIM if name == page_name else "transparent",
                          text_color="#ffffff" if name == page_name else TEXT_DIM)

        if self.current_frame:
            self.current_frame.destroy()

        kwargs = dict(master=self.content, session=self.session, fg_color=BG_DARK, corner_radius=0)
        frame_map = {
            "Dashboard":        lambda: DashboardFrame(**kwargs),
            "Cases":            lambda: CasesFrame(**kwargs, mode="list"),
            "New Case":         lambda: CasesFrame(**kwargs, mode="new"),
            "Evidence":         lambda: EvidenceFrame(**kwargs, mode="list"),
            "New Evidence":     lambda: EvidenceFrame(**kwargs, mode="new"),
            "Chain of Custody": lambda: CustodyFrame(**kwargs),
            "Integrity Check":  lambda: CustodyFrame(**kwargs, mode="integrity"),
            "Reports":          lambda: ReportsFrame(**kwargs),
            "User Management":  lambda: ReportsFrame(**kwargs, mode="users"),
            "Access Logs":      lambda: ReportsFrame(**kwargs, mode="logs"),
        }
        builder = frame_map.get(page_name)
        if builder:
            self.current_frame = builder()
            self.current_frame.grid(row=0, column=0, sticky="nsew")

    def _logout(self):
        self.destroy()
        LoginWindow().mainloop()


if __name__ == "__main__":
    init_db()
    LoginWindow().mainloop()
