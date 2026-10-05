import unittest
from decimal import Decimal

from currency_converter.bnm import DataUnavailableError, parse_bnm_xml


VALID_XML = """<?xml version='1.0'?>
<CurrencyRates Date="03.10.2026">
  <Valute><CharCode>EUR</CharCode><Nominal>1</Nominal><Value>20,1456</Value></Valute>
  <Valute><CharCode>JPY</CharCode><Nominal>100</Nominal><Value>11,5550</Value></Valute>
</CurrencyRates>"""


class BnmParserTests(unittest.TestCase):
    def test_parses_rates_and_nominal(self) -> None:
        snapshot = parse_bnm_xml(VALID_XML)
        self.assertEqual(str(snapshot.effective_date), "2026-10-03")
        self.assertEqual(snapshot.rates["EUR"], Decimal("20.1456"))
        self.assertEqual(snapshot.rates["JPY"], Decimal("0.11555"))
        self.assertEqual(snapshot.rates["MDL"], Decimal("1"))

    def test_rejects_empty_response(self) -> None:
        with self.assertRaises(DataUnavailableError):
            parse_bnm_xml("<CurrencyRates Date='03.10.2026'></CurrencyRates>")

    def test_rejects_missing_required_field(self) -> None:
        xml = "<CurrencyRates Date='03.10.2026'><Valute><CharCode>EUR</CharCode><Nominal>1</Nominal></Valute></CurrencyRates>"
        with self.assertRaises(DataUnavailableError):
            parse_bnm_xml(xml)
