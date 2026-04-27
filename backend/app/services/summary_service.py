from dataclasses import asdict, dataclass
import json
import re
from typing import Any

import httpx

from backend.app.config import Settings


class SummaryError(RuntimeError):
    """Raised when configured summary provider fails."""


@dataclass
class StructuredNotes:
    title: str
    short_summary: str
    detailed_summary: str
    key_points: list[str]
    decisions: list[str]
    action_items: list[str]
    participants_or_speakers: list[str]
    risks_or_open_questions: list[str]
    final_notes: str
    provider: str
    fallback_used: bool
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _provider_configured(settings: Settings) -> bool:
    return bool(
        settings.llm_provider == "openai_compatible"
        and settings.llm_api_base_url
        and settings.llm_api_key
        and settings.llm_model
    )


def _split_sentences(text: str) -> list[str]:
    cleaned = re.sub(r"\s+", " ", text).strip()
    if not cleaned:
        return []
    return [sentence.strip() for sentence in re.split(r"(?<=[.!?])\s+", cleaned) if sentence.strip()]


def _as_text_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value if str(item).strip()]
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return []


def _fallback_notes(
    transcript: str,
    kazakh_translation: str,
    detected_language: str | None,
    error: str | None = None,
) -> StructuredNotes:
    source_text = kazakh_translation.strip() or transcript.strip()
    sentences = _split_sentences(source_text)
    short_summary = " ".join(sentences[:3]) if sentences else "Речь не обнаружена."
    key_points = sentences[:5] if sentences else []

    return StructuredNotes(
        title="QazScribe: протокол встречи",
        short_summary=short_summary,
        detailed_summary=short_summary,
        key_points=key_points,
        decisions=[],
        action_items=[],
        participants_or_speakers=[],
        risks_or_open_questions=[],
        final_notes=(
            "Структура подготовлена в fallback-режиме. Для качественного казахского "
            "резюме, решений и задач подключите LLM-провайдер."
        ),
        provider="fallback",
        fallback_used=True,
        error=error,
    )


def _chat_completion(settings: Settings, system_prompt: str, user_prompt: str) -> str:
    if not _provider_configured(settings):
        raise SummaryError("No LLM provider is configured")

    url = settings.llm_api_base_url.rstrip("/") + "/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.llm_api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": settings.llm_model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.2,
        "response_format": {"type": "json_object"},
    }

    try:
        response = httpx.post(
            url,
            headers=headers,
            json=payload,
            timeout=settings.llm_timeout_seconds,
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"].strip()
    except Exception as exc:
        raise SummaryError(f"Summary provider failed: {exc}") from exc


def _notes_from_provider(
    transcript: str,
    kazakh_translation: str,
    detected_language: str | None,
    settings: Settings,
) -> StructuredNotes:
    content = _chat_completion(
        settings,
        (
            "You create Kazakh structured meeting notes. Return only valid JSON "
            "with the requested fields."
        ),
        (
            "Create structured Kazakh meeting notes from this transcript and "
            "Kazakh translation. Return JSON fields: title, short_summary, "
            "detailed_summary, key_points, decisions, action_items, "
            "participants_or_speakers, risks_or_open_questions, final_notes.\n\n"
            f"Detected language: {detected_language or 'unknown'}\n\n"
            f"Original transcript:\n{transcript}\n\n"
            f"Kazakh translation:\n{kazakh_translation}"
        ),
    )
    parsed = json.loads(content)

    return StructuredNotes(
        title=str(parsed.get("title") or "QazScribe: протокол встречи"),
        short_summary=str(parsed.get("short_summary") or ""),
        detailed_summary=str(parsed.get("detailed_summary") or ""),
        key_points=_as_text_list(parsed.get("key_points")),
        decisions=_as_text_list(parsed.get("decisions")),
        action_items=_as_text_list(parsed.get("action_items")),
        participants_or_speakers=_as_text_list(parsed.get("participants_or_speakers")),
        risks_or_open_questions=_as_text_list(parsed.get("risks_or_open_questions")),
        final_notes=str(parsed.get("final_notes") or ""),
        provider=settings.llm_provider,
        fallback_used=False,
    )


def generate_structured_notes(
    transcript: str,
    kazakh_translation: str,
    detected_language: str | None,
    settings: Settings,
) -> StructuredNotes:
    if not _provider_configured(settings):
        return _fallback_notes(transcript, kazakh_translation, detected_language)

    try:
        return _notes_from_provider(transcript, kazakh_translation, detected_language, settings)
    except Exception as exc:
        return _fallback_notes(transcript, kazakh_translation, detected_language, str(exc))
