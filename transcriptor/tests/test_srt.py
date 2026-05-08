from transcriptor_app.srt import format_timestamp, segments_to_srt


def test_format_timestamp_uses_srt_format() -> None:
    assert format_timestamp(65.432) == "00:01:05,432"


def test_segments_to_srt_generates_numbered_subtitles() -> None:
    srt = segments_to_srt(
        [
            {"start": 0.0, "end": 1.5, "text": " Hola mundo "},
            {"start": 2.0, "end": 4.25, "text": "Segundo subtitulo"},
        ]
    )

    assert srt == (
        "1\n"
        "00:00:00,000 --> 00:00:01,500\n"
        "Hola mundo\n\n"
        "2\n"
        "00:00:02,000 --> 00:00:04,250\n"
        "Segundo subtitulo\n"
    )

