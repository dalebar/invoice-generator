"""Tests for the invoice manager."""

import json
from pathlib import Path

import pytest

from src.invoice_manager import InvoiceManager
from src.models import Invoice, LineItem


class TestInvoiceManagerInitialisation:
    """Tests for InvoiceManager initialisation."""

    def test_creates_data_file_if_not_exists(self, temp_data_dir: Path):
        """Test that manager creates tracker file if it doesn't exist."""
        tracker_file = temp_data_dir / "invoice_tracker.json"
        assert not tracker_file.exists()

        manager = InvoiceManager(data_file=str(tracker_file))

        assert tracker_file.exists()

    def test_creates_parent_directories(self, tmp_path: Path):
        """Test that manager creates parent directories if they don't exist."""
        nested_path = tmp_path / "nested" / "dirs" / "tracker.json"
        assert not nested_path.parent.exists()

        manager = InvoiceManager(data_file=str(nested_path))

        assert nested_path.exists()

    def test_initialises_with_default_values(self, invoice_manager: InvoiceManager):
        """Test that new tracker has correct default values."""
        tracker = invoice_manager.load_tracker()

        assert tracker["last_invoice_number"] == 1000
        assert tracker["invoices"] == []

    def test_preserves_existing_tracker(self, temp_data_dir: Path):
        """Test that existing tracker data is preserved."""
        tracker_file = temp_data_dir / "invoice_tracker.json"
        existing_data = {
            "last_invoice_number": 1050,
            "invoices": [
                {
                    "invoice_number": "INV1050",
                    "client": "Existing Client",
                    "amount": "200.00",
                    "date": "2025-01-01",
                    "file_path": "invoices/INV1050.pdf",
                }
            ],
        }
        with open(tracker_file, "w") as f:
            json.dump(existing_data, f)

        manager = InvoiceManager(data_file=str(tracker_file))
        tracker = manager.load_tracker()

        assert tracker["last_invoice_number"] == 1050
        assert len(tracker["invoices"]) == 1
        assert tracker["invoices"][0]["client"] == "Existing Client"


class TestInvoiceNumbering:
    """Tests for invoice number generation."""

    def test_first_invoice_number_is_1001(self, invoice_manager: InvoiceManager):
        """Test that first invoice number starts at INV1001."""
        invoice_number = invoice_manager.get_next_invoice_number()
        assert invoice_number == "INV1001"

    def test_invoice_numbers_increment(self, invoice_manager: InvoiceManager):
        """Test that invoice numbers increment correctly."""
        first = invoice_manager.get_next_invoice_number()
        second = invoice_manager.get_next_invoice_number()
        third = invoice_manager.get_next_invoice_number()

        assert first == "INV1001"
        assert second == "INV1002"
        assert third == "INV1003"

    def test_invoice_number_format(self, invoice_manager: InvoiceManager):
        """Test that invoice numbers have correct format."""
        invoice_number = invoice_manager.get_next_invoice_number()

        assert invoice_number.startswith("INV")
        assert invoice_number[3:].isdigit()

    def test_invoice_number_persists_after_reload(self, temp_data_dir: Path):
        """Test that invoice numbers persist across manager instances."""
        tracker_file = temp_data_dir / "invoice_tracker.json"

        manager1 = InvoiceManager(data_file=str(tracker_file))
        manager1.get_next_invoice_number()  # INV1001
        manager1.get_next_invoice_number()  # INV1002

        manager2 = InvoiceManager(data_file=str(tracker_file))
        next_number = manager2.get_next_invoice_number()

        assert next_number == "INV1003"

    def test_continues_from_existing_number(self, temp_data_dir: Path):
        """Test that numbering continues from existing last number."""
        tracker_file = temp_data_dir / "invoice_tracker.json"
        with open(tracker_file, "w") as f:
            json.dump({"last_invoice_number": 2000, "invoices": []}, f)

        manager = InvoiceManager(data_file=str(tracker_file))
        invoice_number = manager.get_next_invoice_number()

        assert invoice_number == "INV2001"


class TestInvoiceRecordSaving:
    """Tests for saving invoice records."""

    def test_save_invoice_record(self, invoice_manager: InvoiceManager, sample_invoice: Invoice):
        """Test that invoice record is saved correctly."""
        file_path = "invoices/INV1001_Test.pdf"
        invoice_manager.save_invoice_record(sample_invoice, file_path)

        records = invoice_manager.get_invoice_records()

        assert len(records) == 1
        assert records[0]["invoice_number"] == "INV1001"
        assert records[0]["client"] == "Smith & Co Ltd"
        assert records[0]["amount"] == "150.00"
        assert records[0]["date"] == "2025-11-24"
        assert records[0]["file_path"] == file_path

    def test_save_multiple_records(
        self,
        invoice_manager: InvoiceManager,
        sample_invoice: Invoice,
        business_details,
        client_details_no_company,
    ):
        """Test that multiple invoice records can be saved."""
        from datetime import date
        from decimal import Decimal

        invoice_manager.save_invoice_record(sample_invoice, "invoices/INV1001.pdf")

        line_items2 = [LineItem("Another job", Decimal("200.00"))]
        invoice2 = Invoice(
            invoice_number="INV1002",
            issue_date=date(2025, 11, 25),
            due_date=date(2025, 11, 25),
            business=business_details,
            client=client_details_no_company,
            line_items=line_items2,
        )
        invoice_manager.save_invoice_record(invoice2, "invoices/INV1002.pdf")

        records = invoice_manager.get_invoice_records()

        assert len(records) == 2
        assert records[0]["invoice_number"] == "INV1001"
        assert records[1]["invoice_number"] == "INV1002"

    def test_uses_client_name_when_no_company(
        self,
        invoice_manager: InvoiceManager,
        business_details,
        client_details_no_company,
    ):
        """Test that client name is used when company is empty."""
        from datetime import date
        from decimal import Decimal

        line_items = [LineItem("Test", Decimal("100.00"))]
        invoice = Invoice(
            invoice_number="INV1001",
            issue_date=date.today(),
            due_date=date.today(),
            business=business_details,
            client=client_details_no_company,
            line_items=line_items,
        )

        invoice_manager.save_invoice_record(invoice, "invoices/INV1001.pdf")
        records = invoice_manager.get_invoice_records()

        assert records[0]["client"] == "Jane Doe"

    def test_records_persist_after_reload(self, temp_data_dir: Path, sample_invoice: Invoice):
        """Test that records persist across manager instances."""
        tracker_file = temp_data_dir / "invoice_tracker.json"

        manager1 = InvoiceManager(data_file=str(tracker_file))
        manager1.save_invoice_record(sample_invoice, "invoices/test.pdf")

        manager2 = InvoiceManager(data_file=str(tracker_file))
        records = manager2.get_invoice_records()

        assert len(records) == 1
        assert records[0]["invoice_number"] == "INV1001"


class TestTrackerFileHandling:
    """Tests for tracker file edge cases."""

    def test_handles_corrupted_json(self, temp_data_dir: Path):
        """Test that corrupted JSON is handled gracefully."""
        tracker_file = temp_data_dir / "invoice_tracker.json"
        with open(tracker_file, "w") as f:
            f.write("{ invalid json }")

        manager = InvoiceManager(data_file=str(tracker_file))
        tracker = manager.load_tracker()

        assert tracker["last_invoice_number"] == 1000
        assert tracker["invoices"] == []

    def test_handles_empty_file(self, temp_data_dir: Path):
        """Test that empty file is handled gracefully."""
        tracker_file = temp_data_dir / "invoice_tracker.json"
        tracker_file.touch()

        manager = InvoiceManager(data_file=str(tracker_file))
        tracker = manager.load_tracker()

        assert tracker["last_invoice_number"] == 1000
        assert tracker["invoices"] == []
