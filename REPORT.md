# PSI Laboratory Work 3 — Report

## 1. Selected source and justification

The application uses the official XML feed of the **National Bank of Moldova (BNM)**:

`https://www.bnm.md/en/official_exchange_rates?get_xml=1&date=DD.MM.YYYY`

It was selected because it is the national authoritative source for MDL rates, needs no API key, has a stable documented XML format, and directly supplies the MDL-per-currency values needed by the converter. BNM does not publish a new feed on every calendar day, so the application requests dates backwards for up to 14 days and labels the actual effective date.

## 2. SDD artifacts and implementation process

The specification-first artifacts are in `specs/001-currency-converter/` and the project rules are in `.specify/memory/constitution.md`. They define observable behaviour, data semantics, technical plan, tasks and a requirement checklist before the source code commit.

The implementation is split into the domain model, BNM XML parser/client, persistent cache, service layer and Tkinter GUI. All core business logic is independent of the interface and can be unit-tested without a network connection.

> **Honesty note for submission:** this prepared workspace was assembled in Codex, not inside the student's Antigravity account. Before submitting, replace this paragraph with the *actual* Antigravity model(s) and stages used, and include the relevant screenshots/history if the teacher requests evidence. Do not claim a model that was not used.

## 3. What was correct on the first implementation pass

- The GUI contains all required controls: amount, source and target currencies, disabled-until-ready Convert button, result, source and effective date.
- BNM rates are normalized to MDL per one currency unit, including BNM `Nominal` handling.
- The converter supports both directions and same-currency conversion.
- The last good normalized response is stored in local JSON and remains usable after restarting the program.
- Rate refresh runs outside the UI thread; request errors do not terminate the window.

## 4. Errors and manual corrections (required)

During integration, the initial XML date conversion used a non-existent `date.strptime` call. It was manually corrected to `datetime.strptime(...).date()` in `currency_converter/bnm.py`; a parser test protects the corrected code. The local environment also did not expose the Windows `py` launcher, so the documented commands were corrected to use the available `python` executable. This is why the README's tested command is `python -m unittest discover -s tests -v`.

## 5. Correspondence with the specification

The delivered implementation satisfies FR-01 through FR-09 in `spec.md`: all required controls exist; invalid, zero and negative input is rejected; equal currencies are handled; result provenance is displayed; no-network and no-publication-date paths are handled; and cache data survives restarts. The scope exclusions remain intentionally unimplemented.

## 6. Verification

Command run locally:

```powershell
python -m unittest discover -s tests -v
```

Result: **11 tests passed**. Coverage includes XML parsing, nominal conversion, malformed and empty source responses, conversion in both directions, identical currencies, input validation, previous-working-day fallback, and persistent cache recovery.

## 7. Git workflow

The local history contains separate branches and merge commits for specifications, implementation and tests: `feature/specifications`, `feature/implementation`, and `feature/tests`. A remote GitHub repository and real hosted pull requests are still needed to satisfy the assignment's external GitHub PR requirement; they cannot be created without access to the student's GitHub repository.
