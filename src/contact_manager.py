"""Business contact management for storing and retrieving client details."""

import json
from pathlib import Path
from typing import Any, Optional

from .models import ClientDetails


class ContactManager:
    """Manages business contact storage and retrieval."""

    def __init__(self, data_file: str = "data/business_contacts.json"):
        """
        Initialize contact manager.

        Args:
            data_file: Path to the contacts JSON file.
        """
        self.data_file = Path(data_file)
        self._ensure_data_file_exists()

    def _ensure_data_file_exists(self) -> None:
        """Create the data directory and file if they don't exist."""
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        if not self.data_file.exists():
            self._save_contacts({"contacts": []})

    def load_contacts(self) -> dict[str, Any]:
        """
        Load existing contacts.

        Returns:
            Dictionary containing contacts data.
        """
        try:
            with open(self.data_file, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            default_contacts = {"contacts": []}
            self._save_contacts(default_contacts)
            return default_contacts

    def _save_contacts(self, data: dict[str, Any]) -> None:
        """
        Save contacts data to file.

        Args:
            data: Contacts data to save.
        """
        with open(self.data_file, "w") as f:
            json.dump(data, f, indent=4)

    def get_all_contacts(self) -> list[dict[str, str]]:
        """
        Get all saved contacts.

        Returns:
            List of contact dictionaries.
        """
        data = self.load_contacts()
        return data.get("contacts", [])

    def save_contact(self, client: ClientDetails, contact_name: Optional[str] = None) -> None:
        """
        Save a contact to the storage.

        Args:
            client: ClientDetails to save.
            contact_name: Optional name for the contact. If not provided,
                         uses company name or client name.
        """
        data = self.load_contacts()

        # Determine contact identifier
        if not contact_name:
            contact_name = client.company or client.name

        # Check if contact already exists
        existing_contacts = data.get("contacts", [])
        for contact in existing_contacts:
            if contact.get("contact_name") == contact_name:
                # Update existing contact
                contact["name"] = client.name
                contact["company"] = client.company
                contact["address_line1"] = client.address_line1
                contact["city"] = client.city
                contact["postcode"] = client.postcode
                self._save_contacts(data)
                return

        # Add new contact
        contact_record = {
            "contact_name": contact_name,
            "name": client.name,
            "company": client.company,
            "address_line1": client.address_line1,
            "city": client.city,
            "postcode": client.postcode,
        }

        data["contacts"].append(contact_record)
        self._save_contacts(data)

    def get_contact(self, contact_name: str) -> Optional[ClientDetails]:
        """
        Retrieve a contact by name.

        Args:
            contact_name: Name of the contact to retrieve.

        Returns:
            ClientDetails if found, None otherwise.
        """
        contacts = self.get_all_contacts()
        for contact in contacts:
            if contact.get("contact_name") == contact_name:
                return ClientDetails(
                    name=contact["name"],
                    company=contact["company"],
                    address_line1=contact["address_line1"],
                    city=contact["city"],
                    postcode=contact["postcode"],
                )
        return None

    def delete_contact(self, contact_name: str) -> bool:
        """
        Delete a contact by name.

        Args:
            contact_name: Name of the contact to delete.

        Returns:
            True if contact was deleted, False if not found.
        """
        data = self.load_contacts()
        contacts = data.get("contacts", [])

        for i, contact in enumerate(contacts):
            if contact.get("contact_name") == contact_name:
                contacts.pop(i)
                self._save_contacts(data)
                return True

        return False
