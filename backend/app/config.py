import os
from pathlib import Path

try:
    from dotenv import load_dotenv

    _root = Path(__file__).resolve().parents[2]
    load_dotenv(_root / ".env")
    load_dotenv(_root / "backend" / ".env")
except ImportError:  # pragma: no cover
    pass


def setting(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()


MONGODB_URI = setting("MONGODB_URI")
MONGODB_DB_NAME = setting("MONGODB_DB_NAME", "jyotish_studio")
API_HOST = setting("API_HOST", "127.0.0.1")
API_PORT = int(setting("API_PORT", "8800"))
FRONTEND_ORIGINS = [x.strip() for x in setting("FRONTEND_ORIGINS", "http://localhost:4000,http://127.0.0.1:4000").split(",") if x.strip()]
SWISSEPH_EPHE_PATH = setting("SWISSEPH_EPHE_PATH")
SESSION_HTTPS_ONLY = setting("SESSION_HTTPS_ONLY", "false").lower() == "true"
AI_PROVIDER = setting("AI_PROVIDER", "gemini")
AI_MODEL = setting("AI_MODEL", "gemini-3.6-flash")
GEMINI_API_KEY = setting("GEMINI_API_KEY") or setting("AI_API_KEY") or setting("GOOGLE_API_KEY")
DATA_ENCRYPTION_KEY = setting("DATA_ENCRYPTION_KEY")
