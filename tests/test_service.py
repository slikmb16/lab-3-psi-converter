import tempfile
import unittest
from datetime import date
from decimal import Decimal
from pathlib import Path

from currency_converter.bnm import DataUnavailableError
from currency_converter.cache import RateCache
from currency_converter.models import RateSnapshot
from currency_converter.service import RateService, validate_amount


class ValidationTests(unittest.TestCase):
    def test_accepts_dot_and_comma_decimal_separator(self) -> None:
        self.assertEqual(validate_amount("12,50"), Decimal("12.50"))
        self.assertEqual(validate_amount("12.50"), Decimal("12.50"))

    def test_rejects_invalid_values(self) -> None:
        for value in ("", "abc", "0", "-1"):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    validate_amount(value)


class ServiceTests(unittest.TestCase):
    def test_uses_previous_date_when_today_has_no_feed(self) -> None:
        calls: list[date] = []
        snapshot = RateSnapshot(date(2026, 10, 2), {"EUR": Decimal("20")})

        def fetch(requested: date) -> RateSnapshot:
            calls.append(requested)
            if requested == date(2026, 10, 3):
                raise DataUnavailableError("empty")
            return snapshot

        with tempfile.TemporaryDirectory() as folder:
            service = RateService(RateCache(Path(folder) / "cache.json"), fetch)
            actual, used_prior = service.load_latest_remote(date(2026, 10, 3))
        self.assertEqual(actual, snapshot)
        self.assertTrue(used_prior)
        self.assertEqual(calls, [date(2026, 10, 3), date(2026, 10, 2)])

    def test_saved_cache_survives_new_service_instance(self) -> None:
        snapshot = RateSnapshot(date(2026, 10, 3), {"EUR": Decimal("20")})
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "cache.json"
            RateCache(path).save(snapshot)
            restored = RateService(RateCache(path)).cached_snapshot()
        self.assertEqual(restored, snapshot)
