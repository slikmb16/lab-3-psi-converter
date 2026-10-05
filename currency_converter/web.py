"""Local web server for the Russian-language currency converter interface."""
from __future__ import annotations

import json
import mimetypes
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from .bnm import DataUnavailableError
from .service import RateService

STATIC_DIR = Path(__file__).with_name("web_static")


class ConverterRequestHandler(BaseHTTPRequestHandler):
    service = RateService()
    allowed_files = {"index.html", "app.css", "app.js", "tests.html", "tests.js", "rates.html", "rates.js"}

    def log_message(self, _format: str, *_args: object) -> None:
        """Keep normal application output clean."""

    def _json(self, payload: dict[str, object], status: HTTPStatus = HTTPStatus.OK) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path == "/api/rates":
            self._rates(parse_qs(parsed.query))
            return
        self._static(parsed.path)

    def _rates(self, query: dict[str, list[str]]) -> None:
        if query.get("cache") == ["1"]:
            cached = self.service.cached_snapshot()
            if not cached:
                self._json({"error": "Сохранённые курсы пока отсутствуют."}, HTTPStatus.SERVICE_UNAVAILABLE)
                return
            self._json({"snapshot": cached.as_dict(), "from_cache": True, "prior_date": False})
            return
        try:
            snapshot, prior_date = self.service.load_latest_remote()
            self._json({"snapshot": snapshot.as_dict(), "from_cache": False, "prior_date": prior_date})
        except DataUnavailableError as error:
            cached = self.service.cached_snapshot()
            self._json(
                {
                    "error": "Не удалось обновить официальный курс.",
                    "details": str(error),
                    "cached_date": cached.effective_date.isoformat() if cached else None,
                    "cache_available": cached is not None,
                },
                HTTPStatus.SERVICE_UNAVAILABLE,
            )

    def _static(self, request_path: str) -> None:
        filename = "index.html" if request_path in {"", "/"} else request_path.lstrip("/")
        if filename not in self.allowed_files:
            self.send_error(HTTPStatus.NOT_FOUND, "Страница не найдена")
            return
        content = (STATIC_DIR / filename).read_bytes()
        content_type, _ = mimetypes.guess_type(filename)
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", f"{content_type or 'text/plain'}; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)


def run_server(port: int = 8000) -> None:
    try:
        server = ThreadingHTTPServer(("127.0.0.1", port), ConverterRequestHandler)
    except OSError as error:
        if port != 8000:
            raise
        port = 8001
        server = ThreadingHTTPServer(("127.0.0.1", port), ConverterRequestHandler)
        print("Порт 8000 занят, поэтому выбран свободный порт 8001.")
    print(f"Веб-приложение запущено: http://127.0.0.1:{port}")
    print("Для остановки нажмите Ctrl+C.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nСервер остановлен.")
    finally:
        server.server_close()
