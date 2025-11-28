"""Interactive command-line interface for invoice generation."""

import re
from datetime import date
from decimal import Decimal, InvalidOperation
from typing import Callable, Optional

from .models import ClientDetails, Invoice, LineItem
from .invoice_manager import InvoiceManager
from .pdf_generator import InvoicePDFGenerator


class InvoiceCLI:
    """Interactive command-line interface."""

    def __init__(self, manager: InvoiceManager, generator: InvoicePDFGenerator):
        """
        Initialize with manager and generator.

        Args:
            manager: Invoice manager for numbering and tracking.
            generator: PDF generator for creating invoices.
        """
        self.manager = manager
        self.generator = generator

    def run_interactive(self) -> None:
        """
        Interactive mode - prompt user for invoice details and generate PDF.

        Prompts for:
        - Client name (optional for business-only)
        - Company name (optional)
        - Address line 1
        - City
        - Postcode
        - Multiple line items (description + amount)
        - Due on receipt (Y/n)
        """
        print("\n=== Invoice Generator ===\n")

        # Get client details
        print("Client Details")
        print("-" * 40)

        client_name = input("Client name (optional, press Enter to skip): ").strip()
        company = input("Company name (optional, press Enter to skip): ").strip()

        # At least one of name or company must be provided
        if not client_name and not company:
            print("  Error: Either client name or company name is required.")
            client_name = self.prompt_with_validation(
                "Client name: ",
                validator=self._validate_not_empty,
                error_msg="Client name cannot be empty.",
            )

        address_line1 = self.prompt_with_validation(
            "Address line 1: ",
            validator=self._validate_not_empty,
            error_msg="Address cannot be empty.",
        )

        city = self.prompt_with_validation(
            "City: ",
            validator=self._validate_not_empty,
            error_msg="City cannot be empty.",
        )

        postcode = self.prompt_with_validation(
            "Postcode: ",
            validator=self._validate_postcode,
            error_msg="Please enter a valid UK postcode.",
        )

        # Get line items
        print("\nLine Items")
        print("-" * 40)
        print("Enter line items (description and amount). Press Enter on description to finish.\n")

        line_items = []
        item_num = 1

        while True:
            description = input(f"Item {item_num} description (or Enter to finish): ").strip()
            if not description:
                if len(line_items) == 0:
                    print("  Error: At least one line item is required.")
                    continue
                break

            amount = self.prompt_with_validation(
                f"Item {item_num} amount (\u00a3): ",
                validator=self._validate_decimal,
                error_msg="Please enter a valid amount (e.g., 120.00).",
            )

            line_items.append(LineItem(
                description=description,
                amount=Decimal(amount)
            ))
            item_num += 1

        print()
        due_on_receipt = self.prompt_yes_no("Due on receipt? (Y/n): ", default=True)

        # Create client details
        client = ClientDetails(
            name=client_name,
            company=company,
            address_line1=address_line1,
            city=city,
            postcode=postcode.upper(),
        )

        # Get invoice number and dates
        invoice_number = self.manager.get_next_invoice_number()
        issue_date = date.today()
        due_date = issue_date if due_on_receipt else issue_date

        # Create invoice
        invoice = Invoice(
            invoice_number=invoice_number,
            issue_date=issue_date,
            due_date=due_date,
            business=self.generator.business,
            client=client,
            line_items=line_items,
        )

        # Generate filename
        name_for_file = company if company else client_name
        safe_name = self._sanitize_filename(name_for_file)
        filename = f"{invoice_number}_{safe_name}.pdf"
        output_path = f"invoices/{filename}"

        # Generate PDF
        self.generator.generate(invoice, output_path)

        # Save record
        self.manager.save_invoice_record(invoice, output_path)

        print(f"\n✓ Invoice generated successfully!")
        print(f"  File: {output_path}")
        print(f"  Invoice Number: {invoice_number}")
        print(f"  Total: \u00a3{invoice.total:.2f}")

    def prompt_with_validation(
        self,
        prompt: str,
        validator: Optional[Callable[[str], bool]] = None,
        error_msg: str = "Invalid input.",
    ) -> str:
        """
        Helper for input validation.

        Args:
            prompt: The prompt to display.
            validator: Optional validation function.
            error_msg: Error message to display on validation failure.

        Returns:
            Validated input string.
        """
        while True:
            value = input(prompt).strip()
            if validator is None or validator(value):
                return value
            print(f"  {error_msg}")

    def prompt_yes_no(self, prompt: str, default: bool = True) -> bool:
        """
        Prompt for yes/no input.

        Args:
            prompt: The prompt to display.
            default: Default value if user presses Enter.

        Returns:
            True for yes, False for no.
        """
        value = input(prompt).strip().lower()
        if not value:
            return default
        return value in ("y", "yes")

    @staticmethod
    def _validate_not_empty(value: str) -> bool:
        """Validate that value is not empty."""
        return bool(value)

    @staticmethod
    def _validate_decimal(value: str) -> bool:
        """Validate that value is a valid decimal number."""
        try:
            amount = Decimal(value)
            return amount > 0
        except InvalidOperation:
            return False

    @staticmethod
    def _validate_postcode(value: str) -> bool:
        """Validate UK postcode format (basic validation)."""
        if not value:
            return False
        # Basic UK postcode pattern
        pattern = r"^[A-Za-z]{1,2}\d[A-Za-z\d]?\s*\d[A-Za-z]{2}$"
        return bool(re.match(pattern, value.strip()))

    @staticmethod
    def _sanitize_filename(name: str) -> str:
        """
        Convert name to safe filename.

        Args:
            name: The name to sanitize.

        Returns:
            Sanitized filename-safe string.
        """
        # Replace spaces with underscores and remove unsafe characters
        safe = re.sub(r"[^\w\s-]", "", name)
        safe = re.sub(r"\s+", "_", safe)
        return safe
