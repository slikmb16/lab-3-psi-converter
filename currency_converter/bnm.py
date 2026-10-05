from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from urllib.error import URLError
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

from .models import CurrencyError, RateSnapshot

BNM_URL = "https://www.bnm.md/en/official_exchange_rates?get_xml=1&date={date}"


class DataUnavailableError(RuntimeError):
    """BNM data cannot be obtained or cannot be trusted."""


class NetworkUnavailableError(DataUnavailableError):
    """The remote endpoint could not be reached; retrying earlier dates will not help."""


def _text(parent: ET.Element, name: str) -> str:
    value = parent.findtext(name)
    if not value or not value.strip():
        raise DataUnavailableError(f"В ответе BNM отсутствует обязательное поле {name}.")
    return value.strip()


def parse_bnm_xml(xml_text: str) -> RateSnapshot:
    """Parse an official BNM XML document into normalized MDL-per-unit rates."""
    try:
        root = ET.fromstring(xml_text)
        date_text = root.attrib.get("Date") or root.attrib.get("date")
        if not date_text:
            raise DataUnavailableError("В ответе BNM отсутствует дата курса.")
        effective_date = date.fromisoformat(date_text) if "-" in date_text else datetime.strptime(date_text, "%d.%m.%Y").date()
        rates: dict[str, Decimal] = {"MDL": Decimal("1")}
        entries = root.findall(".//Valute")
        if not entries:
            raise DataUnavailableError("BNM не вернул курсы валют на эту дату.")
        for entry in entries:
            code = _text(entry, "CharCode").upper()
            nominal = Decimal(_text(entry, "Nominal").replace(",", "."))
            value = Decimal(_text(entry, "Value").replace(",", "."))
            if nominal <= 0 or value <= 0:
                raise DataUnavailableError("Ответ BNM содержит неположительный курс.")
            rates[code] = value / nominal
        return RateSnapshot(effective_date=effective_date, rates=rates)
    except (ET.ParseError, InvalidOperation, ValueError, CurrencyError) as exc:
        if isinstance(exc, DataUnavailableError):
            raise
        raise DataUnavailableError("Ответ BNM пустой или содержит некорректный XML.") from exc


def fetch_bnm_rates(requested_date: date, timeout_seconds: int = 12) -> RateSnapshot:
    url = BNM_URL.format(date=requested_date.strftime("%d.%m.%Y"))
    request = Request(url, headers={"User-Agent": "PSI-Lab3-Currency-Converter/1.0"})
    try:
        with urlopen(request, timeout=timeout_seconds) as response:
            return parse_bnm_xml(response.read().decode("utf-8"))
    except (URLError, OSError, UnicodeDecodeError) as exc:
        raise NetworkUnavailableError("Не удалось подключиться к Национальному банку Молдовы.") from exc
