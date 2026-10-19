"""
Embedded HTTP and JSON API server for the Mini SQL Compiler Web Demo.
Uses standard library http.server — requires zero third-party packages.
"""

import json
import os
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
from typing import Optional

from src.compiler import MiniSQLCompiler
from src.semantic.schema import get_default_catalog

WEB_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "web"))


class CompilerHTTPHandler(BaseHTTPRequestHandler):
    """Handles static web requests and compiler API endpoints."""

    compiler: Optional[MiniSQLCompiler] = None
    catalog = get_default_catalog()

    def do_GET(self):
        url = urlparse(self.path)
        path = url.path

        if path == "/api/schema":
            self._send_json(self.catalog.to_dict())
            return

        # Serve static files from web/
        if path == "/" or path == "/index.html":
            file_path = os.path.join(WEB_DIR, "index.html")
            self._send_file(file_path, "text/html; charset=utf-8")
        elif path == "/style.css":
            file_path = os.path.join(WEB_DIR, "style.css")
            self._send_file(file_path, "text/css; charset=utf-8")
        elif path == "/app.js":
            file_path = os.path.join(WEB_DIR, "app.js")
            self._send_file(file_path, "application/javascript; charset=utf-8")
        else:
            self.send_error(404, f"File not found: {path}")

    def do_POST(self):
        url = urlparse(self.path)
        if url.path == "/api/compile":
            content_length = int(self.headers.get("Content-Length", 0))
            post_body = self.rfile.read(content_length).decode("utf-8")

            try:
                data = json.loads(post_body)
                query = data.get("query", "")
            except Exception as e:
                self._send_json({"error": f"Invalid JSON payload: {str(e)}"}, status=400)
                return

            if CompilerHTTPHandler.compiler is None:
                CompilerHTTPHandler.compiler = MiniSQLCompiler(CompilerHTTPHandler.catalog)

            result = CompilerHTTPHandler.compiler.compile(query)
            self._send_json(result.to_dict())
        else:
            self.send_error(404, "Endpoint not found")

    def _send_file(self, filepath: str, content_type: str):
        if not os.path.exists(filepath):
            self.send_error(404, f"File not found on server: {filepath}")
            return

        with open(filepath, "rb") as f:
            content = f.read()

        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(content)

    def _send_json(self, data: dict, status: int = 200):
        body = json.dumps(data, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        # Keep terminal clean: suppress routine access logs
        return


def start_server(host: str = "127.0.0.1", port: int = 5000):
    server_address = (host, port)
    httpd = HTTPServer(server_address, CompilerHTTPHandler)
    url = f"http://{host}:{port}"
    print(f"\n=======================================================")
    print(f"  Mini SQL Compiler Web IDE Server Started!")
    print(f"  Access URL: {url}")
    print(f"  Press Ctrl+C to terminate the server.")
    print(f"=======================================================\n")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[*] Shutting down server gracefully...")
        httpd.server_close()


if __name__ == "__main__":
    start_server()
