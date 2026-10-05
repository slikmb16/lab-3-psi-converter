from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from typing import Mapping


class CurrencyError(ValueError):
    """Raised for impossible or incomplete conversion data."""


@dataclass(frozen=True)
class RateSnapshot:
    """Official exchange rates expressed as MDL for one unit of currency."""

    effective_date: date
    rates: Mapping[str, Decimal]
    source: str = "National Bank of Moldova (BNM)"

    def __post_init__(self) -> None:
        normalized = {code.upper(): Decimal(str(rate)) for code, rate in self.rates.items()}
        normalized["MDL"] = Decimal("1")
        if any(rate <= 0 for rate in normalized.values()):
            raise CurrencyError("Все курсы валют должны быть положительными.")
        object.__setattr__(self, "rates", normalized)

    @property
    def currencies(self) -> list[str]:
        return sorted(self.rates)

    def convert(self, amount: Decimal, source_currency: str, target_currency: str) -> Decimal:
        if amount <= 0:
            raise CurrencyError("Сумма должна быть больше нуля.")
        source = source_currency.upper()
        target = target_currency.upper()
        if source not in self.rates or target not in self.rates:
            raise CurrencyError("Выбранная валюта отсутствует в загруженном курсе.")
        if source == target:
            return amount
        return (amount * self.rates[source] / self.rates[target]).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

    def as_dict(self) -> dict[str, object]:
        return {
            "effective_date": self.effective_date.isoformat(),
            "rates": {code: str(rate) for code, rate in self.rates.items()},
            "source": self.source,
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> "RateSnapshot":
        try:
            raw_rates = payload["rates"]
            if not isinstance(raw_rates, Mapping):
                raise TypeError("rates is not a mapping")
            return cls(
                effective_date=date.fromisoformat(str(payload["effective_date"])),
                rates={str(code): Decimal(str(value)) for code, value in raw_rates.items()},
                source=str(payload.get("source", "National Bank of Moldova (BNM)")),
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise CurrencyError("Сохранённые данные имеют неверную структуру.") from exc
