# Invoice Generator - Build Specification

## Project Overview
CLI tool for generating professional PDF invoices for a man-and-van waste removal business. Must auto-increment invoice numbers, maintain records, and produce PDFs matching the existing template style.

## Tech Stack
- Python 3.9+
- ReportLab for PDF generation
- JSON for data persistence
- Type hints throughout
- Clean, documented, testable code

## Project Structure
```
invoice-generator/
├── src/
│   ├── __init__.py
│   ├── models.py          # Data classes with type hints
│   ├── pdf_generator.py   # PDF creation using ReportLab
│   ├── invoice_manager.py # Invoice numbering & persistence
│   └── cli.py            # Interactive CLI interface
├── config/
│   └── business_details.json  # Business information
├── data/
│   └── invoice_tracker.json   # Auto-created, tracks invoice numbers
├── invoices/              # Output directory for PDFs
├── requirements.txt
├── README.md
├── .gitignore
└── main.py               # Entry point
```

## Data Models (models.py)

### BusinessDetails
```python
@dataclass
class BusinessDetails:
    name: str
    address_line1: str
    address_line2: str
    city: str
    postcode: str
    email: str
    sort_code: str
    account_number: str
```

### ClientDetails
```python
@dataclass
class ClientDetails:
    name: str
    company: str  # Can be empty string
    address_line1: str
    city: str
    postcode: str
```

### Invoice
```python
@dataclass
class Invoice:
    invoice_number: str
    issue_date: date
    due_date: date
    business: BusinessDetails
    client: ClientDetails
    description: str
    amount: Decimal
    vat_status: str = "No VAT"
    
    @property
    def total(self) -> Decimal:
        return self.amount
```

## Invoice Manager (invoice_manager.py)

Handles invoice numbering and record-keeping:
```python
class InvoiceManager:
    """Manages invoice numbering and tracking"""
    
    def __init__(self, data_file: str = "data/invoice_tracker.json"):
        """Initialize manager, create data file if doesn't exist"""
        
    def get_next_invoice_number(self) -> str:
        """
        Returns next invoice number in format 'INV1001', 'INV1002', etc.
        Starts at INV1001 if no previous invoices exist.
        """
        
    def save_invoice_record(self, invoice: Invoice) -> None:
        """
        Saves invoice metadata to tracker JSON file.
        Stores: invoice_number, client_name, amount, date, file_path
        """
        
    def load_tracker(self) -> dict:
        """Load existing tracker or create new one"""
```

Tracker JSON format:
```json
{
    "last_invoice_number": 1002,
    "invoices": [
        {
            "invoice_number": "INV1001",
            "client": "Client Name",
            "amount": "120.00",
            "date": "2025-11-24",
            "file_path": "invoices/INV1001_Client_Name.pdf"
        }
    ]
}
```

## PDF Generator (pdf_generator.py)

Creates professional PDFs matching the reference template:
```python
class InvoicePDFGenerator:
    """Generates invoice PDFs using ReportLab"""
    
    def __init__(self, business_details: BusinessDetails):
        """Initialize with business details"""
        
    def generate(self, invoice: Invoice, output_path: str) -> None:
        """
        Generate PDF invoice matching template style.
        
        Layout requirements:
        - A4 page size
        - "INVOICE" title at top (bold, large)
        - Two-column layout: "From:" (left) and "To:" (right)
        - Invoice details: Number, Issue Date, Due Date, Payment Terms
        - Table with Description and Amount columns
        - Subtotal, VAT status, Total
        - Footer with business name, sort code, account number
        
        Use clean, professional styling matching reference invoice.
        """
```

## CLI Interface (cli.py)

Interactive prompts for invoice creation:
```python
class InvoiceCLI:
    """Interactive command-line interface"""
    
    def __init__(self, manager: InvoiceManager, generator: InvoicePDFGenerator):
        """Initialize with manager and generator"""
        
    def run_interactive(self) -> None:
        """
        Interactive mode - prompt user for:
        - Client name
        - Company name (optional, can be empty)
        - Address line 1
        - City
        - Postcode
        - Job description
        - Amount (validate as decimal)
        - Due on receipt? (Y/n) - defaults to Y
        
        Then generate PDF and show success message with file path.
        """
        
    def prompt_with_validation(self, prompt: str, validator=None) -> str:
        """Helper for input validation"""
```

## Main Entry Point (main.py)
```python
def main():
    """
    Entry point:
    1. Load business details from config/business_details.json
    2. Initialize InvoiceManager
    3. Initialize InvoicePDFGenerator
    4. Initialize InvoiceCLI
    5. Run interactive mode
    
    Handle errors gracefully with user-friendly messages.
    """

if __name__ == "__main__":
    main()
```

## Configuration File

Create `config/business_details.json`:
```json
{
    "name": "Dale Barnes",
    "address_line1": "Flat D",
    "address_line2": "216 Wellington Road North",
    "city": "Stockport",
    "postcode": "SK4 2QN",
    "email": "dalewithvan@gmail.com",
    "sort_code": "04-00-04",
    "account_number": "53377826"
}
```

## Reference Invoice Template

The PDF should match this layout:
```
                              INVOICE

From:                                   To:
Dale Barnes                             [Client Name]
Flat D                                  [Company Name]
216 Wellington Road North               [Address]
Stockport                               [City]
SK4 2QN                                 [Postcode]
dalewithvan@gmail.com

Invoice Number:    INV1001
Issue Date:        24/11/2025
Due Date:          24/11/2025
Payment Terms:     Due on receipt

┌───────────────────────────────────────────────┬──────────────┐
│ Description                                   │ Amount (GBP) │
├───────────────────────────────────────────────┼──────────────┤
│ [Job description]                             │ £[amount]    │
└───────────────────────────────────────────────┴──────────────┘

Subtotal:                                          £[amount]
VAT:                                               No VAT
Total:                                             £[amount]

Many thanks and kind regards,
Dale Barnes
04-00-04
53377826
```

## File Naming Convention

Generated PDFs should be named:
`INV[number]_[Client_Company_Name].pdf`

Example: `INV1001_Holker_Mansions_Ltd.pdf`

If no company name, use client name: `INV1001_Matt_Holker.pdf`

## Error Handling

- Validate all user inputs
- Handle missing config files gracefully
- Create directories if they don't exist
- Provide clear error messages
- Handle decimal/currency validation

## Implementation Priority

1. models.py - Data structures
2. invoice_manager.py - Numbering system
3. pdf_generator.py - PDF creation
4. cli.py - User interface
5. main.py - Tie it together
6. Test with sample invoices

## Success Criteria

- Generates PDFs matching reference style
- Auto-increments invoice numbers correctly
- Maintains persistent records
- Clean, type-hinted, documented code
- No external dependencies beyond requirements.txt
- Professional output suitable for actual business use