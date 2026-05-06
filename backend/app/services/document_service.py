from datetime import datetime
from html import escape
import json
from pathlib import Path
import textwrap
from typing import Any

from docx import Document
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer


class DocumentGenerationError(RuntimeError):
    """Raised when result documents cannot be generated."""


def _text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, list):
        return "\n".join(f"- {item}" for item in value)
    return str(value)


def _section(title: str, body: Any) -> str:
    content = _text(body).strip() or "Not available."
    return f"\n{title}\n{'=' * len(title)}\n{content}\n"


def _font_name() -> str:
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/TTF/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/liberation/LiberationSans-Regular.ttf",
    ]
    for candidate in candidates:
        path = Path(candidate)
        if path.exists():
            font_name = path.stem
            if font_name not in pdfmetrics.getRegisteredFontNames():
                pdfmetrics.registerFont(TTFont(font_name, str(path)))
            return font_name
    return "Helvetica"


def _build_payload(
    task_id: str,
    detected_language: str | None,
    transcript: dict[str, Any],
    translation: dict[str, Any],
    summary: dict[str, Any],
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    metadata = metadata or {}
    segments = _subtitle_segments(transcript)
    speaker_names = sorted({segment.get("speaker", "Спикер 1") for segment in segments})
    duration = metadata.get("recording_duration_seconds") or _recording_duration(segments)
    return {
        "title": "Qtranscript: конспект записи",
        "task_id": task_id,
        "processed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "recording_started_at": metadata.get("recording_started_at") or "unknown",
        "recording_duration": _format_duration(duration),
        "speaker_count": len(speaker_names) if speaker_names else 0,
        "speaker_names": speaker_names,
        "detected_language": detected_language or transcript.get("detected_language") or "unknown",
        "original_transcript": transcript.get("full_transcript") or "",
        "speaker_transcript": _speaker_transcript(segments),
        "kazakh_translation": translation.get("translated_text") or "",
        "short_summary": summary.get("short_summary") or "",
        "detailed_summary": summary.get("detailed_summary") or "",
        "key_points": summary.get("key_points") or [],
        "decisions": summary.get("decisions") or [],
        "action_items": summary.get("action_items") or [],
        "participants_or_speakers": summary.get("participants_or_speakers") or [],
        "risks_or_open_questions": summary.get("risks_or_open_questions") or [],
        "final_notes": summary.get("final_notes") or "",
    }


def _plain_text(payload: dict[str, Any]) -> str:
    parts = [
        payload["title"],
        f"Номер задачи: {payload['task_id']}",
        f"Время начала записи: {payload['recording_started_at']}",
        f"Длительность записи: {payload['recording_duration']}",
        f"Количество спикеров: {payload['speaker_count']}",
        f"Обработано: {payload['processed_at']}",
        f"Определённый язык: {payload['detected_language']}",
        _section("Полная расшифровка по спикерам", payload["speaker_transcript"]),
        _section("Основной полный конспект", payload["detailed_summary"]),
        _section("Краткое резюме", payload["short_summary"]),
        _section("Ключевые пункты", payload["key_points"]),
        _section("Решения", payload["decisions"]),
        _section("Задачи", payload["action_items"]),
        _section("Казахская версия", payload["kazakh_translation"]),
        _section("Финальные заметки", payload["final_notes"]),
    ]
    return "\n".join(parts).strip() + "\n"


def _html(payload: dict[str, Any]) -> str:
    def list_or_paragraph(value: Any) -> str:
        if isinstance(value, list):
            if not value:
                return "<p>Not available.</p>"
            return "<ul>" + "".join(f"<li>{escape(str(item))}</li>" for item in value) + "</ul>"
        return f"<p>{escape(_text(value).strip() or 'Not available.')}</p>"

    sections = [
        ("Полная расшифровка по спикерам", payload["speaker_transcript"]),
        ("Основной полный конспект", payload["detailed_summary"]),
        ("Краткое резюме", payload["short_summary"]),
        ("Ключевые пункты", payload["key_points"]),
        ("Решения", payload["decisions"]),
        ("Задачи", payload["action_items"]),
        ("Казахская версия", payload["kazakh_translation"]),
        ("Финальные заметки", payload["final_notes"]),
    ]
    body = "\n".join(
        f"<section><h2>{escape(title)}</h2>{list_or_paragraph(value)}</section>"
        for title, value in sections
    )
    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <title>{escape(payload["title"])}</title>
    <style>
      body {{ font-family: Arial, sans-serif; line-height: 1.5; margin: 32px; color: #18202a; }}
      h1 {{ margin-bottom: 8px; }}
      h2 {{ margin-top: 28px; border-bottom: 1px solid #d9dee7; padding-bottom: 6px; }}
      p, li {{ white-space: pre-wrap; }}
      .meta {{ color: #667085; }}
    </style>
  </head>
  <body>
    <h1>{escape(payload["title"])}</h1>
    <p class="meta">Номер задачи: {escape(payload["task_id"])}</p>
    <p class="meta">Время начала записи: {escape(payload["recording_started_at"])}</p>
    <p class="meta">Длительность записи: {escape(payload["recording_duration"])}</p>
    <p class="meta">Количество спикеров: {escape(str(payload["speaker_count"]))}</p>
    <p class="meta">Обработано: {escape(payload["processed_at"])}</p>
    <p class="meta">Определённый язык: {escape(payload["detected_language"])}</p>
    {body}
  </body>
</html>
"""


def _timestamp_srt(seconds: float) -> str:
    milliseconds = int(round(seconds * 1000))
    hours, remainder = divmod(milliseconds, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    secs, millis = divmod(remainder, 1000)
    return f"{hours:02}:{minutes:02}:{secs:02},{millis:03}"


def _timestamp_vtt(seconds: float) -> str:
    return _timestamp_srt(seconds).replace(",", ".")


def _subtitle_segments(transcript: dict[str, Any]) -> list[dict[str, Any]]:
    segments = transcript.get("segments") or []
    normalized = []
    for index, segment in enumerate(segments, start=1):
        text = str(segment.get("text") or "").strip()
        if not text:
            continue
        start = float(segment.get("start") or 0)
        end = float(segment.get("end") or max(start + 1, index))
        normalized.append(
            {
                "start": start,
                "end": max(end, start + 0.5),
                "text": text,
                "speaker": str(segment.get("speaker") or "Спикер 1"),
            }
        )
    if normalized:
        return normalized

    full_text = str(transcript.get("full_transcript") or "").strip()
    return [{"start": 0.0, "end": 3.0, "text": full_text, "speaker": "Спикер 1"}] if full_text else []


def _recording_duration(segments: list[dict[str, Any]]) -> float:
    if not segments:
        return 0.0
    return max(float(segment.get("end") or 0) for segment in segments)


def _format_duration(seconds: float | int | None) -> str:
    total_seconds = int(round(float(seconds or 0)))
    hours, remainder = divmod(total_seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    if hours:
        return f"{hours:02}:{minutes:02}:{secs:02}"
    return f"{minutes:02}:{secs:02}"


def _speaker_transcript(segments: list[dict[str, Any]]) -> str:
    lines = []
    for segment in segments:
        lines.append(
            f"[{_timestamp_vtt(float(segment['start']))}] {segment.get('speaker', 'Спикер 1')}: {segment['text']}"
        )
    return "\n".join(lines)


def _srt(transcript: dict[str, Any]) -> str:
    blocks = []
    for index, segment in enumerate(_subtitle_segments(transcript), start=1):
        blocks.append(
            "\n".join(
                [
                    str(index),
                    f"{_timestamp_srt(segment['start'])} --> {_timestamp_srt(segment['end'])}",
                    f"{segment.get('speaker', 'Спикер 1')}: {segment['text']}",
                ]
            )
        )
    return "\n\n".join(blocks).strip() + "\n"


def _vtt(transcript: dict[str, Any]) -> str:
    blocks = ["WEBVTT"]
    for segment in _subtitle_segments(transcript):
        blocks.append(
            "\n".join(
                [
                    f"{_timestamp_vtt(segment['start'])} --> {_timestamp_vtt(segment['end'])}",
                    f"{segment.get('speaker', 'Спикер 1')}: {segment['text']}",
                ]
            )
        )
    return "\n\n".join(blocks).strip() + "\n"


def _write_docx(path: Path, payload: dict[str, Any]) -> None:
    document = Document()
    document.add_heading(payload["title"], level=0)
    document.add_paragraph(f"Номер задачи: {payload['task_id']}")
    document.add_paragraph(f"Время начала записи: {payload['recording_started_at']}")
    document.add_paragraph(f"Длительность записи: {payload['recording_duration']}")
    document.add_paragraph(f"Количество спикеров: {payload['speaker_count']}")
    document.add_paragraph(f"Обработано: {payload['processed_at']}")
    document.add_paragraph(f"Определённый язык: {payload['detected_language']}")

    for title, key in [
        ("Полная расшифровка по спикерам", "speaker_transcript"),
        ("Основной полный конспект", "detailed_summary"),
        ("Краткое резюме", "short_summary"),
        ("Ключевые пункты", "key_points"),
        ("Решения", "decisions"),
        ("Задачи", "action_items"),
        ("Казахская версия", "kazakh_translation"),
        ("Финальные заметки", "final_notes"),
    ]:
        document.add_heading(title, level=1)
        value = payload[key]
        if isinstance(value, list):
            if not value:
                document.add_paragraph("Not available.")
            for item in value:
                document.add_paragraph(str(item), style="List Bullet")
        else:
            document.add_paragraph(_text(value).strip() or "Not available.")

    document.save(path)


def _write_pdf(path: Path, payload: dict[str, Any]) -> None:
    font_name = _font_name()
    styles = getSampleStyleSheet()
    normal = ParagraphStyle(
        "QtranscriptNormal",
        parent=styles["Normal"],
        fontName=font_name,
        fontSize=10,
        leading=14,
    )
    heading = ParagraphStyle(
        "QtranscriptHeading",
        parent=styles["Heading2"],
        fontName=font_name,
        fontSize=14,
        leading=18,
        spaceBefore=12,
        spaceAfter=6,
    )
    title = ParagraphStyle(
        "QtranscriptTitle",
        parent=styles["Title"],
        fontName=font_name,
        fontSize=18,
        leading=22,
    )

    doc = SimpleDocTemplate(
        str(path),
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
    )
    story = [
        Paragraph(escape(payload["title"]), title),
        Paragraph(escape(f"Номер задачи: {payload['task_id']}"), normal),
        Paragraph(escape(f"Время начала записи: {payload['recording_started_at']}"), normal),
        Paragraph(escape(f"Длительность записи: {payload['recording_duration']}"), normal),
        Paragraph(escape(f"Количество спикеров: {payload['speaker_count']}"), normal),
        Paragraph(escape(f"Обработано: {payload['processed_at']}"), normal),
        Paragraph(escape(f"Определённый язык: {payload['detected_language']}"), normal),
        Spacer(1, 8),
    ]

    for section_title, key in [
        ("Полная расшифровка по спикерам", "speaker_transcript"),
        ("Основной полный конспект", "detailed_summary"),
        ("Краткое резюме", "short_summary"),
        ("Ключевые пункты", "key_points"),
        ("Решения", "decisions"),
        ("Задачи", "action_items"),
        ("Казахская версия", "kazakh_translation"),
        ("Финальные заметки", "final_notes"),
    ]:
        story.append(Paragraph(escape(section_title), heading))
        text = _text(payload[key]).strip() or "Not available."
        for chunk in textwrap.wrap(text, width=180, replace_whitespace=False) or [text]:
            story.append(Paragraph(escape(chunk), normal))

    doc.build(story)


def generate_documents(
    task_id: str,
    output_dir: Path,
    detected_language: str | None,
    transcript: dict[str, Any],
    translation: dict[str, Any],
    summary: dict[str, Any],
    metadata: dict[str, Any] | None = None,
) -> dict[str, Path]:
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        payload = _build_payload(task_id, detected_language, transcript, translation, summary, metadata)

        paths = {
            "txt": output_dir / "qazscribe_result.txt",
            "srt": output_dir / "qazscribe_result.srt",
            "vtt": output_dir / "qazscribe_result.vtt",
            "json": output_dir / "qazscribe_result.json",
            "html": output_dir / "qazscribe_result.html",
            "docx": output_dir / "qazscribe_result.docx",
            "pdf": output_dir / "qazscribe_result.pdf",
        }

        paths["txt"].write_text(_plain_text(payload), encoding="utf-8")
        paths["srt"].write_text(_srt(transcript), encoding="utf-8")
        paths["vtt"].write_text(_vtt(transcript), encoding="utf-8")
        paths["json"].write_text(
            json.dumps(
                {
                    "task_id": task_id,
                    "detected_language": detected_language,
                    "transcript": transcript,
                    "translation": translation,
                    "summary": summary,
                    "metadata": metadata or {},
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        paths["html"].write_text(_html(payload), encoding="utf-8")
        _write_docx(paths["docx"], payload)
        _write_pdf(paths["pdf"], payload)
        return paths
    except Exception as exc:
        raise DocumentGenerationError(f"Document generation failed: {exc}") from exc
