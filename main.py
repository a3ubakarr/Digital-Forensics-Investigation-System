from backend.database import init_db
from frontend.app import LoginWindow

if __name__ == "__main__":
    init_db()
    LoginWindow().mainloop()