from __future__ import annotations

from collections.abc import Iterable
from typing import Any


def format_timestamp(seconds: float) -> str:
    """Convert seconds to the SRT timestamp format: HH:MM:SS,mmm."""
    if seconds < 0:
        raise ValueError("El tiempo de un subtitulo no puede ser negativo.")

    total_milliseconds = round(seconds * 1000)
    total_seconds, milliseconds = divmod(total_milliseconds, 1000)
    minutes_total, seconds_part = divmod(total_seconds, 60)
    hours, minutes = divmod(minutes_total, 60)

    return f"{hours:02}:{minutes:02}:{seconds_part:02},{milliseconds:03}"


def segments_to_srt(segments: Iterable[Any]) -> str:
    lines: list[str] = []
    subtitle_number = 1

    for segment in segments:
        start = _read_segment_value(segment, "start")
        end = _read_segment_value(segment, "end")
        text = str(_read_segment_value(segment, "text")).strip()

        if not text:
            continue
        if end < start:
            raise ValueError("Un subtitulo no puede terminar antes de empezar.")

        lines.extend(
            [
                str(subtitle_number),
                f"{format_timestamp(float(start))} --> {format_timestamp(float(end))}",
                _normalize_text(text),
                "",
            ]
        )
        subtitle_number += 1

    return "\n".join(lines).strip() + ("\n" if lines else "")


def _read_segment_value(segment: Any, name: str) -> Any:
    if isinstance(segment, dict):
        return segment[name]

    return getattr(segment, name)


def _normalize_text(text: str) -> str:
    return " ".join(text.split())

