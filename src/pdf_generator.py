"""PDF generation for invoices using ReportLab."""

from decimal import Decimal
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from .models import BusinessDetails, Invoice


class InvoicePDFGenerator:
    """Generates invoice PDFs using ReportLab."""

    def __init__(self, business_details: BusinessDetails):
        """
        Initialize with business details.

        Args:
            business_details: Business information for invoice header.
        """
        self.business = business_details
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self) -> None:
        """Set up custom paragraph styles for the invoice."""
        self.styles.add(
            ParagraphStyle(
                "InvoiceTitle",
                parent=self.styles["Heading1"],
                fontSize=28,
                alignment=2,  # Right align
                spaceAfter=20,
                fontName="Helvetica-Bold",
            )
        )
        self.styles.add(
            ParagraphStyle(
                "SectionHeader",
                parent=self.styles["Normal"],
                fontSize=10,
                fontName="Helvetica-Bold",
                textColor=colors.grey,
                spaceAfter=5,
            )
        )
        self.styles.add(
            ParagraphStyle(
                "AddressText",
                parent=self.styles["Normal"],
                fontSize=10,
                fontName="Helvetica",
                leading=14,
            )
        )
        self.styles.add(
            ParagraphStyle(
                "DetailLabel",
                parent=self.styles["Normal"],
                fontSize=10,
                fontName="Helvetica-Bold",
            )
        )
        self.styles.add(
            ParagraphStyle(
                "DetailValue",
                parent=self.styles["Normal"],
                fontSize=10,
                fontName="Helvetica",
            )
        )
        self.styles.add(
            ParagraphStyle(
                "Footer",
                parent=self.styles["Normal"],
                fontSize=10,
                fontName="Helvetica",
                alignment=0,  # Left align
                leading=14,
            )
        )

    def generate(self, invoice: Invoice, output_path: str) -> None:
        """
        Generate PDF invoice matching template style.

        Args:
            invoice: Invoice data to render.
            output_path: Path where PDF will be saved.
        """
        # Ensure output directory exists
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=20 * mm,
            leftMargin=20 * mm,
            topMargin=20 * mm,
            bottomMargin=20 * mm,
        )

        story = []

        # Title
        story.append(Paragraph("INVOICE", self.styles["InvoiceTitle"]))
        story.append(Spacer(1, 10 * mm))

        # From/To section
        story.append(self._create_address_section(invoice))
        story.append(Spacer(1, 8 * mm))

        # Invoice details
        story.append(self._create_invoice_details(invoice))
        story.append(Spacer(1, 8 * mm))

        # Description table
        story.append(self._create_description_table(invoice))
        story.append(Spacer(1, 5 * mm))

        # Totals
        story.append(self._create_totals_section(invoice))
        story.append(Spacer(1, 15 * mm))

        # Footer
        story.append(self._create_footer(invoice))

        doc.build(story)

    def _create_address_section(self, invoice: Invoice) -> Table:
        """Create the From/To address section."""
        # Build From address
        from_lines = [
            Paragraph("<b>From:</b>", self.styles["SectionHeader"]),
            Paragraph(self.business.name, self.styles["AddressText"]),
            Paragraph(self.business.address_line1, self.styles["AddressText"]),
            Paragraph(self.business.city, self.styles["AddressText"]),
            Paragraph(self.business.postcode, self.styles["AddressText"]),
            Paragraph(self.business.email, self.styles["AddressText"]),
        ]

        # Build To address
        to_lines = [Paragraph("<b>To:</b>", self.styles["SectionHeader"])]

        # Add name and/or company (at least one must exist)
        if invoice.client.name:
            to_lines.append(Paragraph(invoice.client.name, self.styles["AddressText"]))
        if invoice.client.company:
            to_lines.append(Paragraph(invoice.client.company, self.styles["AddressText"]))

        to_lines.extend(
            [
                Paragraph(invoice.client.address_line1, self.styles["AddressText"]),
                Paragraph(invoice.client.city, self.styles["AddressText"]),
                Paragraph(invoice.client.postcode, self.styles["AddressText"]),
            ]
        )

        # Pad shorter column
        max_lines = max(len(from_lines), len(to_lines))
        while len(from_lines) < max_lines:
            from_lines.append(Paragraph("", self.styles["AddressText"]))
        while len(to_lines) < max_lines:
            to_lines.append(Paragraph("", self.styles["AddressText"]))

        # Create table with two columns
        data = list(zip(from_lines, to_lines))
        table = Table(data, colWidths=[85 * mm, 85 * mm])
        table.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                    ("TOPPADDING", (0, 0), (-1, -1), 0),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
                ]
            )
        )
        return table

    def _create_invoice_details(self, invoice: Invoice) -> Table:
        """Create the invoice details section."""
        date_format = "%d/%m/%Y"
        payment_terms = "Due on receipt" if invoice.issue_date == invoice.due_date else f"Due by {invoice.due_date.strftime(date_format)}"

        details = [
            ("Invoice Number:", invoice.invoice_number),
            ("Issue Date:", invoice.issue_date.strftime(date_format)),
            ("Due Date:", invoice.due_date.strftime(date_format)),
            ("Payment Terms:", payment_terms),
        ]

        data = [
            [
                Paragraph(f"<b>{label}</b>", self.styles["DetailLabel"]),
                Paragraph(value, self.styles["DetailValue"]),
            ]
            for label, value in details
        ]

        table = Table(data, colWidths=[35 * mm, 60 * mm], hAlign="LEFT")
        table.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ]
            )
        )
        return table

    def _create_description_table(self, invoice: Invoice) -> Table:
        """Create the description and amount table with line items."""
        # Header row
        data = [["Description", "Qty", "Unit Price (GBP)", "Total (GBP)"]]

        # Add each line item
        for item in invoice.line_items:
            data.append([
                item.description,
                str(item.quantity),
                f"\u00a3{item.amount:.2f}",
                f"\u00a3{item.line_total:.2f}"
            ])

        table = Table(data, colWidths=[95 * mm, 15 * mm, 30 * mm, 30 * mm])
        table.setStyle(
            TableStyle(
                [
                    # Header row
                    ("BACKGROUND", (0, 0), (-1, 0), colors.Color(0.9, 0.9, 0.9)),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 10),
                    # Alignment
                    ("ALIGN", (1, 0), (1, -1), "CENTER"),  # Qty column centered
                    ("ALIGN", (2, 0), (2, -1), "RIGHT"),   # Unit Price right
                    ("ALIGN", (3, 0), (3, -1), "RIGHT"),   # Total right
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    # Borders
                    ("BOX", (0, 0), (-1, -1), 0.5, colors.black),
                    ("LINEBELOW", (0, 0), (-1, 0), 0.5, colors.black),
                    # Padding
                    ("LEFTPADDING", (0, 0), (-1, -1), 8),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                    ("TOPPADDING", (0, 0), (-1, -1), 8),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ]
            )
        )
        return table

    def _create_totals_section(self, invoice: Invoice) -> Table:
        """Create the subtotal, VAT, and total section."""
        data = [
            ["Subtotal:", f"\u00a3{invoice.subtotal:.2f}"],
            ["VAT:", invoice.vat_status],
            ["Total:", f"\u00a3{invoice.total:.2f}"],
        ]

        table = Table(data, colWidths=[130 * mm, 40 * mm])
        table.setStyle(
            TableStyle(
                [
                    ("ALIGN", (0, 0), (0, -1), "RIGHT"),
                    ("ALIGN", (1, 0), (1, -1), "RIGHT"),
                    ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 10),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ]
            )
        )
        return table

    def _create_footer(self, invoice: Invoice) -> Paragraph:
        """Create the footer with payment details."""
        footer_text = (
            f"Many thanks and kind regards,<br/>"
            f"{self.business.name}<br/>"
            f"{self.business.sort_code}<br/>"
            f"{self.business.account_number}"
        )
        return Paragraph(footer_text, self.styles["Footer"])
