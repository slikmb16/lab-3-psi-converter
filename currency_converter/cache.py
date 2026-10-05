from __future__ import annotations

import json
import os
from pathlib import Path

from .models import CurrencyError, RateSnapshot


def default_cache_path() -> Path:
    base = Path(os.environ.get("LOCALAPPDATA", Path.home() / ".currency_converter"))
    return base / "PSI-Lab3-CurrencyConverter" / "rates.json"


class RateCache:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path or default_cache_path()

    def save(self, snapshot: RateSnapshot) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_suffix(".tmp")
        temporary.write_text(json.dumps(snapshot.as_dict(), indent=2), encoding="utf-8")
        temporary.replace(self.path)

    def load(self) -> RateSnapshot | None:
        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
            if not isinstance(payload, dict):
                return None
            return RateSnapshot.from_dict(payload)
        except (OSError, json.JSONDecodeError, CurrencyError):
            return None
