from backend.app import chat_service


def test_generate_chat_answer_uses_local_fallback(monkeypatch):
    monkeypatch.setattr(chat_service, "get_chat_context", lambda: "Contexte local")
    monkeypatch.setattr(chat_service, "_call_gemini", lambda prompt, client: (_ for _ in ()).throw(RuntimeError("boom")))
    monkeypatch.setattr(chat_service, "_call_openrouter", lambda prompt, client: (_ for _ in ()).throw(RuntimeError("boom")))

    result = chat_service.generate_chat_answer([{"role": "user", "content": "Quel quartier est le plus cher ?"}])

    assert result.provider == "local"
    assert "Contexte local" in result.answer


def test_generate_chat_answer_prefers_gemini(monkeypatch):
    monkeypatch.setattr(chat_service, "get_chat_context", lambda: "Contexte local")
    monkeypatch.setattr(chat_service, "_call_gemini", lambda prompt, client: "Réponse Gemini")

    result = chat_service.generate_chat_answer([{"role": "user", "content": "Bonjour"}])

    assert result.provider == "gemini"
    assert result.answer == "Réponse Gemini"


def test_generate_chat_answer_falls_back_to_openrouter(monkeypatch):
    monkeypatch.setattr(chat_service, "get_chat_context", lambda: "Contexte local")
    monkeypatch.setattr(chat_service, "_call_gemini", lambda prompt, client: (_ for _ in ()).throw(RuntimeError("boom")))
    monkeypatch.setattr(chat_service, "_call_openrouter", lambda prompt, client: "Réponse OpenRouter")

    result = chat_service.generate_chat_answer([{"role": "user", "content": "Bonjour"}])

    assert result.provider == "openrouter"
    assert result.answer == "Réponse OpenRouter"
