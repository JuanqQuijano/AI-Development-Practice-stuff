from __future__ import annotations

DEFAULT_LANGUAGE = "es"
DEFAULT_MODEL_SIZE = "base"
DEFAULT_DEVICE = "auto"
DEFAULT_COMPUTE_TYPE = "default"
MAX_VIDEO_SECONDS = 5 * 60

MODEL_CHOICES = ("tiny", "base", "small", "medium")
DEVICE_CHOICES = ("auto", "cpu", "cuda")
COMPUTE_TYPE_CHOICES = ("default", "int8", "float16", "float32")
VIDEO_EXTENSIONS = ("mp4", "mov", "mkv", "avi", "webm", "m4v")

