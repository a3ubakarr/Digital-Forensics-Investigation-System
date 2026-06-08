"""
DFIS - Digital Forensics Investigation System
File        : app.py
Description : Main entry point - Login screen + App window controller
Developer   : Malik Abubakar (Group Lead)
"""

import customtkinter as ctk
import tkinter as tk
import hashlib
from datetime import datetime
from database import init_db, run_query, execute_command
from dashboard import DashboardFrame
from cases import CasesFrame
from evidence import EvidenceFrame
from custody import CustodyFrame
from reports import ReportsFrame

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Color palette - all 6-char hex only
BG_DARK     = "#060a18"
BG_CARD     = "#0a0e1e"
BG_SIDEBAR  = "#04060f"
BG_INPUT    = "#0f1428"
PURPLE      = "#6366f1"
PURPLE_DARK = "#4338ca"
PURPLE_DIM  = "#312e81"
PURPLE_HOVER= "#8b5cf6"
TEXT_MAIN   = "#e2e8f0"
TEXT_DIM    = "#a0aec0"
TEXT_FAINT  = "#4a5568"
TEXT_GHOST  = "#2d3748"
SEP_COLOR   = "#1a202c"
GREEN       = "#22c55e"
RED         = "#ef4444"
RED_DARK    = "#7f1d1d"
ORANGE      = "#fb923c"
BLUE        = "#60a5fa"



def draw_logo(canvas, cx, cy, size=28):
    """Draw a shield + magnifier logo on a tkinter Canvas."""
    s = size / 28  # scale factor

    # Shield body
    pts = [
        cx,       cy - 14*s,
        cx+12*s,  cy - 8*s,
        cx+12*s,  cy + 2*s,
        cx,       cy + 14*s,
        cx-12*s,  cy + 2*s,
        cx-12*s,  cy - 8*s,
    ]
    canvas.create_polygon(pts, fill=PURPLE_DARK, outline=PURPLE, width=1)

    # Inner shield highlight
    pts2 = [
        cx,       cy - 9*s,
        cx+7*s,   cy - 5*s,
        cx+7*s,   cy + 1*s,
        cx,       cy + 8*s,
        cx-7*s,   cy + 1*s,
        cx-7*s,   cy - 5*s,
    ]
    canvas.create_polygon(pts2, fill="#0a0e1e", outline="")

    # Magnifier circle
    canvas.create_oval(
        cx-2*s, cy-6*s, cx+8*s, cy+4*s,
        outline=PURPLE, width=round(1.5*s), fill=""
    )
    # Magnifier handle
    canvas.create_line(
        cx+6*s, cy+2*s, cx+10*s, cy+7*s,
        fill=PURPLE, width=round(2*s), capstyle=tk.ROUND
    )


# -------------------------------------------------------
#  LOGIN WINDOW
# -------------------------------------------------------
class LoginWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("DFIS - Digital Forensics Investigation System")
        self.geometry("460x580")
        self.resizable(True, True)
        self.configure(fg_color=BG_DARK)
        self._center()
        self._build_ui()

    def _center(self):
        self.update_idletasks()
        x = (self.winfo_screenwidth()  - 460) // 2
        y = (self.winfo_screenheight() - 580) // 2
        self.geometry(f"460x580+{x}+{y}")

    def _build_ui(self):
        # Outer wrapper - centers content vertically
        wrapper = ctk.CTkFrame(self, fg_color="transparent")
        wrapper.pack(expand=True, fill="both")

        # Content container - fixed width, centered
        container = ctk.CTkFrame(wrapper, fg_color="transparent", width=420)
        container.pack(expand=True, padx=60)

        # Logo area
        logo_area = ctk.CTkFrame(container, fg_color="transparent")
        logo_area.pack(pady=(0, 28))

        logo_canvas = tk.Canvas(
            logo_area, width=56, height=56,
            bg=BG_DARK, highlightthickness=0
        )
        logo_canvas.pack()
        draw_logo(logo_canvas, 28, 28, size=24)

        ctk.CTkLabel(
            logo_area, text="DFIS",
            font=ctk.CTkFont(family="Segoe UI", size=28, weight="bold"),
            text_color="#ffffff"
        ).pack(pady=(8, 0))

        ctk.CTkLabel(
            logo_area, text="Digital Forensics Investigation System",
            font=ctk.CTkFont(size=11),
            text_color=TEXT_DIM
        ).pack()

        ctk.CTkLabel(
            logo_area,
            text="National Investigation Agency  -  Cyber Crime Division",
            font=ctk.CTkFont(size=10),
            text_color=TEXT_FAINT
        ).pack(pady=(3, 0))

        # Login card
        card = ctk.CTkFrame(
            container, fg_color=BG_CARD,
            border_color=PURPLE_DIM, border_width=1,
            corner_radius=16
        )
        card.pack(fill="x")

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(padx=32, pady=32, fill="x")

        # Username
        ctk.CTkLabel(
            inner, text="USERNAME",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=TEXT_DIM
        ).pack(anchor="w")
        self.username_entry = ctk.CTkEntry(
            inner, placeholder_text="Enter your username",
            fg_color=BG_INPUT, border_color=PURPLE_DIM,
            text_color=TEXT_MAIN,
            placeholder_text_color=TEXT_FAINT,
            height=44, corner_radius=10
        )
        self.username_entry.pack(fill="x", pady=(6, 18))

        # Password label row
        ctk.CTkLabel(
            inner, text="PASSWORD",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=TEXT_DIM
        ).pack(anchor="w")

        # Password field + show/hide toggle
        pw_row = ctk.CTkFrame(inner, fg_color="transparent")
        pw_row.pack(fill="x", pady=(6, 6))

        self.password_entry = ctk.CTkEntry(
            pw_row, placeholder_text="Enter your password", show="*",
            fg_color=BG_INPUT, border_color=PURPLE_DIM,
            text_color=TEXT_MAIN,
            placeholder_text_color=TEXT_FAINT,
            height=44, corner_radius=10
        )
        self.password_entry.pack(side="left", fill="x", expand=True)
        self.password_entry.bind("<Return>", lambda e: self._login())

        self._pw_visible = False
        self.eye_btn = ctk.CTkButton(
            pw_row, text="Show", width=60, height=44,
            fg_color=PURPLE_DIM, hover_color=PURPLE,
            text_color=TEXT_MAIN,
            font=ctk.CTkFont(size=11),
            corner_radius=10,
            command=self._toggle_password
        )
        self.eye_btn.pack(side="left", padx=(6, 0))

        self.error_label = ctk.CTkLabel(
            inner, text="",
            font=ctk.CTkFont(size=12),
            text_color=RED
        )
        self.error_label.pack(pady=(8, 0))

        self.login_btn = ctk.CTkButton(
            inner, text="Sign In", height=46,
            fg_color=PURPLE, hover_color=PURPLE_HOVER,
            font=ctk.CTkFont(size=14, weight="bold"),
            corner_radius=10, command=self._login
        )
        self.login_btn.pack(fill="x", pady=(10, 0))

        # Footer
        ctk.CTkLabel(
            container,
            text="Authorized personnel only  -  All access is logged",
            font=ctk.CTkFont(size=10),
            text_color=TEXT_FAINT
        ).pack(pady=(16, 0))

    def _toggle_password(self):
        self._pw_visible = not self._pw_visible
        if self._pw_visible:
            self.password_entry.configure(show="")
            self.eye_btn.configure(text="Hide")
        else:
            self.password_entry.configure(show="*")
            self.eye_btn.configure(text="Show")

    def _login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            self.error_label.configure(text="Please enter both username and password.")
            return

        pw_hash = hashlib.sha256(password.encode()).hexdigest().upper()
        rows = run_query(
            "SELECT user_id, username, password_hash, role FROM users WHERE username=? AND is_active=1",
            (username,)
        )

        if not rows:
            self.error_label.configure(text="Username not found.")
            return

        row = rows[0]
        if pw_hash != row["password_hash"].upper():
            self.error_label.configure(text="Incorrect password.")
            try:
                execute_command(
                    "INSERT INTO access_logs (user_id,action,resource_accessed,ip_address,success,failure_reason) VALUES (?,?,?,?,?,?)",
                    (row["user_id"], "LOGIN", "dashboard", "127.0.0.1", 0, "Wrong password")
                )
            except Exception:
                pass
            return

        inv = run_query(
            "SELECT full_name, badge_number FROM investigators WHERE user_id=?",
            (row["user_id"],)
        )
        inv_name  = inv[0]["full_name"]    if inv else "Administrator"
        inv_badge = inv[0]["badge_number"] if inv else "ADMIN"

        session = {
            "user_id":   row["user_id"],
            "username":  row["username"],
            "role":      row["role"],
            "inv_name":  inv_name,
            "inv_badge": inv_badge,
        }

        try:
            execute_command(
                "UPDATE users SET last_login=? WHERE user_id=?",
                (datetime.now().isoformat(), row["user_id"])
            )
            execute_command(
                "INSERT INTO access_logs (user_id,action,resource_accessed,ip_address,success) VALUES (?,?,?,?,?)",
                (row["user_id"], "LOGIN", "dashboard", "127.0.0.1", 1)
            )
        except Exception:
            pass

        self.destroy()
        main_app = MainApp(session)
        main_app.mainloop()


# -------------------------------------------------------
#  MAIN APPLICATION WINDOW
# -------------------------------------------------------
class MainApp(ctk.CTk):
    def __init__(self, session: dict):
        super().__init__()
        self.session = session
        self.title("DFIS - Digital Forensics Investigation System")
        self.geometry("1280x780")
        self.minsize(1100, 650)
        self.configure(fg_color=BG_DARK)
        self._center()

        role = session["role"]
        if role == "admin":
            self.pages = [
                "Dashboard", "Cases", "New Case", "Evidence",
                "New Evidence", "Chain of Custody", "Integrity Check",
                "Reports", "User Management", "Access Logs"
            ]
        elif role == "investigator":
            self.pages = [
                "Dashboard", "Cases", "New Case", "Evidence",
                "New Evidence", "Chain of Custody", "Reports"
            ]
        else:
            self.pages = [
                "Dashboard", "Cases", "Evidence",
                "Integrity Check", "Reports"
            ]

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
        sidebar = ctk.CTkFrame(
            self, fg_color=BG_SIDEBAR, width=220,
            corner_radius=0,
            border_color=SEP_COLOR, border_width=1
        )
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_propagate(False)
        sidebar.grid_rowconfigure(2, weight=1)

        # Logo area
        logo_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        logo_frame.grid(row=0, column=0, padx=16, pady=(16, 10), sticky="ew")

        logo_canvas = tk.Canvas(
            logo_frame, width=32, height=32,
            bg=BG_SIDEBAR, highlightthickness=0
        )
        logo_canvas.pack(side="left")
        draw_logo(logo_canvas, 16, 16, size=14)

        title_frame = ctk.CTkFrame(logo_frame, fg_color="transparent")
        title_frame.pack(side="left", padx=(8, 0))
        ctk.CTkLabel(
            title_frame, text="DFIS",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#ffffff"
        ).pack(anchor="w")
        ctk.CTkLabel(
            title_frame, text="NIA Cyber Crime",
            font=ctk.CTkFont(size=9),
            text_color=TEXT_FAINT
        ).pack(anchor="w")

        # User card
        user_card = ctk.CTkFrame(
            sidebar, fg_color=PURPLE_DARK,
            border_color=PURPLE_DIM, border_width=1,
            corner_radius=10
        )
        user_card.grid(row=1, column=0, padx=12, pady=(0, 10), sticky="ew")

        uc_inner = ctk.CTkFrame(user_card, fg_color="transparent")
        uc_inner.pack(padx=12, pady=10, fill="x")

        top_row = ctk.CTkFrame(uc_inner, fg_color="transparent")
        top_row.pack(fill="x")

        # Online indicator
        online_dot = tk.Canvas(
            top_row, width=8, height=8,
            bg=PURPLE_DARK, highlightthickness=0
        )
        online_dot.pack(side="left", pady=2)
        online_dot.create_oval(1, 1, 7, 7, fill=GREEN, outline="")

        ctk.CTkLabel(
            top_row,
            text=self.session["inv_name"],
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=TEXT_MAIN
        ).pack(side="left", padx=(6, 0))

        ctk.CTkLabel(
            uc_inner, text=self.session["inv_badge"],
            font=ctk.CTkFont(size=10),
            text_color=TEXT_FAINT
        ).pack(anchor="w")

        ctk.CTkLabel(
            uc_inner, text=self.session["role"].upper(),
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=PURPLE
        ).pack(anchor="w")

        # Nav
        nav_frame = ctk.CTkScrollableFrame(
            sidebar, fg_color="transparent",
            scrollbar_button_color=BG_SIDEBAR
        )
        nav_frame.grid(row=2, column=0, padx=8, sticky="nsew")

        nav_labels = {
            "Dashboard":        "Dashboard",
            "Cases":            "Cases",
            "New Case":         "New Case",
            "Evidence":         "Evidence",
            "New Evidence":     "New Evidence",
            "Chain of Custody": "Chain of Custody",
            "Integrity Check":  "Integrity Check",
            "Reports":          "Reports",
            "User Management":  "User Management",
            "Access Logs":      "Access Logs",
        }

        self.nav_buttons = {}
        for page in self.pages:
            btn = ctk.CTkButton(
                nav_frame,
                text=nav_labels.get(page, page),
                anchor="w", height=36,
                fg_color="transparent",
                hover_color=PURPLE_DARK,
                text_color=TEXT_DIM,
                font=ctk.CTkFont(size=13),
                corner_radius=8,
                command=lambda p=page: self._show_page(p)
            )
            btn.pack(fill="x", pady=2)
            self.nav_buttons[page] = btn

        # Separator
        ctk.CTkFrame(sidebar, fg_color=SEP_COLOR, height=1).grid(
            row=3, column=0, padx=12, sticky="ew"
        )

        # Logout
        ctk.CTkButton(
            sidebar, text="Logout", anchor="w", height=36,
            fg_color="transparent", hover_color=RED_DARK,
            text_color=RED,
            font=ctk.CTkFont(size=13), corner_radius=8,
            command=self._logout
        ).grid(row=4, column=0, padx=8, pady=(6, 14), sticky="ew")

    def _show_page(self, page_name: str):
        for name, btn in self.nav_buttons.items():
            if name == page_name:
                btn.configure(fg_color=PURPLE_DIM, text_color="#ffffff")
            else:
                btn.configure(fg_color="transparent", text_color=TEXT_DIM)

        if self.current_frame:
            self.current_frame.destroy()

        kwargs = dict(
            master=self.content,
            session=self.session,
            fg_color=BG_DARK,
            corner_radius=0
        )

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
        login = LoginWindow()
        login.mainloop()


# -------------------------------------------------------
#  ENTRY POINT
# -------------------------------------------------------
if __name__ == "__main__":
    init_db()
    app = LoginWindow()
    app.mainloop()