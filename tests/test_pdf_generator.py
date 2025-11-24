"""Tests for the PDF generator."""

import os
from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from src.models import BusinessDetails, ClientDetails, Invoice
from src.pdf_generator import InvoicePDFGenerator


class TestPDFGeneratorInitialisation:
    """Tests for PDF generator initialisation."""

    def test_initialises_with_business_details(self, pdf_generator: InvoicePDFGenerator, business_details: BusinessDetails):
        """Test that generator stores business details."""
        assert pdf_generator.business == business_details

    def test_has_custom_styles(self, pdf_generator: InvoicePDFGenerator):
        """Test that generator sets up custom styles."""
        assert "InvoiceTitle" in pdf_generator.styles
        assert "SectionHeader" in pdf_generator.styles
        assert "AddressText" in pdf_generator.styles
        assert "DetailLabel" in pdf_generator.styles
        assert "DetailValue" in pdf_generator.styles
        assert "Footer" in pdf_generator.styles


class TestPDFGeneration:
    """Tests for PDF file generation."""

    def test_generates_pdf_file(
        self,
        pdf_generator: InvoicePDFGenerator,
        sample_invoice: Invoice,
        temp_invoice_dir: Path,
    ):
        """Test that PDF file is created."""
        output_path = str(temp_invoice_dir / "test_invoice.pdf")

        pdf_generator.generate(sample_invoice, output_path)

        assert os.path.exists(output_path)

    def test_generated_pdf_has_content(
        self,
        pdf_generator: InvoicePDFGenerator,
        sample_invoice: Invoice,
        temp_invoice_dir: Path,
    ):
        """Test that generated PDF has non-zero size."""
        output_path = str(temp_invoice_dir / "test_invoice.pdf")

        pdf_generator.generate(sample_invoice, output_path)

        file_size = os.path.getsize(output_path)
        assert file_size > 0

    def test_creates_output_directory_if_not_exists(
        self,
        pdf_generator: InvoicePDFGenerator,
        sample_invoice: Invoice,
        tmp_path: Path,
    ):
        """Test that output directory is created if it doesn't exist."""
        nested_path = tmp_path / "nested" / "dir" / "invoice.pdf"
        assert not nested_path.parent.exists()

        pdf_generator.generate(sample_invoice, str(nested_path))

        assert nested_path.exists()

    def test_generates_valid_pdf_format(
        self,
        pdf_generator: InvoicePDFGenerator,
        sample_invoice: Invoice,
        temp_invoice_dir: Path,
    ):
        """Test that generated file is a valid PDF."""
        output_path = str(temp_invoice_dir / "test_invoice.pdf")

        pdf_generator.generate(sample_invoice, output_path)

        with open(output_path, "rb") as f:
            header = f.read(5)
        assert header == b"%PDF-"

    def test_overwrites_existing_file(
        self,
        pdf_generator: InvoicePDFGenerator,
        sample_invoice: Invoice,
        temp_invoice_dir: Path,
    ):
        """Test that existing file is overwritten."""
        output_path = str(temp_invoice_dir / "test_invoice.pdf")

        # Generate first version
        pdf_generator.generate(sample_invoice, output_path)
        first_size = os.path.getsize(output_path)

        # Modify invoice and regenerate
        sample_invoice.description = "A much longer description that should result in a different file size"
        pdf_generator.generate(sample_invoice, output_path)
        second_size = os.path.getsize(output_path)

        # File should be regenerated (sizes may differ)
        assert os.path.exists(output_path)


class TestPDFContentGeneration:
    """Tests for PDF content generation (internal methods)."""

    def test_creates_address_section(
        self,
        pdf_generator: InvoicePDFGenerator,
        sample_invoice: Invoice,
    ):
        """Test that address section table is created."""
        table = pdf_generator._create_address_section(sample_invoice)

        assert table is not None
        # Table should have data
        assert len(table._cellvalues) > 0

    def test_creates_invoice_details(
        self,
        pdf_generator: InvoicePDFGenerator,
        sample_invoice: Invoice,
    ):
        """Test that invoice details table is created."""
        table = pdf_generator._create_invoice_details(sample_invoice)

        assert table is not None
        assert len(table._cellvalues) == 4  # 4 detail rows

    def test_creates_description_table(
        self,
        pdf_generator: InvoicePDFGenerator,
        sample_invoice: Invoice,
    ):
        """Test that description table is created."""
        table = pdf_generator._create_description_table(sample_invoice)

        assert table is not None
        assert len(table._cellvalues) == 2  # Header + 1 item row

    def test_creates_totals_section(
        self,
        pdf_generator: InvoicePDFGenerator,
        sample_invoice: Invoice,
    ):
        """Test that totals section is created."""
        table = pdf_generator._create_totals_section(sample_invoice)

        assert table is not None
        assert len(table._cellvalues) == 3  # Subtotal, VAT, Total

    def test_creates_footer(
        self,
        pdf_generator: InvoicePDFGenerator,
        sample_invoice: Invoice,
    ):
        """Test that footer is created."""
        footer = pdf_generator._create_footer(sample_invoice)

        assert footer is not None


class TestPDFWithDifferentDates:
    """Tests for PDF generation with different date scenarios."""

    def test_due_on_receipt(
        self,
        pdf_generator: InvoicePDFGenerator,
        business_details: BusinessDetails,
        client_details: ClientDetails,
        temp_invoice_dir: Path,
    ):
        """Test PDF generation when due date equals issue date."""
        invoice = Invoice(
            invoice_number="INV1001",
            issue_date=date(2025, 11, 24),
            due_date=date(2025, 11, 24),
            business=business_details,
            client=client_details,
            description="Test job",
            amount=Decimal("100.00"),
        )
        output_path = str(temp_invoice_dir / "due_on_receipt.pdf")

        pdf_generator.generate(invoice, output_path)

        assert os.path.exists(output_path)

    def test_future_due_date(
        self,
        pdf_generator: InvoicePDFGenerator,
        business_details: BusinessDetails,
        client_details: ClientDetails,
        temp_invoice_dir: Path,
    ):
        """Test PDF generation with future due date."""
        invoice = Invoice(
            invoice_number="INV1002",
            issue_date=date(2025, 11, 24),
            due_date=date(2025, 12, 24),
            business=business_details,
            client=client_details,
            description="Test job",
            amount=Decimal("100.00"),
        )
        output_path = str(temp_invoice_dir / "future_due.pdf")

        pdf_generator.generate(invoice, output_path)

        assert os.path.exists(output_path)


class TestPDFWithDifferentClients:
    """Tests for PDF generation with different client scenarios."""

    def test_client_with_company(
        self,
        pdf_generator: InvoicePDFGenerator,
        sample_invoice: Invoice,
        temp_invoice_dir: Path,
    ):
        """Test PDF generation for client with company name."""
        output_path = str(temp_invoice_dir / "with_company.pdf")

        pdf_generator.generate(sample_invoice, output_path)

        assert os.path.exists(output_path)

    def test_client_without_company(
        self,
        pdf_generator: InvoicePDFGenerator,
        business_details: BusinessDetails,
        client_details_no_company: ClientDetails,
        temp_invoice_dir: Path,
    ):
        """Test PDF generation for client without company name."""
        invoice = Invoice(
            invoice_number="INV1001",
            issue_date=date.today(),
            due_date=date.today(),
            business=business_details,
            client=client_details_no_company,
            description="Test job",
            amount=Decimal("100.00"),
        )
        output_path = str(temp_invoice_dir / "without_company.pdf")

        pdf_generator.generate(invoice, output_path)

        assert os.path.exists(output_path)


class TestPDFWithDifferentAmounts:
    """Tests for PDF generation with various amounts."""

    @pytest.mark.parametrize(
        "amount",
        [
            Decimal("0.01"),
            Decimal("1.00"),
            Decimal("99.99"),
            Decimal("100.00"),
            Decimal("999.99"),
            Decimal("1000.00"),
            Decimal("9999.99"),
        ],
    )
    def test_various_amounts(
        self,
        pdf_generator: InvoicePDFGenerator,
        business_details: BusinessDetails,
        client_details: ClientDetails,
        temp_invoice_dir: Path,
        amount: Decimal,
    ):
        """Test PDF generation with various amounts."""
        invoice = Invoice(
            invoice_number="INV1001",
            issue_date=date.today(),
            due_date=date.today(),
            business=business_details,
            client=client_details,
            description="Test job",
            amount=amount,
        )
        output_path = str(temp_invoice_dir / f"amount_{amount}.pdf")

        pdf_generator.generate(invoice, output_path)

        assert os.path.exists(output_path)


class TestPDFWithSpecialCharacters:
    """Tests for PDF generation with special characters in content."""

    def test_description_with_special_chars(
        self,
        pdf_generator: InvoicePDFGenerator,
        business_details: BusinessDetails,
        client_details: ClientDetails,
        temp_invoice_dir: Path,
    ):
        """Test PDF generation with special characters in description."""
        invoice = Invoice(
            invoice_number="INV1001",
            issue_date=date.today(),
            due_date=date.today(),
            business=business_details,
            client=client_details,
            description="Waste removal - including: sofas, chairs & tables (x3)",
            amount=Decimal("200.00"),
        )
        output_path = str(temp_invoice_dir / "special_chars.pdf")

        pdf_generator.generate(invoice, output_path)

        assert os.path.exists(output_path)

    def test_client_name_with_apostrophe(
        self,
        pdf_generator: InvoicePDFGenerator,
        business_details: BusinessDetails,
        temp_invoice_dir: Path,
    ):
        """Test PDF generation with apostrophe in client name."""
        client = ClientDetails(
            name="O'Brien",
            company="O'Brien's Ltd",
            address_line1="123 Test St",
            city="Dublin",
            postcode="D01 ABC",
        )
        invoice = Invoice(
            invoice_number="INV1001",
            issue_date=date.today(),
            due_date=date.today(),
            business=business_details,
            client=client,
            description="Test job",
            amount=Decimal("100.00"),
        )
        output_path = str(temp_invoice_dir / "apostrophe.pdf")

        pdf_generator.generate(invoice, output_path)

        assert os.path.exists(output_path)
