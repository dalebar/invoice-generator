# Invoice Generator

CLI tool for generating professional PDF invoices for a man-and-van waste removal business.

## Features

- 🚀 **Global CLI command** - Run from anywhere on your system
- 📄 **Auto-incrementing invoice numbers** (INV1001, INV1002, etc.)
- 📝 **Multiple line items** per invoice with optional quantities
- 🏢 **Business-only invoices** (no individual client name required)
- 💾 **Contact storage** - Save and reuse client details
- 📊 **Persistent tracking** - JSON-based invoice records
- 🎨 **Professional PDFs** - Detailed line item breakdown
- ⚡ **Interactive CLI** - Easy-to-use prompts and validation

## Quick Start

```bash
# Clone and setup
git clone <repository-url>
cd invoice-generator

# Install
uv venv
source .venv/bin/activate
uv pip install -e .

# Run from anywhere
invoice-generator
```

## Installation

### Prerequisites

- Python 3.9 or higher
- [uv](https://github.com/astral-sh/uv) package manager

### Setup

```bash
# Create and activate virtual environment
uv venv
source .venv/bin/activate  # On macOS/Linux
# or: .venv\Scripts\activate  # On Windows

# Install as editable package
uv pip install -e .
```

This installs the `invoice-generator` command which can be run from anywhere on your system.

### First Run

On first run, the application will automatically create:
- `data/invoice_tracker.json` - Starts at invoice number 1001
- `data/business_contacts.json` - Empty contacts list
- `invoices/` directory - For PDF output

**Note:** Make sure `config/business_details.json` exists with your business information before running.

## Usage

### Method 1: CLI Command (Recommended)

After installation, with the virtual environment activated:

```bash
invoice-generator
```

Run from anywhere on your system - the command will automatically use the project directory for configuration and output.

### Method 2: Direct Execution

From the project directory:

```bash
python main.py
```

### Method 3: Global Access (Optional)

To run `invoice-generator` without activating the venv, add this alias to your shell config (`~/.zshrc` or `~/.bashrc`):

```bash
alias invoice-generator='/path/to/invoice-generator/.venv/bin/invoice-generator'
```

Then reload your shell or run `source ~/.zshrc`.

### Interactive Workflow

The CLI will guide you through these steps:

1. **Select or create contact:**
   - Choose from saved business contacts, or
   - Enter new contact details manually

2. **Enter client details** (if creating new contact):
   - Client name (optional if company provided)
   - Company name (optional if client name provided)
   - Address details (line 1, city, postcode)

3. **Add line items:**
   - Description
   - Unit price (£)
   - Quantity (optional, defaults to 1)
   - Press Enter on description to finish adding items

4. **Payment terms:** Due on receipt or specify due date

5. **Save contact** (optional): Save the contact for future invoices

The PDF will be saved to the `invoices/` directory (in the project folder) with automatic filename generation.

### Example Line Items

```
Day Rate: 5 × £100.00 = £500.00
Transport Fee: 2 × £25.00 = £50.00
Fixed Disposal: 1 × £75.00 = £75.00
Total: £625.00
```

## Development

### Running Tests

Make sure you have the dev dependencies installed:

```bash
uv pip install -e ".[dev]"
```

Then run tests:

```bash
pytest                              # Run all tests
pytest -v                           # Verbose output
pytest --cov=src                    # With coverage report
pytest --cov=src --cov-report=html  # HTML coverage report
```

Current test coverage: **98%** (106 tests)

## Project Structure

```
invoice-generator/
├── src/
│   ├── __init__.py          # Package initialization
│   ├── __main__.py          # CLI entry point
│   ├── models.py            # Data classes
│   ├── pdf_generator.py     # PDF creation
│   ├── invoice_manager.py   # Invoice numbering & persistence
│   ├── contact_manager.py   # Business contact storage
│   └── cli.py               # Interactive CLI
├── tests/
│   ├── conftest.py          # Shared test fixtures
│   ├── test_models.py
│   ├── test_invoice_manager.py
│   ├── test_contact_manager.py
│   ├── test_pdf_generator.py
│   └── test_cli.py
├── config/
│   └── business_details.json    # Business information
├── data/
│   ├── invoice_tracker.json     # Auto-created invoice records
│   └── business_contacts.json   # Auto-created saved contacts
├── invoices/                # Output directory for PDFs
├── pyproject.toml           # Package configuration & dependencies
├── requirements.txt         # Legacy requirements file
├── main.py                  # Direct execution wrapper
└── LICENSE                  # MIT License
```

## Configuration

Edit `config/business_details.json` to update your business details. The application will automatically find this file regardless of where you run the command from.

## How It Works

The `invoice-generator` command automatically:
- Locates the project directory (where config, data, and invoices are stored)
- Changes to the project directory before executing
- Saves all invoices and data to the project location
- Restores your original working directory after completion

This means you can run `invoice-generator` from any directory on your system, and all files will be saved in the correct location.

## Managing Contacts

Business contacts are automatically saved to `data/business_contacts.json`. You can:

- **Select saved contacts:** When creating an invoice, choose from your saved contacts
- **Save new contacts:** After creating an invoice, you'll be prompted to save the contact
- **Manual editing:** Edit `data/business_contacts.json` directly to add, update, or remove contacts

Each contact stores:
- Contact name (identifier)
- Client name (optional for business-only)
- Company name
- Address line 1
- City
- Postcode

## License

MIT License - see [LICENSE](LICENSE) for details.
