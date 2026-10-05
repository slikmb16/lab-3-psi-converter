import unittest
from datetime import date
from decimal import Decimal

from currency_converter.models import CurrencyError, RateSnapshot


class ConversionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.rates = RateSnapshot(date(2026, 10, 3), {"USD": Decimal("17.2"), "EUR": Decimal("20.0")})

    def test_converts_between_foreign_currencies(self) -> None:
        self.assertEqual(self.rates.convert(Decimal("100"), "USD", "EUR"), Decimal("86.00"))

    def test_converts_in_reverse_direction(self) -> None:
        self.assertEqual(self.rates.convert(Decimal("86"), "EUR", "USD"), Decimal("100.00"))

    def test_same_currency_returns_amount(self) -> None:
        self.assertEqual(self.rates.convert(Decimal("12.34"), "EUR", "EUR"), Decimal("12.34"))

    def test_rejects_non_positive_amount(self) -> None:
        with self.assertRaises(CurrencyError):
            self.rates.convert(Decimal("0"), "USD", "MDL")
