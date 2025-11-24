#!/usr/bin/env python3
"""Entry point for the Invoice Generator CLI."""

import json
import sys
from pathlib import Path

from src.models import BusinessDetails
from src.invoice_manager import InvoiceManager
from src.pdf_generator import InvoicePDFGenerator
from src.cli import InvoiceCLI


def load_business_details(config_path: str = "config/business_details.json") -> BusinessDetails:
    """
    Load business details from configuration file.

    Args:
        config_path: Path to the business details JSON file.

    Returns:
        BusinessDetails instance.

    Raises:
        FileNotFoundError: If config file doesn't exist.
        ValueError: If config file is invalid.
    """
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(
            f"Configuration file not found: {config_path}\n"
            "Please create the file with your business details."
        )

    try:
        with open(path, "r") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in configuration file: {e}")

    required_fields = [
        "name", "address_line1", "address_line2", "city",
        "postcode", "email", "sort_code", "account_number"
    ]

    missing = [field for field in required_fields if field not in data]
    if missing:
        raise ValueError(f"Missing required fields in config: {', '.join(missing)}")

    return BusinessDetails(
        name=data["name"],
        address_line1=data["address_line1"],
        address_line2=data["address_line2"],
        city=data["city"],
        postcode=data["postcode"],
        email=data["email"],
        sort_code=data["sort_code"],
        account_number=data["account_number"],
    )


def main() -> None:
    """
    Entry point for the invoice generator.

    1. Load business details from config
    2. Initialize InvoiceManager
    3. Initialize InvoicePDFGenerator
    4. Initialize InvoiceCLI
    5. Run interactive mode
    """
    try:
        # Load business details
        business = load_business_details()

        # Initialize components
        manager = InvoiceManager()
        generator = InvoicePDFGenerator(business)
        cli = InvoiceCLI(manager, generator)

        # Run interactive mode
        cli.run_interactive()

    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Configuration error: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nCancelled.")
        sys.exit(0)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
