from pathlib import Path
import socket

class Settings:
    LAN_MODE: bool = False
    SERVER_HOST: str = "127.0.0.1"
    SERVER_PORT: int = 8000

    # Base paths (resolved relative to this file's location)
    _BASE: Path = Path(__file__).resolve().parent.parent.parent.parent  # …/quiz_pipeline

    ATTEMPTS_DIR: Path = _BASE / "work" / "attempts"
    ARCHIVED_DIR: Path = _BASE / "work" / "archived"
    GENERATED_DIR: Path = _BASE / "work" / "generated"
    INCOMING_DIR: Path = _BASE / "work" / "incoming"

    # Frontend paths
    _FRONTEND_ROOT: Path = _BASE.parent / "apps" / "quiz_shell"
    FRONTEND_DIST_PATH: Path = _FRONTEND_ROOT / "dist"
    PUBLIC_DIR: Path = _FRONTEND_ROOT / "public"
    MANIFEST_PATH: Path = _FRONTEND_ROOT / "public" / "quiz_manifest.json"

    def __post_init__(self):
        self.ARCHIVED_DIR.mkdir(parents=True, exist_ok=True)

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
# Ensure archived dir exists on startup
settings.ARCHIVED_DIR.mkdir(parents=True, exist_ok=True)

