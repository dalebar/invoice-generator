#!/usr/bin/env python3
"""Entry point for the Invoice Generator CLI."""

import json
import os
import sys
from pathlib import Path

from .models import BusinessDetails
from .invoice_manager import InvoiceManager
from .pdf_generator import InvoicePDFGenerator
from .cli import InvoiceCLI

# Get the project root directory (parent of src/)
PROJECT_ROOT = Path(__file__).parent.parent


def load_business_details(config_path: str = None) -> BusinessDetails:
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
    if config_path is None:
        config_path = PROJECT_ROOT / "config" / "business_details.json"
    else:
        config_path = Path(config_path)

    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(
            f"Configuration file not found: {path}\n"
            "Please create the file with your business details."
        )

    try:
        with open(path, "r") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in configuration file: {e}")

    required_fields = [
        "name", "address_line1", "city",
        "postcode", "email", "sort_code", "account_number"
    ]

    missing = [field for field in required_fields if field not in data]
    if missing:
        raise ValueError(f"Missing required fields in config: {', '.join(missing)}")

    return BusinessDetails(
        name=data["name"],
        address_line1=data["address_line1"],
        city=data["city"],
        postcode=data["postcode"],
        email=data["email"],
        sort_code=data["sort_code"],
        account_number=data["account_number"],
    )


def main() -> None:
    """
    Entry point for the invoice generator.

    1. Change to project directory
    2. Load business details from config
    3. Initialize InvoiceManager
    4. Initialize InvoicePDFGenerator
    5. Initialize InvoiceCLI
    6. Run interactive mode
    """
    # Save original directory
    original_cwd = os.getcwd()

    try:
        # Change to project directory so relative paths work
        os.chdir(PROJECT_ROOT)

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
    finally:
        # Restore original directory
        os.chdir(original_cwd)


if __name__ == "__main__":
    main()
