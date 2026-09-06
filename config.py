"""
GoalMate Configuration Module
Handles environment variables, paths, and default model settings.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Base Directory
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Load environment variables from .env if present
load_dotenv(BASE_DIR / ".env")

# Database Path
DB_PATH = os.getenv("GOALMATE_DB_PATH", str(DATA_DIR / "goalmate.db"))

# LLM Providers & Keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "") or os.getenv("GOOGLE_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Default Models
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# Assistant Personality & Settings
ASSISTANT_NAME = "GoalMate"
MAX_HISTORY_TURNS = 10
