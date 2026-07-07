from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx

from backend.app.database import SessionLocal
from backend.app.models import ExternalContextSummary, PropertyTrain, ScrapedMarketTrend
from backend.config.settings import get_settings


@dataclass(frozen=True)
class ChatProviderResult:
    provider: str
    answer: str


def get_chat_context() -> str:
    db = SessionLocal()
    try:
        properties = db.query(PropertyTrain).all()
        if not properties:
            return "Aucune donnee immobiliere n'est disponible pour le moment."

        prices = [float(row.sale_price) for row in properties if row.sale_price is not None]
        top_contexts = (
            db.query(ExternalContextSummary)
            .order_by(ExternalContextSummary.created_at.desc())
            .limit(2)
            .all()
        )
        trends = (
            db.query(ScrapedMarketTrend)
            .order_by(ScrapedMarketTrend.created_at.desc())
            .limit(3)
            .all()
        )

        lines = [
            f"Biens disponibles: {len(properties)}",
            f"Prix moyen observe: {sum(prices) / len(prices):.2f}" if prices else "Prix moyen observe: indisponible",
        ]
        for summary in top_contexts:
            if summary.summary_text:
                lines.append(f"Contexte externe: {summary.summary_text}")
        for trend in trends:
            description = trend.description or trend.trend or "Signal disponible"
            lines.append(f"Tendance: {trend.city or 'Unknown'} - {description}")
        return "\n".join(lines)
    finally:
        db.close()


def normalize_messages(messages: list[dict[str, Any]]) -> list[dict[str, str]]:
    normalized: list[dict[str, str]] = []
    for message in messages:
        role = str(message.get("role", "")).strip().lower()
        content = str(message.get("content", "")).strip()
        if not content:
            continue
        if role in {"user", "assistant"}:
            normalized.append({"role": role, "content": content})
    return normalized[-12:]


def build_prompt(messages: list[dict[str, str]], context: str) -> str:
    transcript = []
    for message in messages:
        label = "Utilisateur" if message["role"] == "user" else "Assistant"
        transcript.append(f"{label}: {message['content']}")

    return (
        "Tu es un assistant immobilier utile, concret et bref.\n"
        "Tu réponds en français simple, sans markdown inutile.\n"
        "Tu t'appuies d'abord sur le contexte fourni.\n"
        "Si une information manque, dis-le clairement.\n\n"
        f"CONTEXTE:\n{context}\n\n"
        f"CONVERSATION:\n" + "\n".join(transcript)
    )


def _extract_openai_text(payload: dict[str, Any]) -> str:
    choices = payload.get("choices") or []
    if not choices:
        raise ValueError("OpenRouter response did not return any choices.")
    message = choices[0].get("message") or {}
    content = message.get("content") or ""
    if not str(content).strip():
        raise ValueError("OpenRouter response was empty.")
    return str(content).strip()


def _extract_gemini_text(payload: dict[str, Any]) -> str:
    candidates = payload.get("candidates") or []
    if not candidates:
        raise ValueError("Gemini response did not return any candidates.")
    content = candidates[0].get("content") or {}
    parts = content.get("parts") or []
    text = "".join(part.get("text", "") for part in parts if isinstance(part, dict))
    if not text.strip():
        raise ValueError("Gemini response was empty.")
    return text.strip()


def _call_gemini(prompt: str, *, client: httpx.Client) -> str:
    settings = get_settings()
    if not settings.gemini_api_key.strip():
        raise RuntimeError("GEMINI_API_KEY is not configured.")

    response = client.post(
        f"https://generativelanguage.googleapis.com/v1beta/models/{settings.gemini_model}:generateContent",
        headers={
            "Content-Type": "application/json",
            "x-goog-api-key": settings.gemini_api_key.strip(),
            "X-Goog-User-Project": settings.gemini_app_name.strip() or "Estate AI",
            "HTTP-Referer": settings.gemini_site_url.strip() or "http://localhost:5173",
        },
        json={
            "systemInstruction": {
                "parts": [{"text": "Réponds en français, de façon concise et utile."}],
            },
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.3, "maxOutputTokens": 512},
        },
        timeout=60.0,
    )
    response.raise_for_status()
    return _extract_gemini_text(response.json())


def _call_openrouter(prompt: str, *, client: httpx.Client) -> str:
    settings = get_settings()
    if not settings.openrouter_api_key.strip():
        raise RuntimeError("OPENROUTER_API_KEY is not configured.")

    response = client.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {settings.openrouter_api_key.strip()}",
            "Content-Type": "application/json",
            "HTTP-Referer": settings.openrouter_site_url.strip() or "http://localhost:5173",
            "X-Title": settings.openrouter_app_name.strip() or "Estate AI",
        },
        json={
            "model": settings.openrouter_model.strip() or "openai/gpt-4o-mini",
            "messages": [
                {"role": "system", "content": "Réponds en français, de manière utile et concise."},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.3,
            "max_tokens": 512,
        },
        timeout=60.0,
    )
    response.raise_for_status()
    return _extract_openai_text(response.json())


def _local_answer(messages: list[dict[str, str]], context: str) -> str:
    user_messages = [message["content"] for message in messages if message["role"] == "user"]
    latest_question = user_messages[-1] if user_messages else ""
    lower_question = latest_question.lower()

    if any(keyword in lower_question for keyword in ["quartier", "cher", "prix", "market", "marche"]):
        return (
            "Réponse locale: les quartiers les plus chers sont généralement ceux avec le meilleur prix moyen "
            "dans les données disponibles. "
            "Contexte disponible: " + context
        )

    return (
        "Je n'ai pas pu joindre Gemini ni OpenRouter pour l'instant. "
        "Voici le contexte local disponible: " + context
    )


def generate_chat_answer(messages: list[dict[str, Any]]) -> ChatProviderResult:
    normalized_messages = normalize_messages(messages)
    if not normalized_messages:
        return ChatProviderResult(provider="local", answer="Veuillez écrire un message pour commencer.")

    context = get_chat_context()
    prompt = build_prompt(normalized_messages, context)

    with httpx.Client(timeout=60.0) as client:
        try:
            return ChatProviderResult(provider="gemini", answer=_call_gemini(prompt, client=client))
        except Exception:
            pass

        try:
            return ChatProviderResult(provider="openrouter", answer=_call_openrouter(prompt, client=client))
        except Exception:
            pass

    return ChatProviderResult(provider="local", answer=_local_answer(normalized_messages, context))
