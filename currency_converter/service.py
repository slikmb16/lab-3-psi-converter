from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal, InvalidOperation
from typing import Callable

from .bnm import DataUnavailableError, fetch_bnm_rates
from .cache import RateCache
from .models import RateSnapshot

FetchFunction = Callable[[date], RateSnapshot]


def validate_amount(value: str) -> Decimal:
    normalized = value.strip().replace(",", ".")
    if not normalized:
        raise ValueError("Enter an amount.")
    try:
        amount = Decimal(normalized)
    except InvalidOperation as exc:
        raise ValueError("Amount must be a number, for example 125.50.") from exc
    if not amount.is_finite() or amount <= 0:
        raise ValueError("Amount must be greater than zero.")
    return amount


class RateService:
    def __init__(self, cache: RateCache | None = None, fetch: FetchFunction = fetch_bnm_rates) -> None:
        self.cache = cache or RateCache()
        self.fetch = fetch

    def load_latest_remote(self, start_date: date | None = None, lookback_days: int = 14) -> tuple[RateSnapshot, bool]:
        """Load the nearest published BNM snapshot; returns (snapshot, older_than_today)."""
        requested = start_date or date.today()
        last_error: Exception | None = None
        for offset in range(lookback_days + 1):
            try:
                snapshot = self.fetch(requested - timedelta(days=offset))
                self.cache.save(snapshot)
                return snapshot, offset > 0 or snapshot.effective_date != requested
            except DataUnavailableError as exc:
                last_error = exc
        raise DataUnavailableError(
            "No BNM rates were available for the last 14 days. Check your internet connection."
        ) from last_error

    def cached_snapshot(self) -> RateSnapshot | None:
        return self.cache.load()
