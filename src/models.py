"""Data models for the invoice generator."""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass
class BusinessDetails:
    """Business information for invoice header and payment details."""

    name: str
    address_line1: str
    city: str
    postcode: str
    email: str
    sort_code: str
    account_number: str


@dataclass
class ClientDetails:
    """Client information for invoice recipient."""

    name: str  # Can be empty string for business-only invoices
    company: str  # Can be empty string
    address_line1: str
    city: str
    postcode: str


@dataclass
class LineItem:
    """Individual line item on an invoice."""

    description: str
    amount: Decimal


@dataclass
class Invoice:
    """Complete invoice data including business, client, and transaction details."""

    invoice_number: str
    issue_date: date
    due_date: date
    business: BusinessDetails
    client: ClientDetails
    line_items: list[LineItem]
    vat_status: str = "No VAT"

    @property
    def subtotal(self) -> Decimal:
        """Calculate subtotal from all line items."""
        return sum(item.amount for item in self.line_items)

    @property
    def total(self) -> Decimal:
        """Calculate total amount (currently same as subtotal since no VAT)."""
        return self.subtotal
