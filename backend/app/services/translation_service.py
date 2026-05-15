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
        settings.llm_provider in {"gemini", "openai_compatible", "ollama"}
        and settings.llm_api_base_url
        and settings.llm_model
        and (settings.llm_provider != "gemini" or settings.llm_api_key)
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


LANGUAGE_NAMES = {
    "kk": "Kazakh",
    "ky": "Kyrgyz",
}


def _target_language(source_language: str | None) -> str:
    normalized = (source_language or "").strip().lower()
    if normalized.startswith("kk") or normalized == "kazakh":
        return "ky"
    return "kk"


def _fallback_translation(
    text: str,
    target_language: str = "kk",
    error: str | None = None,
) -> TranslationResult:
    if text.strip():
        translated_text = text.strip()
    else:
        language_name = "Казахский" if target_language == "kk" else "Кыргызский"
        translated_text = (
            f"{language_name} перевод не сформирован, потому что распознанный текст пустой "
            "или речь не обнаружена."
        )

    return TranslationResult(
        target_language=target_language,
        translated_text=translated_text,
        provider="fallback",
        fallback_used=True,
        error=error,
    )


def translate_transcript(
    text: str,
    settings: Settings,
    source_language: str | None = None,
) -> TranslationResult:
    target_language = _target_language(source_language)
    if not text.strip():
        return _fallback_translation(text, target_language)

    if not _provider_configured(settings):
        return _fallback_translation(text, target_language)

    target_name = LANGUAGE_NAMES[target_language]
    try:
        translated_text = _chat_completion(
            settings,
            f"You translate meeting and conference transcripts into clear {target_name}.",
            (
                f"Translate the following transcript into {target_name}. Preserve meaning, "
                "names, numbers, and technical terms where appropriate. Return only "
                f"the translated {target_name} text without explanations or notes.\n\n"
                f"{text}"
            ),
        )
        return TranslationResult(
            target_language=target_language,
            translated_text=translated_text,
            provider=settings.llm_provider,
            fallback_used=False,
        )
    except TranslationError as exc:
        return _fallback_translation(text, target_language, str(exc))


def translate_to_kazakh(text: str, settings: Settings) -> TranslationResult:
    return translate_transcript(text, settings, "ky")
