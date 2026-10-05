# Currency Converter — PSI Lab 3

Desktop currency converter built from Spec-Driven Development artifacts. It uses the official National Bank of Moldova (BNM) XML feed and supports cached offline operation.

## Requirements

- Python 3.10 or newer (no third-party runtime packages)
- Tkinter (included with the usual Windows Python installation)

## Start the application

```powershell
python -m currency_converter
```

The first successful BNM response is saved locally in `%LOCALAPPDATA%\PSI-Lab3-CurrencyConverter\rates.json`. The program will offer this saved rate when the network is unavailable.

## Run tests

```powershell
python -m unittest discover -s tests -v
```

## Project layout

- `specs/001-currency-converter/` — specification, implementation plan, task list and quality checklist
- `.specify/memory/constitution.md` — project rules
- `currency_converter/` — GUI and application logic
- `tests/` — unit tests
- `REPORT.md` — required lab report

## Data source

The application requests BNM's official XML endpoint:

`https://www.bnm.md/en/official_exchange_rates?get_xml=1&date=DD.MM.YYYY`

BNM publishes rates for working days. If today's response is empty, the application searches earlier dates and clearly marks the date actually used.
