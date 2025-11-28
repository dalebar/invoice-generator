"""Tests for the data models."""

from dataclasses import asdict
from datetime import date
from decimal import Decimal

import pytest

from src.models import BusinessDetails, ClientDetails, Invoice, LineItem


class TestBusinessDetails:
    """Tests for the BusinessDetails dataclass."""

    def test_create_business_details(self, business_details: BusinessDetails):
        """Test that BusinessDetails can be created with all fields."""
        assert business_details.name == "Test Business"
        assert business_details.address_line1 == "123 Test Street"
        assert business_details.city == "Test City"
        assert business_details.postcode == "TE1 1ST"
        assert business_details.email == "test@example.com"
        assert business_details.sort_code == "12-34-56"
        assert business_details.account_number == "12345678"

    def test_business_details_is_dataclass(self, business_details: BusinessDetails):
        """Test that BusinessDetails is a proper dataclass."""
        data = asdict(business_details)
        assert isinstance(data, dict)
        assert len(data) == 8  # Including optional invoice_output_dir field

    def test_business_details_equality(self):
        """Test that two identical BusinessDetails are equal."""
        details1 = BusinessDetails(
            name="Test",
            address_line1="Line 1",
            city="City",
            postcode="AB1 2CD",
            email="test@test.com",
            sort_code="00-00-00",
            account_number="00000000",
        )
        details2 = BusinessDetails(
            name="Test",
            address_line1="Line 1",
            city="City",
            postcode="AB1 2CD",
            email="test@test.com",
            sort_code="00-00-00",
            account_number="00000000",
        )
        assert details1 == details2


class TestClientDetails:
    """Tests for the ClientDetails dataclass."""

    def test_create_client_with_company(self, client_details: ClientDetails):
        """Test creating client details with company name."""
        assert client_details.name == "John Smith"
        assert client_details.company == "Smith & Co Ltd"
        assert client_details.address_line1 == "456 Client Road"
        assert client_details.city == "Client Town"
        assert client_details.postcode == "CL1 1NT"

    def test_create_client_without_company(self, client_details_no_company: ClientDetails):
        """Test creating client details without company name."""
        assert client_details_no_company.name == "Jane Doe"
        assert client_details_no_company.company == ""
        assert client_details_no_company.address_line1 == "789 Private Lane"

    def test_client_details_is_dataclass(self, client_details: ClientDetails):
        """Test that ClientDetails is a proper dataclass."""
        data = asdict(client_details)
        assert isinstance(data, dict)
        assert len(data) == 5


class TestLineItem:
    """Tests for the LineItem dataclass."""

    def test_create_line_item(self):
        """Test that LineItem can be created."""
        item = LineItem("Test description", Decimal("100.00"))
        assert item.description == "Test description"
        assert item.amount == Decimal("100.00")
        assert item.quantity == 1  # Default

    def test_create_line_item_with_quantity(self):
        """Test that LineItem can be created with quantity."""
        item = LineItem("Day Rate", Decimal("100.00"), 5)
        assert item.description == "Day Rate"
        assert item.amount == Decimal("100.00")
        assert item.quantity == 5

    def test_line_item_line_total(self):
        """Test that line_total calculates correctly."""
        item1 = LineItem("Test", Decimal("100.00"), 1)
        assert item1.line_total == Decimal("100.00")

        item2 = LineItem("Day Rate", Decimal("100.00"), 5)
        assert item2.line_total == Decimal("500.00")

        item3 = LineItem("Hourly", Decimal("25.50"), 3)
        assert item3.line_total == Decimal("76.50")

    def test_line_item_is_dataclass(self):
        """Test that LineItem is a proper dataclass."""
        item = LineItem("Test", Decimal("50.00"))
        data = asdict(item)
        assert isinstance(data, dict)
        assert len(data) == 3  # description, amount, quantity


class TestInvoice:
    """Tests for the Invoice dataclass."""

    def test_create_invoice(self, sample_invoice: Invoice):
        """Test that Invoice can be created with all fields."""
        assert sample_invoice.invoice_number == "INV1001"
        assert sample_invoice.issue_date == date(2025, 11, 24)
        assert sample_invoice.due_date == date(2025, 11, 24)
        assert len(sample_invoice.line_items) == 1
        assert sample_invoice.line_items[0].description == "Waste removal and disposal services"
        assert sample_invoice.line_items[0].amount == Decimal("150.00")
        assert sample_invoice.vat_status == "No VAT"

    def test_invoice_total_property(self, sample_invoice: Invoice):
        """Test that total property returns the correct amount."""
        assert sample_invoice.total == Decimal("150.00")
        assert sample_invoice.total == sample_invoice.subtotal

    def test_invoice_default_vat_status(self, business_details, client_details):
        """Test that VAT status defaults to 'No VAT'."""
        line_items = [LineItem("Test", Decimal("100.00"))]
        invoice = Invoice(
            invoice_number="INV1002",
            issue_date=date.today(),
            due_date=date.today(),
            business=business_details,
            client=client_details,
            line_items=line_items,
        )
        assert invoice.vat_status == "No VAT"

    def test_invoice_custom_vat_status(self, business_details, client_details):
        """Test that custom VAT status can be set."""
        line_items = [LineItem("Test", Decimal("100.00"))]
        invoice = Invoice(
            invoice_number="INV1003",
            issue_date=date.today(),
            due_date=date.today(),
            business=business_details,
            client=client_details,
            line_items=line_items,
            vat_status="20% VAT",
        )
        assert invoice.vat_status == "20% VAT"

    def test_invoice_contains_business_details(self, sample_invoice: Invoice):
        """Test that invoice contains business details."""
        assert sample_invoice.business.name == "Test Business"
        assert sample_invoice.business.email == "test@example.com"

    def test_invoice_contains_client_details(self, sample_invoice: Invoice):
        """Test that invoice contains client details."""
        assert sample_invoice.client.name == "John Smith"
        assert sample_invoice.client.company == "Smith & Co Ltd"

    def test_invoice_with_different_amounts(self, business_details, client_details):
        """Test invoice with various decimal amounts."""
        test_amounts = [
            Decimal("0.01"),
            Decimal("99.99"),
            Decimal("1000.00"),
            Decimal("12345.67"),
        ]

        for amount in test_amounts:
            line_items = [LineItem("Test", amount)]
            invoice = Invoice(
                invoice_number="INV0001",
                issue_date=date.today(),
                due_date=date.today(),
                business=business_details,
                client=client_details,
                line_items=line_items,
            )
            assert invoice.subtotal == amount
            assert invoice.total == amount

    def test_invoice_with_multiple_line_items(self, business_details, client_details):
        """Test invoice with multiple line items calculates subtotal correctly."""
        line_items = [
            LineItem("Item 1", Decimal("50.00")),
            LineItem("Item 2", Decimal("30.00")),
            LineItem("Item 3", Decimal("20.00")),
        ]
        invoice = Invoice(
            invoice_number="INV0002",
            issue_date=date.today(),
            due_date=date.today(),
            business=business_details,
            client=client_details,
            line_items=line_items,
        )
        assert invoice.subtotal == Decimal("100.00")
        assert invoice.total == Decimal("100.00")

    def test_invoice_with_quantities(self, business_details, client_details):
        """Test invoice with line item quantities calculates correctly."""
        line_items = [
            LineItem("Day Rate", Decimal("100.00"), 5),
            LineItem("Hourly Rate", Decimal("25.00"), 4),
            LineItem("Fixed Fee", Decimal("50.00"), 1),
        ]
        invoice = Invoice(
            invoice_number="INV0003",
            issue_date=date.today(),
            due_date=date.today(),
            business=business_details,
            client=client_details,
            line_items=line_items,
        )
        # 100*5 + 25*4 + 50*1 = 500 + 100 + 50 = 650
        assert invoice.subtotal == Decimal("650.00")
        assert invoice.total == Decimal("650.00")
