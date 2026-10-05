from __future__ import annotations

import threading
import tkinter as tk
from datetime import date
from decimal import Decimal
from tkinter import messagebox, ttk

from .bnm import DataUnavailableError
from .models import CurrencyError, RateSnapshot
from .service import RateService, validate_amount


class CurrencyConverterApp:
    BG = "#0B1220"
    CARD = "#162033"
    ACCENT = "#4F8CFF"
    TEXT = "#F4F7FB"
    MUTED = "#AAB8D0"

    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("Currency Flow · BNM Converter")
        self.root.geometry("620x570")
        self.root.minsize(560, 520)
        self.root.configure(bg=self.BG)
        self.service = RateService()
        self.snapshot: RateSnapshot | None = self.service.cached_snapshot()
        self.amount_var = tk.StringVar()
        self.source_var = tk.StringVar(value="EUR")
        self.target_var = tk.StringVar(value="MDL")
        self.status_var = tk.StringVar(value="Preparing rate data…")
        self.result_var = tk.StringVar(value="—")
        self.meta_var = tk.StringVar(value="Loading the latest official BNM rate")
        self._create_style()
        self._create_widgets()
        self._apply_snapshot(self.snapshot, cached=True) if self.snapshot else self._refresh_controls()
        self._load_rates_async()

    def _create_style(self) -> None:
        style = ttk.Style(self.root)
        style.theme_use("clam")
        style.configure("TFrame", background=self.BG)
        style.configure("Card.TFrame", background=self.CARD)
        style.configure("Title.TLabel", background=self.BG, foreground=self.TEXT, font=("Segoe UI", 23, "bold"))
        style.configure("Subtitle.TLabel", background=self.BG, foreground=self.MUTED, font=("Segoe UI", 10))
        style.configure("Label.TLabel", background=self.CARD, foreground=self.MUTED, font=("Segoe UI", 9, "bold"))
        style.configure("Value.TLabel", background=self.CARD, foreground=self.TEXT, font=("Segoe UI", 24, "bold"))
        style.configure("Info.TLabel", background=self.CARD, foreground=self.MUTED, font=("Segoe UI", 9))
        style.configure("TEntry", fieldbackground="#F8FAFC", padding=10, font=("Segoe UI", 12))
        style.configure("TCombobox", padding=9, font=("Segoe UI", 11))
        style.configure("Accent.TButton", background=self.ACCENT, foreground="white", padding=11, font=("Segoe UI", 11, "bold"))
        style.map("Accent.TButton", background=[("disabled", "#40506B"), ("active", "#3679ED")])

    def _create_widgets(self) -> None:
        container = ttk.Frame(self.root, padding=(38, 32), style="TFrame")
        container.pack(fill="both", expand=True)
        ttk.Label(container, text="Currency Flow", style="Title.TLabel").pack(anchor="w")
        ttk.Label(container, text="Official exchange rates · National Bank of Moldova", style="Subtitle.TLabel").pack(anchor="w", pady=(2, 24))

        card = ttk.Frame(container, padding=24, style="Card.TFrame")
        card.pack(fill="x")
        ttk.Label(card, text="AMOUNT", style="Label.TLabel").grid(row=0, column=0, sticky="w")
        amount = ttk.Entry(card, textvariable=self.amount_var)
        amount.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(6, 18))
        amount.bind("<KeyRelease>", lambda _event: self._refresh_controls())
        amount.bind("<Return>", lambda _event: self.convert())

        ttk.Label(card, text="FROM", style="Label.TLabel").grid(row=2, column=0, sticky="w")
        ttk.Label(card, text="TO", style="Label.TLabel").grid(row=2, column=2, sticky="w")
        self.source_box = ttk.Combobox(card, textvariable=self.source_var, state="readonly", width=13)
        self.target_box = ttk.Combobox(card, textvariable=self.target_var, state="readonly", width=13)
        self.source_box.grid(row=3, column=0, sticky="ew", pady=(6, 20))
        ttk.Label(card, text="→", style="Info.TLabel", font=("Segoe UI", 18)).grid(row=3, column=1, padx=14)
        self.target_box.grid(row=3, column=2, sticky="ew", pady=(6, 20))
        self.source_box.bind("<<ComboboxSelected>>", lambda _event: self._refresh_controls())
        self.target_box.bind("<<ComboboxSelected>>", lambda _event: self._refresh_controls())
        self.convert_button = ttk.Button(card, text="Convert", style="Accent.TButton", command=self.convert)
        self.convert_button.grid(row=4, column=0, columnspan=3, sticky="ew")
        card.columnconfigure(0, weight=1)
        card.columnconfigure(2, weight=1)

        result = ttk.Frame(container, padding=24, style="Card.TFrame")
        result.pack(fill="x", pady=(18, 0))
        ttk.Label(result, text="CONVERTED AMOUNT", style="Label.TLabel").pack(anchor="w")
        ttk.Label(result, textvariable=self.result_var, style="Value.TLabel").pack(anchor="w", pady=(6, 4))
        ttk.Label(result, textvariable=self.meta_var, style="Info.TLabel", wraplength=480).pack(anchor="w")
        ttk.Label(container, textvariable=self.status_var, style="Subtitle.TLabel", wraplength=520).pack(anchor="w", pady=(16, 0))

    def _refresh_controls(self) -> None:
        ready = bool(self.amount_var.get().strip() and self.source_var.get() and self.target_var.get())
        self.convert_button.configure(state="normal" if ready else "disabled")

    def _apply_snapshot(self, snapshot: RateSnapshot, cached: bool = False, prior_date: bool = False) -> None:
        self.snapshot = snapshot
        currencies = snapshot.currencies
        self.source_box["values"] = currencies
        self.target_box["values"] = currencies
        if self.source_var.get() not in currencies:
            self.source_var.set("MDL")
        if self.target_var.get() not in currencies:
            self.target_var.set("EUR" if "EUR" in currencies else "MDL")
        detail = f"Rate date: {snapshot.effective_date:%d.%m.%Y} · {snapshot.source}"
        if cached:
            detail = "Saved local data · " + detail
        elif prior_date:
            detail = "Latest available working-day rate · " + detail
        self.meta_var.set(detail)
        self.status_var.set("Offline cache ready." if cached else "Official rates are ready.")
        self._refresh_controls()

    def _load_rates_async(self) -> None:
        self.status_var.set("Updating official rates…")
        threading.Thread(target=self._load_worker, daemon=True).start()

    def _load_worker(self) -> None:
        try:
            snapshot, prior_date = self.service.load_latest_remote(date.today())
            self.root.after(0, lambda: self._apply_snapshot(snapshot, prior_date=prior_date))
        except DataUnavailableError as error:
            self.root.after(0, lambda: self._handle_load_failure(str(error)))

    def _handle_load_failure(self, error: str) -> None:
        cached = self.service.cached_snapshot()
        if cached:
            use_cache = messagebox.askyesno(
                "Network unavailable",
                f"{error}\n\nUse saved BNM rates from {cached.effective_date:%d.%m.%Y}?",
                parent=self.root,
            )
            if use_cache:
                self._apply_snapshot(cached, cached=True)
                return
        self.status_var.set("No rate data available. Connect to the internet and try again.")
        self.meta_var.set("No cached data is available for a safe conversion.")

    def convert(self) -> None:
        try:
            amount: Decimal = validate_amount(self.amount_var.get())
            if not self.snapshot:
                raise CurrencyError("Rates are still loading. Please wait a moment.")
            value = self.snapshot.convert(amount, self.source_var.get(), self.target_var.get())
        except (ValueError, CurrencyError) as error:
            self.result_var.set("Input needs attention")
            self.status_var.set(str(error))
            return
        self.result_var.set(f"{value:,.2f} {self.target_var.get()}")
        self.status_var.set("Conversion completed successfully.")

    def run(self) -> None:
        self.root.mainloop()
