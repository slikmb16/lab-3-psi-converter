# Implementation Plan: Currency Converter

## Technical design

| Layer | Responsibility | Module |
|---|---|---|
| Domain | immutable rate snapshot and conversion formula | `models.py` |
| Data | XML interpretation and BNM HTTP fetch | `bnm.py` |
| Storage | atomic local JSON cache read/write | `cache.py` |
| Application | validation, date fallback and offline decision | `service.py` |
| Presentation | Tkinter GUI and background request orchestration | `gui.py` |

## Key decisions

1. **BNM XML** is authoritative for Moldova and needs no API key. It is appropriate for a MDL-based converter, although weekend fallback is required.
2. **Decimal** is used for money calculation to avoid binary floating-point rounding artifacts.
3. **JSON cache** saves normalized rates instead of only raw XML, allowing validation before persistence and easy recovery after restart.
4. **Tkinter** fulfils the graphical desktop requirement with no external install.

## Error handling

- Missing/invalid XML results in `DataUnavailableError`, not an application crash.
- Network failure causes a cache prompt; declining it leaves the GUI usable.
- Empty BNM result is treated as unavailable and causes a prior-date lookup.
- Cache corruption is ignored safely, then reported as no cache.

## Test strategy

- Fixture-based XML parser tests: nominal handling and absent fields.
- Domain conversion tests in both directions and same-currency path.
- Input-validation parameterized tests.
- Service tests with injected fetch functions for empty-response fallback and offline cache path.
