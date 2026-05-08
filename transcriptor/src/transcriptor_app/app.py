from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import streamlit as st

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from transcriptor_app.config import (  # noqa: E402
    COMPUTE_TYPE_CHOICES,
    DEFAULT_COMPUTE_TYPE,
    DEFAULT_DEVICE,
    DEFAULT_LANGUAGE,
    DEFAULT_MODEL_SIZE,
    DEVICE_CHOICES,
    MAX_VIDEO_SECONDS,
    MODEL_CHOICES,
    VIDEO_EXTENSIONS,
)
from transcriptor_app.srt import segments_to_srt  # noqa: E402
from transcriptor_app.transcription import (  # noqa: E402
    ToolMissingError,
    VideoTooLongError,
    transcribe_video,
)


def main() -> None:
    st.set_page_config(page_title="Transcriptor pe", page_icon="CC", layout="centered")
    st.title("Video a SRT")
    st.write(
        "Cargar un video y se transcribe a SRT"
    )

    with st.sidebar:
        st.header("Configuracion")
        model_size = st.selectbox(
            "Modelo Whisper",
            MODEL_CHOICES,
            index=MODEL_CHOICES.index(DEFAULT_MODEL_SIZE),
            help="'base' es un buen inicio. 'small' suele ser mas preciso, pero tarda mas.",
        )
        language = st.text_input(
            "Idioma",
            value=DEFAULT_LANGUAGE,
            help="Usa 'es' para espanol. Dejalo vacio para deteccion automatica.",
        ).strip()
        device = st.selectbox(
            "Dispositivo",
            DEVICE_CHOICES,
            index=DEVICE_CHOICES.index(DEFAULT_DEVICE),
        )
        compute_type = st.selectbox(
            "Precision",
            COMPUTE_TYPE_CHOICES,
            index=COMPUTE_TYPE_CHOICES.index(DEFAULT_COMPUTE_TYPE),
            help="Si tienes errores en CPU, prueba con 'int8'. Si usas GPU NVIDIA, prueba 'float16'.",
        )

    uploaded_video = st.file_uploader(
        "Selecciona un video de hasta 5 minutos",
        type=VIDEO_EXTENSIONS,
        accept_multiple_files=False,
    )

    if not uploaded_video:
        st.info("Cuando cargues un video, podras iniciar la transcripcion.")
        return

    if st.session_state.get("uploaded_video_name") != uploaded_video.name:
        st.session_state["uploaded_video_name"] = uploaded_video.name
        st.session_state.pop("srt_editor", None)
        st.session_state.pop("srt_output_name", None)

    st.caption(f"Archivo: {uploaded_video.name}")
    if st.button("Transcribir video", type="primary"):
        temp_video_path: Path | None = None
        status = st.empty()

        try:
            suffix = Path(uploaded_video.name).suffix or ".mp4"
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_video:
                temp_video.write(uploaded_video.getbuffer())
                temp_video_path = Path(temp_video.name)

            with st.spinner("Procesando video..."):
                segments = transcribe_video(
                    temp_video_path,
                    model_size=model_size,
                    language=language or None,
                    device=device,
                    compute_type=compute_type,
                    max_duration_seconds=MAX_VIDEO_SECONDS,
                    progress_callback=status.info,
                )

            if not segments:
                st.warning("No se detecto voz en el video.")
                return

            srt_text = segments_to_srt(segments)
            output_name = f"{Path(uploaded_video.name).stem}.srt"
            st.session_state["srt_editor"] = srt_text
            st.session_state["srt_output_name"] = output_name

            status.success("Transcripcion lista.")

        except ToolMissingError as error:
            st.error(str(error))
            st.info("Instala FFmpeg y confirma que los comandos `ffmpeg` y `ffprobe` funcionen en PowerShell.")
        except VideoTooLongError as error:
            st.error(str(error))
        except Exception as error:
            st.error("No se pudo completar la transcripcion.")
            st.exception(error)
        finally:
            if temp_video_path and temp_video_path.exists():
                temp_video_path.unlink(missing_ok=True)

    _render_srt_editor()


def _render_srt_editor() -> None:
    if "srt_editor" not in st.session_state:
        return

    st.subheader("Editor SRT")
    st.caption("Puedes corregir el texto aqui. La descarga usara exactamente esta version editada.")
    edited_srt = st.text_area(
        "Contenido del archivo .srt",
        key="srt_editor",
        height=360,
    )
    st.download_button(
        "Descargar subtitulos .srt",
        data=edited_srt.encode("utf-8"),
        file_name=st.session_state.get("srt_output_name", "subtitulos.srt"),
        mime="application/x-subrip",
    )


if __name__ == "__main__":
    main()

