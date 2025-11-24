# Invoice Generator

CLI tool for generating professional PDF invoices for a man-and-van waste removal business.

## Features

- Auto-incrementing invoice numbers (INV1001, INV1002, etc.)
- Persistent invoice tracking
- Professional PDF output
- Interactive CLI for easy invoice creation

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python main.py
```

Follow the interactive prompts to enter:
- Client name
- Company name (optional)
- Address details
- Job description
- Amount

The PDF will be saved to the `invoices/` directory.

## Project Structure

```
invoice-generator/
├── src/
│   ├── models.py          # Data classes
│   ├── pdf_generator.py   # PDF creation
│   ├── invoice_manager.py # Invoice numbering & persistence
│   └── cli.py             # Interactive CLI
├── config/
│   └── business_details.json  # Business information
├── data/
│   └── invoice_tracker.json   # Auto-created invoice records
├── invoices/              # Output directory for PDFs
├── requirements.txt
└── main.py                # Entry point
```

## Configuration

Edit `config/business_details.json` to update business details.
