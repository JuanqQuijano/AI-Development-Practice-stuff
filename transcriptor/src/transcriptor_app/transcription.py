from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from transcriptor_app.config import (
    DEFAULT_COMPUTE_TYPE,
    DEFAULT_DEVICE,
    DEFAULT_LANGUAGE,
    DEFAULT_MODEL_SIZE,
    MAX_VIDEO_SECONDS,
)

ProgressCallback = Callable[[str], None]


@dataclass(frozen=True)
class TranscriptionSegment:
    start: float
    end: float
    text: str


class ToolMissingError(RuntimeError):
    pass


class VideoTooLongError(ValueError):
    pass


def transcribe_video(
    video_path: str | Path,
    *,
    model_size: str = DEFAULT_MODEL_SIZE,
    language: str | None = DEFAULT_LANGUAGE,
    device: str = DEFAULT_DEVICE,
    compute_type: str = DEFAULT_COMPUTE_TYPE,
    max_duration_seconds: int = MAX_VIDEO_SECONDS,
    progress_callback: ProgressCallback | None = None,
) -> list[TranscriptionSegment]:
    video_path = Path(video_path)
    duration = probe_duration(video_path)

    if duration is not None and duration > max_duration_seconds:
        raise VideoTooLongError(
            f"El video dura {duration / 60:.1f} minutos. El limite es de {max_duration_seconds // 60} minutos."
        )

    with tempfile.TemporaryDirectory(prefix="transcriptor-local-") as temp_dir:
        audio_path = Path(temp_dir) / "audio.wav"

        _report(progress_callback, "Extrayendo audio con FFmpeg...")
        extract_audio(video_path, audio_path)

        _report(progress_callback, f"Cargando modelo Whisper '{model_size}'...")
        from faster_whisper import WhisperModel

        model = WhisperModel(model_size, device=device, compute_type=compute_type)

        _report(progress_callback, "Transcribiendo audio...")
        segment_iterator, _info = model.transcribe(
            str(audio_path),
            language=language or None,
            beam_size=5,
            vad_filter=True,
        )

        segments = [
            TranscriptionSegment(
                start=float(segment.start),
                end=float(segment.end),
                text=segment.text.strip(),
            )
            for segment in segment_iterator
            if segment.text.strip()
        ]

    _report(progress_callback, "Transcripcion terminada.")
    return segments


def extract_audio(video_path: str | Path, audio_path: str | Path) -> None:
    ffmpeg_path = _resolve_tool("ffmpeg")
    if not ffmpeg_path:
        raise ToolMissingError(
            "FFmpeg no esta instalado o no esta disponible para esta sesion. "
            "Si lo acabas de instalar, cierra y vuelve a abrir la app."
        )

    command = [
        ffmpeg_path,
        "-y",
        "-i",
        str(video_path),
        "-vn",
        "-acodec",
        "pcm_s16le",
        "-ac",
        "1",
        "-ar",
        "16000",
        str(audio_path),
    ]
    completed = subprocess.run(command, capture_output=True, text=True, check=False)

    if completed.returncode != 0:
        raise RuntimeError(
            "FFmpeg no pudo extraer el audio del video.\n\n"
            + (completed.stderr.strip() or completed.stdout.strip())
        )


def probe_duration(video_path: str | Path) -> float | None:
    ffprobe_path = _resolve_tool("ffprobe")
    if not ffprobe_path:
        return None

    command = [
        ffprobe_path,
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        str(video_path),
    ]
    completed = subprocess.run(command, capture_output=True, text=True, check=False)

    if completed.returncode != 0:
        return None

    try:
        return float(completed.stdout.strip())
    except ValueError:
        return None


def _resolve_tool(name: str) -> str | None:
    current_path_match = shutil.which(name)
    if current_path_match:
        return current_path_match

    executable = f"{name}.exe" if os.name == "nt" else name
    for directory in _candidate_tool_directories():
        candidate = directory / executable
        if candidate.exists():
            return str(candidate)

    return None


def _candidate_tool_directories() -> list[Path]:
    directories: list[Path] = []

    for path_value in _path_values():
        directories.extend(Path(entry) for entry in path_value.split(os.pathsep) if entry)

    if os.name == "nt":
        local_app_data = os.environ.get("LOCALAPPDATA")
        if local_app_data:
            winget_packages = Path(local_app_data) / "Microsoft" / "WinGet" / "Packages"
            directories.extend(path.parent for path in winget_packages.glob("Gyan.FFmpeg*/**/ffmpeg.exe"))

        program_files = [os.environ.get("ProgramFiles"), os.environ.get("ProgramFiles(x86)")]
        for folder in program_files:
            if folder:
                directories.extend(
                    [
                        Path(folder) / "ffmpeg" / "bin",
                        Path(folder) / "Gyan" / "ffmpeg" / "bin",
                    ]
                )

    seen: set[Path] = set()
    unique_directories: list[Path] = []
    for directory in directories:
        expanded = Path(os.path.expandvars(str(directory)))
        if expanded not in seen:
            seen.add(expanded)
            unique_directories.append(expanded)

    return unique_directories


def _path_values() -> list[str]:
    values = [os.environ.get("PATH", "")]

    if os.name == "nt":
        try:
            import winreg

            registry_locations = [
                (winreg.HKEY_CURRENT_USER, r"Environment"),
                (
                    winreg.HKEY_LOCAL_MACHINE,
                    r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment",
                ),
            ]
            for hive, key_path in registry_locations:
                with winreg.OpenKey(hive, key_path) as key:
                    values.append(str(winreg.QueryValueEx(key, "Path")[0]))
        except OSError:
            pass

    return values


def _report(callback: ProgressCallback | None, message: str) -> None:
    if callback:
        callback(message)

