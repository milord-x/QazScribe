from dataclasses import asdict, dataclass
from typing import Any

import httpx

from backend.app.config import Settings


class TranslationError(RuntimeError):
    """Raised when configured translation provider fails."""


@dataclass
class TranslationResult:
    target_language: str
    translated_text: str
    provider: str
    fallback_used: bool
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _provider_configured(settings: Settings) -> bool:
    return bool(
        settings.llm_provider in {"openai_compatible", "ollama"}
        and settings.llm_api_base_url
        and settings.llm_model
    )


def _chat_completion(settings: Settings, system_prompt: str, user_prompt: str) -> str:
    if not _provider_configured(settings):
        raise TranslationError("No LLM provider is configured")

    url = settings.llm_api_base_url.rstrip("/") + "/chat/completions"
    headers = {"Content-Type": "application/json"}
    if settings.llm_api_key:
        headers["Authorization"] = f"Bearer {settings.llm_api_key}"
    payload = {
        "model": settings.llm_model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.2,
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
        raise TranslationError(f"Translation provider failed: {exc}") from exc


def _fallback_translation(text: str, error: str | None = None) -> TranslationResult:
    if text.strip():
        translated_text = (
            "Казахский перевод отключен в бесплатном локальном режиме. "
            "Ниже сохранен исходный распознанный текст.\n\n"
            f"{text.strip()}"
        )
    else:
        translated_text = (
            "Казахский перевод не сформирован, потому что распознанный текст пустой "
            "или речь не обнаружена."
        )

    return TranslationResult(
        target_language="kk",
        translated_text=translated_text,
        provider="fallback",
        fallback_used=True,
        error=error,
    )


def translate_to_kazakh(text: str, settings: Settings) -> TranslationResult:
    if not text.strip():
        return _fallback_translation(text)

    if not _provider_configured(settings):
        return _fallback_translation(text)

    try:
        translated_text = _chat_completion(
            settings,
            "You translate meeting and conference transcripts into clear Kazakh.",
            (
                "Translate the following transcript into Kazakh. Preserve meaning, "
                "names, numbers, and technical terms where appropriate.\n\n"
                f"{text}"
            ),
        )
        return TranslationResult(
            target_language="kk",
            translated_text=translated_text,
            provider=settings.llm_provider,
            fallback_used=False,
        )
    except TranslationError as exc:
        return _fallback_translation(text, str(exc))
