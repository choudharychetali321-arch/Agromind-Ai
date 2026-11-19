"""Application configuration loaded from environment variables."""

import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "data"
DATABASE_PATH = Path(os.getenv("AGROMIND_DATABASE_PATH", DATA_DIR / "agromind.db"))
TRAINED_MODELS_DIR = PROJECT_ROOT / "trained_models"


def _get_streamlit_secret(name: str) -> str:
    try:
        import streamlit as st

        return str(st.secrets.get(name, "")).strip()
    except FileNotFoundError:
        return ""


GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip() or _get_streamlit_secret(
    "GEMINI_API_KEY"
)
GEMINI_MODEL = (
    os.getenv("GEMINI_MODEL", "").strip()
    or _get_streamlit_secret("GEMINI_MODEL")
    or "gemini-2.0-flash"
)
