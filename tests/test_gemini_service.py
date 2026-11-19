import json
from io import BytesIO

from services import gemini_service


def test_gemini_key_is_sent_in_header_not_url(monkeypatch):
    observed = {}

    def fake_urlopen(request, timeout):
        observed["url"] = request.full_url
        observed["key"] = request.get_header("X-goog-api-key")
        observed["timeout"] = timeout
        return BytesIO(
            json.dumps(
                {"candidates": [{"content": {"parts": [{"text": "Test reply"}]}}]}
            ).encode("utf-8")
        )

    monkeypatch.setattr(gemini_service, "GEMINI_API_KEY", "test-secret")
    monkeypatch.setattr(gemini_service, "urlopen", fake_urlopen)

    response = gemini_service.ask_assistant("How should I plan irrigation?", {})

    assert response == "Test reply"
    assert "test-secret" not in observed["url"]
    assert observed["key"] == "test-secret"
    assert observed["timeout"] == 30
