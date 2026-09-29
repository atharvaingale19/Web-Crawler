import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")


USER_AGENT = os.getenv(
    "USER_AGENT",
    "AlgoryxCrawler/1.0 (+educational crawler)"
)

DEFAULT_DEPTH = int(os.getenv("DEFAULT_DEPTH", "2"))
DEFAULT_DELAY = float(os.getenv("DEFAULT_DELAY", "1.0"))
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "10"))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))

OUTPUT_DIR = BASE_DIR / "output"
LOG_DIR = BASE_DIR / "logs"

OUTPUT_DIR.mkdir(exist_ok=True)
LOG_DIR.mkdir(exist_ok=True)