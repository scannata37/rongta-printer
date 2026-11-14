#!/usr/bin/env python3
"""Receipt Printer — a tiny local web app for your thermal printer.

Run:   python3 app.py          (opens http://localhost:8787)
No installs needed: standard-library Python only.

Routes
  GET  /              the web UI (static/index.html)
  GET  /api/status    is the printer queue ready?
  GET  /api/presets   built-in workouts / to-do items (receipt/presets.py)
  POST /api/parse     {"mode", "text"}                       -> {"title", "items"}
  POST /api/preview   {"mode", "title", "items", "options"}  -> {"rows": [...]}
  POST /api/print     same body as preview                   -> {"ok", "detail"}

Modes: shopping, todo, gym (see receipt/modes.py).
"""
from __future__ import annotations

import json
import os
import sys
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from receipt import modes, presets, printer

ROOT = Path(__file__).resolve().parent
STATIC = ROOT / "static"
PORT = int(os.environ.get("PORT", "8787"))


def _slip_from(body: dict):
    return modes.get(body.get("mode", "shopping"))["build"](body)


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):  # quieter console
        sys.stderr.write("  %s\n" % (fmt % args))

    # -- helpers -------------------------------------------------------------
    def _json(self, code: int, data: dict):
        payload = json.dumps(data).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def _body(self) -> dict:
        n = int(self.headers.get("Content-Length") or 0)
        try:
            return json.loads(self.rfile.read(n) or b"{}")
        except ValueError:
            return {}

    # -- routes ----------------------------------------------------------------
    def do_GET(self):
        if self.path in ("/", "/index.html"):
            data = (STATIC / "index.html").read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        elif self.path == "/api/status":
            self._json(200, printer.status())
        elif self.path == "/api/presets":
            self._json(200, presets.all_presets())
        else:
            self._json(404, {"error": "not found"})

    def do_POST(self):
        body = self._body()
        try:
            mode = modes.get(body.get("mode", "shopping"))
        except KeyError as e:
            return self._json(400, {"ok": False, "detail": str(e)})
        if self.path == "/api/parse":
            self._json(200, mode["parse"](body.get("text", "")))
        elif self.path == "/api/preview":
            self._json(200, {"rows": _slip_from(body).to_preview()})
        elif self.path == "/api/print":
            if not body.get("items"):
                return self._json(400, {"ok": False, "detail": "The list is empty."})
            try:
                detail = printer.send(_slip_from(body).to_escpos())
                self._json(200, {"ok": True, "detail": detail})
            except printer.PrintError as e:
                self._json(500, {"ok": False, "detail": str(e)})
        else:
            self._json(404, {"error": "not found"})


def main():
    server = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    url = "http://localhost:%d" % PORT
    print("Receipt Printer running at %s  (printer: %s)" % (url, printer.PRINTER_NAME))
    print("Press Ctrl+C to stop.")
    if "--no-browser" not in sys.argv:
        threading.Timer(0.6, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
