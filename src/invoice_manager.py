"""Invoice management - numbering and record-keeping."""

import json
import os
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Any

from .models import Invoice


class InvoiceManager:
    """Manages invoice numbering and tracking."""

    def __init__(self, data_file: str = "data/invoice_tracker.json"):
        """
        Initialize manager, create data file if doesn't exist.

        Args:
            data_file: Path to the invoice tracker JSON file.
        """
        self.data_file = Path(data_file)
        self._ensure_data_file_exists()

    def _ensure_data_file_exists(self) -> None:
        """Create the data directory and file if they don't exist."""
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        if not self.data_file.exists():
            self._save_tracker({"last_invoice_number": 1000, "invoices": []})

    def load_tracker(self) -> dict[str, Any]:
        """
        Load existing tracker or create new one.

        Returns:
            Dictionary containing tracker data.
        """
        try:
            with open(self.data_file, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            default_tracker = {"last_invoice_number": 1000, "invoices": []}
            self._save_tracker(default_tracker)
            return default_tracker

    def _save_tracker(self, data: dict[str, Any]) -> None:
        """
        Save tracker data to file.

        Args:
            data: Tracker data to save.
        """
        with open(self.data_file, "w") as f:
            json.dump(data, f, indent=4)

    def get_next_invoice_number(self) -> str:
        """
        Returns next invoice number in format 'INV1001', 'INV1002', etc.

        Starts at INV1001 if no previous invoices exist.

        Returns:
            Next invoice number as string.
        """
        tracker = self.load_tracker()
        next_number = tracker["last_invoice_number"] + 1
        tracker["last_invoice_number"] = next_number
        self._save_tracker(tracker)
        return f"INV{next_number}"

    def save_invoice_record(self, invoice: Invoice, file_path: str) -> None:
        """
        Saves invoice metadata to tracker JSON file.

        Stores: invoice_number, client_name, amount, date, file_path

        Args:
            invoice: The invoice to record.
            file_path: Path where the PDF was saved.
        """
        tracker = self.load_tracker()

        record = {
            "invoice_number": invoice.invoice_number,
            "client": invoice.client.company if invoice.client.company else invoice.client.name,
            "amount": str(invoice.amount),
            "date": invoice.issue_date.isoformat(),
            "file_path": file_path,
        }

        tracker["invoices"].append(record)
        self._save_tracker(tracker)

    def get_invoice_records(self) -> list[dict[str, Any]]:
        """
        Get all invoice records.

        Returns:
            List of invoice record dictionaries.
        """
        tracker = self.load_tracker()
        return tracker.get("invoices", [])
