"""Tests for the CLI interface."""

import os
from io import StringIO
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from src.cli import InvoiceCLI
from src.invoice_manager import InvoiceManager
from src.pdf_generator import InvoicePDFGenerator


class TestValidation:
    """Tests for CLI validation methods."""

    def test_validate_not_empty_with_value(self):
        """Test that non-empty values pass validation."""
        assert InvoiceCLI._validate_not_empty("hello") is True
        assert InvoiceCLI._validate_not_empty("a") is True
        assert InvoiceCLI._validate_not_empty("  text  ") is True

    def test_validate_not_empty_with_empty(self):
        """Test that empty values fail validation."""
        assert InvoiceCLI._validate_not_empty("") is False

    def test_validate_decimal_with_valid_values(self):
        """Test that valid decimal values pass validation."""
        assert InvoiceCLI._validate_decimal("100") is True
        assert InvoiceCLI._validate_decimal("100.00") is True
        assert InvoiceCLI._validate_decimal("0.01") is True
        assert InvoiceCLI._validate_decimal("9999.99") is True

    def test_validate_decimal_with_invalid_values(self):
        """Test that invalid decimal values fail validation."""
        assert InvoiceCLI._validate_decimal("") is False
        assert InvoiceCLI._validate_decimal("abc") is False
        assert InvoiceCLI._validate_decimal("12.34.56") is False
        assert InvoiceCLI._validate_decimal("-100") is False
        assert InvoiceCLI._validate_decimal("0") is False

    def test_validate_postcode_with_valid_postcodes(self):
        """Test that valid UK postcodes pass validation."""
        valid_postcodes = [
            "M1 1AA",
            "M11AA",
            "SK4 2QN",
            "SK42QN",
            "SW1A 1AA",
            "SW1A1AA",
            "EC1A 1BB",
            "W1A 0AX",
            "B33 8TH",
        ]
        for postcode in valid_postcodes:
            assert InvoiceCLI._validate_postcode(postcode) is True, f"Failed for {postcode}"

    def test_validate_postcode_with_invalid_postcodes(self):
        """Test that invalid postcodes fail validation."""
        invalid_postcodes = [
            "",
            "12345",
            "INVALID",
            "1234 ABC",
        ]
        for postcode in invalid_postcodes:
            assert InvoiceCLI._validate_postcode(postcode) is False, f"Should fail for {postcode}"


class TestFilenameSanitisation:
    """Tests for filename sanitisation."""

    def test_sanitize_simple_name(self):
        """Test sanitising a simple name."""
        assert InvoiceCLI._sanitize_filename("John Smith") == "John_Smith"

    def test_sanitize_company_name(self):
        """Test sanitising a company name."""
        assert InvoiceCLI._sanitize_filename("Smith & Co Ltd") == "Smith_Co_Ltd"

    def test_sanitize_name_with_special_chars(self):
        """Test sanitising name with special characters."""
        result = InvoiceCLI._sanitize_filename("O'Brien's Ltd.")
        assert "/" not in result
        assert "'" not in result

    def test_sanitize_multiple_spaces(self):
        """Test that multiple spaces become single underscore."""
        assert InvoiceCLI._sanitize_filename("John    Smith") == "John_Smith"


class TestPromptWithValidation:
    """Tests for prompt_with_validation method."""

    def test_valid_input_on_first_try(
        self,
        invoice_manager: InvoiceManager,
        pdf_generator: InvoicePDFGenerator,
    ):
        """Test that valid input is accepted on first try."""
        cli = InvoiceCLI(invoice_manager, pdf_generator)

        with patch("builtins.input", return_value="valid input"):
            result = cli.prompt_with_validation(
                "Enter value: ",
                validator=InvoiceCLI._validate_not_empty,
            )

        assert result == "valid input"

    def test_retries_on_invalid_input(
        self,
        invoice_manager: InvoiceManager,
        pdf_generator: InvoicePDFGenerator,
    ):
        """Test that prompt retries on invalid input."""
        cli = InvoiceCLI(invoice_manager, pdf_generator)

        with patch("builtins.input", side_effect=["", "", "valid"]):
            with patch("builtins.print"):
                result = cli.prompt_with_validation(
                    "Enter value: ",
                    validator=InvoiceCLI._validate_not_empty,
                    error_msg="Cannot be empty",
                )

        assert result == "valid"

    def test_strips_whitespace(
        self,
        invoice_manager: InvoiceManager,
        pdf_generator: InvoicePDFGenerator,
    ):
        """Test that input is stripped of whitespace."""
        cli = InvoiceCLI(invoice_manager, pdf_generator)

        with patch("builtins.input", return_value="  trimmed  "):
            result = cli.prompt_with_validation("Enter: ")

        assert result == "trimmed"


class TestPromptYesNo:
    """Tests for yes/no prompts."""

    def test_default_yes(
        self,
        invoice_manager: InvoiceManager,
        pdf_generator: InvoicePDFGenerator,
    ):
        """Test that empty input returns default True."""
        cli = InvoiceCLI(invoice_manager, pdf_generator)

        with patch("builtins.input", return_value=""):
            result = cli.prompt_yes_no("Continue? ", default=True)

        assert result is True

    def test_default_no(
        self,
        invoice_manager: InvoiceManager,
        pdf_generator: InvoicePDFGenerator,
    ):
        """Test that empty input returns default False."""
        cli = InvoiceCLI(invoice_manager, pdf_generator)

        with patch("builtins.input", return_value=""):
            result = cli.prompt_yes_no("Continue? ", default=False)

        assert result is False

    def test_explicit_yes(
        self,
        invoice_manager: InvoiceManager,
        pdf_generator: InvoicePDFGenerator,
    ):
        """Test that 'y' and 'yes' return True."""
        cli = InvoiceCLI(invoice_manager, pdf_generator)

        for response in ["y", "Y", "yes", "YES", "Yes"]:
            with patch("builtins.input", return_value=response):
                result = cli.prompt_yes_no("Continue? ", default=False)
            assert result is True, f"Failed for response: {response}"

    def test_explicit_no(
        self,
        invoice_manager: InvoiceManager,
        pdf_generator: InvoicePDFGenerator,
    ):
        """Test that 'n' returns False."""
        cli = InvoiceCLI(invoice_manager, pdf_generator)

        for response in ["n", "N", "no", "NO"]:
            with patch("builtins.input", return_value=response):
                result = cli.prompt_yes_no("Continue? ", default=True)
            assert result is False, f"Failed for response: {response}"


class TestInteractiveMode:
    """Tests for the full interactive mode."""

    def test_full_invoice_creation(
        self,
        invoice_manager: InvoiceManager,
        pdf_generator: InvoicePDFGenerator,
        tmp_path: Path,
    ):
        """Test complete invoice creation flow."""
        cli = InvoiceCLI(invoice_manager, pdf_generator)

        inputs = [
            # Contact creation (no saved contacts)
            "John Smith",        # Client name
            "Smith Ltd",         # Company
            "123 Test Street",   # Address
            "Manchester",        # City
            "M1 1AA",           # Postcode
            # Line items
            "Waste removal",     # Item 1 description
            "150.00",           # Item 1 amount
            "",                 # Item 1 quantity (default 1)
            "",                 # Finish adding items
            "y",                # Due on receipt
            # Save contact
            "n",                # Don't save contact
        ]

        # Change to temp directory for output
        original_cwd = os.getcwd()
        os.chdir(tmp_path)

        try:
            with patch("builtins.input", side_effect=inputs):
                with patch("builtins.print"):
                    cli.run_interactive()

            # Check invoice was created
            invoices_dir = tmp_path / "invoices"
            assert invoices_dir.exists()
            pdf_files = list(invoices_dir.glob("*.pdf"))
            assert len(pdf_files) == 1
            assert "INV1001" in pdf_files[0].name
        finally:
            os.chdir(original_cwd)

    def test_invoice_creation_without_company(
        self,
        invoice_manager: InvoiceManager,
        pdf_generator: InvoicePDFGenerator,
        tmp_path: Path,
    ):
        """Test invoice creation without company name."""
        cli = InvoiceCLI(invoice_manager, pdf_generator)

        inputs = [
            # Contact creation (no saved contacts)
            "Jane Doe",          # Client name
            "",                  # No company
            "456 Home Lane",     # Address
            "London",            # City
            "SW1A 1AA",         # Postcode
            # Line items
            "Garden clearance",  # Item 1 description
            "200.00",           # Item 1 amount
            "",                 # Item 1 quantity (default 1)
            "",                 # Finish adding items
            "y",                # Due on receipt
            # Save contact
            "n",                # Don't save contact
        ]

        original_cwd = os.getcwd()
        os.chdir(tmp_path)

        try:
            with patch("builtins.input", side_effect=inputs):
                with patch("builtins.print"):
                    cli.run_interactive()

            invoices_dir = tmp_path / "invoices"
            pdf_files = list(invoices_dir.glob("*.pdf"))
            assert len(pdf_files) == 1
            assert "Jane_Doe" in pdf_files[0].name
        finally:
            os.chdir(original_cwd)

    def test_invoice_number_increments(
        self,
        invoice_manager: InvoiceManager,
        pdf_generator: InvoicePDFGenerator,
        tmp_path: Path,
    ):
        """Test that invoice numbers increment on successive calls."""
        cli = InvoiceCLI(invoice_manager, pdf_generator)

        inputs_template = [
            # Contact creation
            "Client {}",
            "Company {}",
            "Address {}",
            "City",
            "M1 1AA",
            # Line items
            "Job {}",
            "100.00",
            "",  # Quantity (default 1)
            "",  # Finish items
            "y",  # Due on receipt
            "n",  # Don't save contact
        ]

        original_cwd = os.getcwd()
        os.chdir(tmp_path)

        try:
            for i in range(1, 4):
                inputs = [s.format(i) if "{}" in s else s for s in inputs_template]
                with patch("builtins.input", side_effect=inputs):
                    with patch("builtins.print"):
                        cli.run_interactive()

            invoices_dir = tmp_path / "invoices"
            pdf_files = sorted(invoices_dir.glob("*.pdf"))
            assert len(pdf_files) == 3
            assert "INV1001" in pdf_files[0].name
            assert "INV1002" in pdf_files[1].name
            assert "INV1003" in pdf_files[2].name
        finally:
            os.chdir(original_cwd)

    def test_validation_retry_flow(
        self,
        invoice_manager: InvoiceManager,
        pdf_generator: InvoicePDFGenerator,
        tmp_path: Path,
    ):
        """Test that validation errors cause retries."""
        cli = InvoiceCLI(invoice_manager, pdf_generator)

        inputs = [
            # Contact creation with validation errors
            "",                  # Empty client name (valid if company provided)
            "",                  # Empty company - both empty triggers error
            "John Smith",        # Valid client name after error
            "",                  # No company (ok since name provided)
            "",                  # Invalid - empty address
            "123 Test St",       # Valid address
            "",                  # Invalid - empty city
            "London",            # Valid city
            "invalid",           # Invalid postcode
            "SW1A 1AA",         # Valid postcode
            # Line items with validation errors
            "",                  # Invalid - empty description
            "Test job",          # Valid description
            "abc",               # Invalid amount
            "-50",               # Invalid amount (negative)
            "100.00",           # Valid amount
            "",                 # Quantity (default 1)
            "",                 # Finish adding items
            "y",                # Due on receipt
            "n",                # Don't save contact
        ]

        original_cwd = os.getcwd()
        os.chdir(tmp_path)

        try:
            with patch("builtins.input", side_effect=inputs):
                with patch("builtins.print"):
                    cli.run_interactive()

            invoices_dir = tmp_path / "invoices"
            pdf_files = list(invoices_dir.glob("*.pdf"))
            assert len(pdf_files) == 1
        finally:
            os.chdir(original_cwd)


class TestContactManagement:
    """Tests for contact management features."""

    def test_select_or_create_with_no_saved_contacts(
        self,
        invoice_manager: InvoiceManager,
        pdf_generator: InvoicePDFGenerator,
        tmp_path: Path,
    ):
        """Test contact selection when no contacts are saved."""
        from src.contact_manager import ContactManager

        contact_file = tmp_path / "contacts.json"
        contact_manager = ContactManager(str(contact_file))
        cli = InvoiceCLI(invoice_manager, pdf_generator, contact_manager)

        inputs = [
            "John Smith",        # Client name
            "Smith Ltd",         # Company
            "123 Test St",       # Address
            "London",            # City
            "SW1A 1AA",         # Postcode
        ]

        with patch("builtins.input", side_effect=inputs):
            with patch("builtins.print"):
                result = cli._select_or_create_contact()

        assert result.name == "John Smith"
        assert result.company == "Smith Ltd"
        assert result.postcode == "SW1A 1AA"

    def test_select_or_create_with_saved_contacts_choose_new(
        self,
        invoice_manager: InvoiceManager,
        pdf_generator: InvoicePDFGenerator,
        tmp_path: Path,
    ):
        """Test choosing to create new contact when saved contacts exist."""
        from src.contact_manager import ContactManager
        from src.models import ClientDetails

        contact_file = tmp_path / "contacts.json"
        contact_manager = ContactManager(str(contact_file))

        # Save a contact
        existing = ClientDetails(
            name="Existing Client",
            company="Existing Corp",
            address_line1="Old Address",
            city="Old City",
            postcode="OL1 1DC",
        )
        contact_manager.save_contact(existing)

        cli = InvoiceCLI(invoice_manager, pdf_generator, contact_manager)

        inputs = [
            "2",                 # Choose "Enter new contact manually"
            "New Client",        # Client name
            "New Corp",          # Company
            "New Address",       # Address
            "New City",          # City
            "NE1 1WC",          # Postcode
        ]

        with patch("builtins.input", side_effect=inputs):
            with patch("builtins.print"):
                result = cli._select_or_create_contact()

        assert result.name == "New Client"
        assert result.company == "New Corp"

    def test_select_or_create_with_saved_contacts_choose_existing(
        self,
        invoice_manager: InvoiceManager,
        pdf_generator: InvoicePDFGenerator,
        tmp_path: Path,
    ):
        """Test selecting an existing saved contact."""
        from src.contact_manager import ContactManager
        from src.models import ClientDetails

        contact_file = tmp_path / "contacts.json"
        contact_manager = ContactManager(str(contact_file))

        # Save a contact
        existing = ClientDetails(
            name="Saved Client",
            company="Saved Corp",
            address_line1="Saved Address",
            city="Saved City",
            postcode="SA1 1VE",
        )
        contact_manager.save_contact(existing, "Saved Contact")

        cli = InvoiceCLI(invoice_manager, pdf_generator, contact_manager)

        inputs = ["1"]  # Select first contact

        with patch("builtins.input", side_effect=inputs):
            with patch("builtins.print"):
                result = cli._select_or_create_contact()

        assert result.name == "Saved Client"
        assert result.company == "Saved Corp"
        assert result.postcode == "SA1 1VE"

    def test_create_new_contact_with_both_name_and_company(
        self,
        invoice_manager: InvoiceManager,
        pdf_generator: InvoicePDFGenerator,
    ):
        """Test creating a new contact with both name and company."""
        cli = InvoiceCLI(invoice_manager, pdf_generator)

        inputs = [
            "Alice Jones",       # Client name
            "Jones & Co",        # Company
            "100 Business Rd",   # Address
            "Manchester",        # City
            "M1 1AA",           # Postcode
        ]

        with patch("builtins.input", side_effect=inputs):
            with patch("builtins.print"):
                result = cli._create_new_contact()

        assert result.name == "Alice Jones"
        assert result.company == "Jones & Co"
        assert result.city == "Manchester"

    def test_create_new_contact_company_only(
        self,
        invoice_manager: InvoiceManager,
        pdf_generator: InvoicePDFGenerator,
    ):
        """Test creating a business-only contact (no individual name)."""
        cli = InvoiceCLI(invoice_manager, pdf_generator)

        inputs = [
            "",                  # No client name
            "Business Corp",     # Company
            "200 Corp Ave",      # Address
            "Birmingham",        # City
            "B33 8TH",          # Postcode
        ]

        with patch("builtins.input", side_effect=inputs):
            with patch("builtins.print"):
                result = cli._create_new_contact()

        assert result.name == ""
        assert result.company == "Business Corp"

    def test_create_new_contact_retries_on_empty_both(
        self,
        invoice_manager: InvoiceManager,
        pdf_generator: InvoicePDFGenerator,
    ):
        """Test that creating contact retries when both name and company are empty."""
        cli = InvoiceCLI(invoice_manager, pdf_generator)

        inputs = [
            "",                  # Empty client name
            "",                  # Empty company (triggers retry)
            "Retry Client",      # Valid client name
            "",                  # No company (ok since name provided)
            "123 Retry St",      # Address
            "London",            # City
            "SW1A 1AA",         # Postcode
        ]

        with patch("builtins.input", side_effect=inputs):
            with patch("builtins.print"):
                result = cli._create_new_contact()

        assert result.name == "Retry Client"

    def test_offer_save_contact_accepts_save(
        self,
        invoice_manager: InvoiceManager,
        pdf_generator: InvoicePDFGenerator,
        tmp_path: Path,
    ):
        """Test offering to save contact when user accepts."""
        from src.contact_manager import ContactManager
        from src.models import ClientDetails

        contact_file = tmp_path / "contacts.json"
        contact_manager = ContactManager(str(contact_file))
        cli = InvoiceCLI(invoice_manager, pdf_generator, contact_manager)

        client = ClientDetails(
            name="New Client",
            company="New Corp",
            address_line1="123 New St",
            city="Newtown",
            postcode="NE1 1WN",
        )

        inputs = [
            "y",                 # Yes, save contact
            "",                  # Use default name (New Corp)
        ]

        with patch("builtins.input", side_effect=inputs):
            with patch("builtins.print"):
                cli._offer_save_contact(client)

        # Verify contact was saved
        contacts = contact_manager.get_all_contacts()
        assert len(contacts) == 1
        assert contacts[0]["contact_name"] == "New Corp"

    def test_offer_save_contact_with_custom_name(
        self,
        invoice_manager: InvoiceManager,
        pdf_generator: InvoicePDFGenerator,
        tmp_path: Path,
    ):
        """Test offering to save contact with custom name."""
        from src.contact_manager import ContactManager
        from src.models import ClientDetails

        contact_file = tmp_path / "contacts.json"
        contact_manager = ContactManager(str(contact_file))
        cli = InvoiceCLI(invoice_manager, pdf_generator, contact_manager)

        client = ClientDetails(
            name="Bob Smith",
            company="",
            address_line1="456 Custom Ave",
            city="Customville",
            postcode="CU1 1ST",
        )

        inputs = [
            "y",                 # Yes, save contact
            "Bob's Account",     # Custom contact name
        ]

        with patch("builtins.input", side_effect=inputs):
            with patch("builtins.print"):
                cli._offer_save_contact(client)

        contacts = contact_manager.get_all_contacts()
        assert len(contacts) == 1
        assert contacts[0]["contact_name"] == "Bob's Account"

    def test_offer_save_contact_declines_save(
        self,
        invoice_manager: InvoiceManager,
        pdf_generator: InvoicePDFGenerator,
        tmp_path: Path,
    ):
        """Test offering to save contact when user declines."""
        from src.contact_manager import ContactManager
        from src.models import ClientDetails

        contact_file = tmp_path / "contacts.json"
        contact_manager = ContactManager(str(contact_file))
        cli = InvoiceCLI(invoice_manager, pdf_generator, contact_manager)

        client = ClientDetails(
            name="Decline Client",
            company="",
            address_line1="789 Decline Rd",
            city="Declineton",
            postcode="DE1 1CL",
        )

        inputs = ["n"]  # No, don't save

        with patch("builtins.input", side_effect=inputs):
            with patch("builtins.print"):
                cli._offer_save_contact(client)

        # Verify no contact was saved
        contacts = contact_manager.get_all_contacts()
        assert len(contacts) == 0

    def test_offer_save_contact_skips_if_already_exists(
        self,
        invoice_manager: InvoiceManager,
        pdf_generator: InvoicePDFGenerator,
        tmp_path: Path,
    ):
        """Test that offer to save is skipped if contact already exists."""
        from src.contact_manager import ContactManager
        from src.models import ClientDetails

        contact_file = tmp_path / "contacts.json"
        contact_manager = ContactManager(str(contact_file))
        cli = InvoiceCLI(invoice_manager, pdf_generator, contact_manager)

        # Save a contact
        client = ClientDetails(
            name="Existing Client",
            company="Existing Corp",
            address_line1="Existing Address",
            city="Existing City",
            postcode="EX1 1ST",
        )
        contact_manager.save_contact(client)

        # Try to offer save for same contact (should skip without prompting)
        with patch("builtins.input") as mock_input:
            with patch("builtins.print"):
                cli._offer_save_contact(client)

        # Verify no input was requested (function returned early)
        mock_input.assert_not_called()

        # Verify still only one contact
        contacts = contact_manager.get_all_contacts()
        assert len(contacts) == 1
