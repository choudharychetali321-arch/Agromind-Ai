"""Optional Gemini assistant client; no key is required to run other modules."""

import json
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

from config import GEMINI_API_KEY, GEMINI_MODEL


def ask_assistant(question: str, application_context: dict, language: str = "English") -> str:
    if not GEMINI_API_KEY:
        raise RuntimeError("Gemini is not configured. Set GEMINI_API_KEY in your environment.")
    if not question.strip():
        raise ValueError("Enter a farming question.")
    prompt = (
        "You are AgroMind AI, a cautious farming information assistant. "
        "Use only the supplied application context for user-specific measurements and predictions. "
        "If data is missing, say so. Give general guidance as general guidance, not a diagnosis. "
        f"Reply in {language}.\n\n"
        f"Application context (JSON): {json.dumps(application_context, ensure_ascii=False)}\n\n"
        f"User question: {question.strip()}"
    )
    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        + quote(GEMINI_MODEL, safe="")
        + ":generateContent"
    )
    request = Request(
        url,
        data=json.dumps({"contents": [{"parts": [{"text": prompt}]}]}).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "x-goog-api-key": GEMINI_API_KEY,
        },
        method="POST",
    )
    try:
        with urlopen(request, timeout=30) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"Gemini request failed: {exc}") from exc
    try:
        return payload["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError, TypeError) as exc:
        raise RuntimeError("Gemini returned no assistant response.") from exc
