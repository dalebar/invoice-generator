"""Shared test fixtures for the invoice generator test suite."""

import json
import tempfile
from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from src.models import BusinessDetails, ClientDetails, Invoice
from src.invoice_manager import InvoiceManager
from src.pdf_generator import InvoicePDFGenerator


@pytest.fixture
def business_details() -> BusinessDetails:
    """Fixture providing sample business details."""
    return BusinessDetails(
        name="Test Business",
        address_line1="123 Test Street",
        city="Test City",
        postcode="TE1 1ST",
        email="test@example.com",
        sort_code="12-34-56",
        account_number="12345678",
    )


@pytest.fixture
def client_details() -> ClientDetails:
    """Fixture providing sample client details."""
    return ClientDetails(
        name="John Smith",
        company="Smith & Co Ltd",
        address_line1="456 Client Road",
        city="Client Town",
        postcode="CL1 1NT",
    )


@pytest.fixture
def client_details_no_company() -> ClientDetails:
    """Fixture providing client details without company name."""
    return ClientDetails(
        name="Jane Doe",
        company="",
        address_line1="789 Private Lane",
        city="Home Town",
        postcode="HM1 1ME",
    )


@pytest.fixture
def sample_invoice(business_details: BusinessDetails, client_details: ClientDetails) -> Invoice:
    """Fixture providing a complete sample invoice."""
    return Invoice(
        invoice_number="INV1001",
        issue_date=date(2025, 11, 24),
        due_date=date(2025, 11, 24),
        business=business_details,
        client=client_details,
        description="Waste removal and disposal services",
        amount=Decimal("150.00"),
    )


@pytest.fixture
def temp_data_dir(tmp_path: Path) -> Path:
    """Fixture providing a temporary data directory."""
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    return data_dir


@pytest.fixture
def temp_invoice_dir(tmp_path: Path) -> Path:
    """Fixture providing a temporary invoice output directory."""
    invoice_dir = tmp_path / "invoices"
    invoice_dir.mkdir()
    return invoice_dir


@pytest.fixture
def invoice_manager(temp_data_dir: Path) -> InvoiceManager:
    """Fixture providing an InvoiceManager with temporary storage."""
    tracker_file = temp_data_dir / "invoice_tracker.json"
    return InvoiceManager(data_file=str(tracker_file))


@pytest.fixture
def pdf_generator(business_details: BusinessDetails) -> InvoicePDFGenerator:
    """Fixture providing a PDF generator with sample business details."""
    return InvoicePDFGenerator(business_details)


@pytest.fixture
def temp_config_file(tmp_path: Path, business_details: BusinessDetails) -> Path:
    """Fixture providing a temporary config file with business details."""
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    config_file = config_dir / "business_details.json"

    config_data = {
        "name": business_details.name,
        "address_line1": business_details.address_line1,
        "city": business_details.city,
        "postcode": business_details.postcode,
        "email": business_details.email,
        "sort_code": business_details.sort_code,
        "account_number": business_details.account_number,
    }

    with open(config_file, "w") as f:
        json.dump(config_data, f)

    return config_file
