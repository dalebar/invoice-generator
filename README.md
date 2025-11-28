# Invoice Generator

CLI tool for generating professional PDF invoices for a man-and-van waste removal business.

## Features

- Auto-incrementing invoice numbers (INV1001, INV1002, etc.)
- Multiple line items per invoice with optional quantities
- Support for business-only invoices (no individual client name required)
- Business contact storage - save and reuse client details
- Persistent invoice tracking with JSON storage
- Professional PDF output with detailed line item breakdown
- Interactive CLI for easy invoice creation

## Installation

```bash
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

## Usage

```bash
python main.py
```

Follow the interactive prompts:

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

The PDF will be saved to the `invoices/` directory with automatic filename generation.

### Example Line Items

```
Day Rate: 5 × £100.00 = £500.00
Transport Fee: 2 × £25.00 = £50.00
Fixed Disposal: 1 × £75.00 = £75.00
Total: £625.00
```

## Testing

```bash
pytest                              # Run all tests
pytest -v                           # Verbose output
pytest --cov=src                    # With coverage report
pytest --cov=src --cov-report=html  # HTML coverage report
```

## Project Structure

```
invoice-generator/
├── src/
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
├── requirements.txt
└── main.py                  # Entry point
```

## Configuration

Edit `config/business_details.json` to update business details.

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
