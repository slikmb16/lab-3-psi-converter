# Specification: Currency Converter

**Feature branch:** `feature/specifications`  
**Status:** Approved for implementation  
**Source:** National Bank of Moldova (BNM), official XML feed

## User stories

### US-1 — Convert an amount (priority P1)

As a user, I enter a positive amount, choose a source and target currency, and receive the converted amount.

**Acceptance scenarios**

1. Given valid rates for USD and EUR, when I convert 100 USD to EUR, then the result is calculated through MDL using both rates.
2. Given identical source and target currencies, when I convert a valid amount, then the result equals the original amount and no error is shown.
3. The Convert button remains disabled until amount and both currencies are supplied.

### US-2 — Trust the result (priority P1)

As a user, I see the source and effective date of the rate used for every result.

**Acceptance scenarios**

1. After a successful conversion, the interface names BNM and displays the effective rate date.
2. If BNM has no data for the requested date, the interface explicitly says that the last available date was used.

### US-3 — Work safely without network (priority P1)

As a user, I can keep converting with a previously saved rate if the network is unavailable.

**Acceptance scenarios**

1. A request failure does not close or freeze the application.
2. When a valid local cache exists, the user is offered a choice to use it, and its date is shown.
3. When no cache exists, a clear message explains that a connection is needed before the first conversion.
4. A successful remote response is saved locally and is usable after restarting the application.

### US-4 — Receive useful validation (priority P1)

As a user, I get a clear error rather than an invalid calculation.

**Acceptance scenarios**

1. Empty input, letters, zero and negative amounts are rejected.
2. Decimal comma and decimal point are accepted.
3. No conversion is performed after validation fails.

## Functional requirements

- **FR-01:** GUI contains an amount field, two currency selectors, Convert button and result panel.
- **FR-02:** Supported currencies include MDL and all valid currencies from the BNM response.
- **FR-03:** XML parser validates required fields `CharCode`, `Nominal`, `Value`, and response date.
- **FR-04:** BNM quote is interpreted as MDL per one foreign-currency unit (`Value / Nominal`).
- **FR-05:** `converted = amount * source_mdl_rate / target_mdl_rate`; MDL rate is exactly 1.
- **FR-06:** The app requests today's feed and searches up to 14 preceding calendar days for a usable published feed.
- **FR-07:** Cache stores the complete successfully parsed rate snapshot under a user-local project data directory.
- **FR-08:** Network, parsing and storage errors are caught and expressed in user-facing language.
- **FR-09:** Output shows a value rounded to two decimal places and an informative rate status.

## Non-functional requirements

- Standard-library runtime dependencies only.
- Unit tests do not perform live HTTP requests.
- Responsive GUI: the remote load runs in a background thread.
- Application is operable with mouse and keyboard.

## Out of scope

- Historical-date picker.
- Automatic repeated background updates.
- Buying/selling spread or fees.
