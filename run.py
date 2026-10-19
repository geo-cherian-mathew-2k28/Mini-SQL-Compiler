"""
Mini SQL Compiler — Application Entry Point.
Run directly with:
    python run.py          (Launches the Interactive Web IDE in your browser)
    python run.py --cli    (Runs in terminal CLI mode)
"""

import sys
import webbrowser
import threading
import time
from src.ui.server import start_server
from src.cli import main as cli_main


def main():
    if "--cli" in sys.argv:
        sys.argv.remove("--cli")
        cli_main()
    else:
        port = 5000
        url = f"http://127.0.0.1:{port}"

        # Open web browser automatically in background thread after 0.8 seconds
        def open_browser():
            time.sleep(0.8)
            try:
                webbrowser.open(url)
            except Exception:
                pass

        threading.Thread(target=open_browser, daemon=True).start()
        start_server(port=port)


if __name__ == "__main__":
    main()
