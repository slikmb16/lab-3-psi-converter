import http.client
import json
import threading
import unittest
from datetime import date
from decimal import Decimal
from http.server import ThreadingHTTPServer

from currency_converter.models import RateSnapshot
from currency_converter.web import ConverterRequestHandler


class StubRateService:
    def __init__(self) -> None:
        self.snapshot = RateSnapshot(date(2026, 10, 3), {"EUR": Decimal("20")})

    def load_latest_remote(self) -> tuple[RateSnapshot, bool]:
        return self.snapshot, False

    def cached_snapshot(self) -> RateSnapshot:
        return self.snapshot


class WebApplicationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.original_service = ConverterRequestHandler.service
        ConverterRequestHandler.service = StubRateService()
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), ConverterRequestHandler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)
        ConverterRequestHandler.service = cls.original_service

    def request(self, path: str) -> tuple[int, str, str]:
        connection = http.client.HTTPConnection("127.0.0.1", self.server.server_port, timeout=2)
        connection.request("GET", path)
        response = connection.getresponse()
        body = response.read().decode("utf-8")
        content_type = response.getheader("Content-Type") or ""
        connection.close()
        return response.status, content_type, body

    def test_home_page_is_served_in_russian(self) -> None:
        status, content_type, body = self.request("/")
        self.assertEqual(status, 200)
        self.assertIn("text/html", content_type)
        self.assertIn("Конвертер валют", body)

    def test_test_page_offers_individual_and_full_test_runs(self) -> None:
        status, _, body = self.request("/tests.html")
        self.assertEqual(status, 200)
        self.assertIn('id="run-all"', body)
        self.assertIn("Запустить все тесты", body)

    def test_rates_directory_page_is_served(self) -> None:
        status, _, body = self.request("/rates.html")
        self.assertEqual(status, 200)
        self.assertIn("СПРАВОЧНИК ВАЛЮТ", body)
        self.assertIn('id="rate-search"', body)

    def test_rates_api_returns_normalized_snapshot(self) -> None:
        status, content_type, body = self.request("/api/rates")
        payload = json.loads(body)
        self.assertEqual(status, 200)
        self.assertIn("application/json", content_type)
        self.assertEqual(payload["snapshot"]["rates"]["MDL"], "1")
        self.assertEqual(payload["snapshot"]["effective_date"], "2026-10-03")
