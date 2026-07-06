from __future__ import annotations

from dataclasses import dataclass

import httpx

from backend.config.settings import get_settings


@dataclass(frozen=True)
class GeminiChatConfig:
    api_key: str
    model: str
    base_url: str
    app_name: str
    site_url: str


def get_gemini_config() -> GeminiChatConfig:
    settings = get_settings()
    return GeminiChatConfig(
        api_key=settings.gemini_api_key.strip(),
        model=settings.gemini_model.strip() or "gemini-1.5-flash",
        base_url="https://generativelanguage.googleapis.com/v1beta",
        app_name=settings.gemini_app_name.strip() or "Estate AI",
        site_url=settings.gemini_site_url.strip() or "http://localhost:5173",
    )


def build_system_prompt(market_context: str) -> str:
    return (
        "Tu es un assistant d'analyse du marche immobilier.\n"
        "Reponds en texte brut, en francais, sans Markdown.\n"
        "Sois concret, precis et bref.\n"
        "N'invente pas de chiffres.\n\n"
        f"CONTEXTE MARCHE:\n{market_context}"
    )


def normalize_chat_messages(messages: list[dict]) -> list[dict]:
    normalized: list[dict] = []
    for message in messages:
        role = message.get("role")
        content = message.get("content")
        if role == "user" and content:
            normalized.append({"role": "user", "parts": [{"text": str(content)}]})
        elif role in {"assistant", "model"} and content:
            normalized.append({"role": "model", "parts": [{"text": str(content)}]})
    return normalized


def extract_gemini_text(response_payload: dict) -> str:
    candidates = response_payload.get("candidates") or []
    if not candidates:
        raise ValueError("Gemini response did not return any candidates.")

    content = candidates[0].get("content") or {}
    parts = content.get("parts") or []
    text = "".join(part.get("text", "") for part in parts if isinstance(part, dict))
    if not text.strip():
        raise ValueError("Gemini response was empty.")
    return text.strip()


def call_gemini_chat(messages: list[dict], market_context: str, *, client: httpx.Client | None = None) -> str:
    config = get_gemini_config()
    if not config.api_key:
        raise RuntimeError("GEMINI_API_KEY is not configured.")

    request_client = client or httpx.Client(timeout=60.0)
    close_client = client is None
    try:
        payload = {
            "systemInstruction": {"parts": [{"text": build_system_prompt(market_context)}]},
            "contents": normalize_chat_messages(messages),
            "generationConfig": {"temperature": 0.3, "maxOutputTokens": 512},
        }
        response = request_client.post(
            f"{config.base_url}/models/{config.model}:generateContent",
            headers={
                "Content-Type": "application/json",
                "x-goog-api-key": config.api_key,
                "X-Goog-User-Project": config.app_name,
                "HTTP-Referer": config.site_url,
            },
            json=payload,
        )
        response.raise_for_status()
        return extract_gemini_text(response.json())
    finally:
        if close_client:
            request_client.close()
