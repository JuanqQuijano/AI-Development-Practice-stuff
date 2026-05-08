from __future__ import annotations

import sys
from pathlib import Path

from streamlit.web import cli as streamlit_cli


def main() -> None:
    app_path = _app_path()
    sys.argv = [
        "streamlit",
        "run",
        str(app_path),
        "--global.developmentMode=false",
        "--server.headless=false",
        "--server.address=localhost",
        "--server.port=8501",
        "--browser.serverAddress=localhost",
        "--browser.serverPort=8501",
        "--browser.gatherUsageStats=false",
    ]
    streamlit_cli.main()


def _app_path() -> Path:
    if getattr(sys, "frozen", False):
        bundle_dir = Path(getattr(sys, "_MEIPASS"))
        return bundle_dir / "transcriptor_app" / "app.py"

    return Path(__file__).with_name("app.py")


if __name__ == "__main__":
    main()

