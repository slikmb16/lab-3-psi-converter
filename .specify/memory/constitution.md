# Currency Converter Constitution

## Principles

1. **Specification first.** Behavioural requirements are captured in Markdown and reviewed before implementation begins.
2. **Reliable offline behaviour.** A failed request must never terminate the GUI. A locally persisted last known good rate may be used only with its real source date shown.
3. **Correct financial calculation.** BNM rates represent MDL per currency nominal; conversion always goes through MDL and respects `Nominal`.
4. **Transparent data provenance.** Every displayed result identifies BNM and the effective rate date.
5. **Test the non-visual core.** Parsing, validation, conversion and cache fallback are independently testable without Tkinter or a live network.

## Constraints

- Desktop graphical interface; no console-only workflow.
- Python standard library only at runtime.
- Cache data is local, JSON encoded, and must survive restart.
- Invalid user input never triggers a network request or calculation.

## Quality gate

Before release, all tasks in `specs/001-currency-converter/tasks.md` marked complete and
`python -m unittest discover -s tests -v` must pass.
