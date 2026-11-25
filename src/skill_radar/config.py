"""Settings. Everything comes from environment variables (see .env.example)."""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()  # reads .env if it exists; real environment variables always win

RAW_DIR = Path(os.getenv("RAW_DIR", "data/raw"))
API_URL = os.getenv("ARBEITNOW_URL", "https://www.arbeitnow.com/api/job-board-api")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
# "" lets the model decide. "true"/"false" forces it. Non-thinking models reject the flag.
OLLAMA_THINK = os.getenv("OLLAMA_THINK", "").strip().lower()
