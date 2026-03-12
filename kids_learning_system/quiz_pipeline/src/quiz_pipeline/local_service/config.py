from pathlib import Path



import socket

class Settings:
    LAN_MODE: bool = False
    SERVER_HOST: str = "127.0.0.1"
    SERVER_PORT: int = 8000
    ATTEMPTS_DIR: Path = Path(__file__).parent.parent.parent.parent / "work" / "attempts"
    FRONTEND_DIST_PATH: Path = Path(__file__).parent.parent.parent.parent.parent / "apps" / "quiz_shell" / "dist"

    @staticmethod
    def get_lan_ip():
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "(unavailable)"

    def apply_lan_mode(self):
        if self.LAN_MODE:
            self.SERVER_HOST = "0.0.0.0"

settings = Settings()
