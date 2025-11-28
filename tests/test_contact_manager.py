"""Tests for the ContactManager."""

import json
from pathlib import Path

import pytest

from src.contact_manager import ContactManager
from src.models import ClientDetails


class TestContactManager:
    """Tests for ContactManager initialization and file handling."""

    def test_init_creates_data_file(self, tmp_path: Path):
        """Test that initialization creates the data file."""
        data_file = tmp_path / "test_contacts.json"
        manager = ContactManager(str(data_file))

        assert data_file.exists()
        with open(data_file, "r") as f:
            data = json.load(f)
        assert data == {"contacts": []}

    def test_init_with_existing_file(self, tmp_path: Path):
        """Test initialization with existing data file."""
        data_file = tmp_path / "contacts.json"
        existing_data = {
            "contacts": [
                {
                    "contact_name": "Test Client",
                    "name": "John Doe",
                    "company": "",
                    "address_line1": "123 Test St",
                    "city": "London",
                    "postcode": "SW1A 1AA",
                }
            ]
        }

        data_file.parent.mkdir(parents=True, exist_ok=True)
        with open(data_file, "w") as f:
            json.dump(existing_data, f)

        manager = ContactManager(str(data_file))
        contacts = manager.get_all_contacts()

        assert len(contacts) == 1
        assert contacts[0]["contact_name"] == "Test Client"


class TestLoadContacts:
    """Tests for loading contacts."""

    def test_load_empty_contacts(self, tmp_path: Path):
        """Test loading when no contacts exist."""
        data_file = tmp_path / "contacts.json"
        manager = ContactManager(str(data_file))

        data = manager.load_contacts()
        assert data == {"contacts": []}

    def test_load_with_contacts(self, tmp_path: Path):
        """Test loading existing contacts."""
        data_file = tmp_path / "contacts.json"
        manager = ContactManager(str(data_file))

        # Add a contact
        client = ClientDetails(
            name="Jane Smith",
            company="Smith Ltd",
            address_line1="456 Business Ave",
            city="Manchester",
            postcode="M1 1AA",
        )
        manager.save_contact(client)

        # Load and verify
        data = manager.load_contacts()
        assert len(data["contacts"]) == 1
        assert data["contacts"][0]["name"] == "Jane Smith"

    def test_load_handles_corrupted_file(self, tmp_path: Path):
        """Test that corrupted JSON is handled gracefully."""
        data_file = tmp_path / "contacts.json"
        data_file.parent.mkdir(parents=True, exist_ok=True)

        # Write invalid JSON
        with open(data_file, "w") as f:
            f.write("invalid json {{{")

        manager = ContactManager(str(data_file))
        data = manager.load_contacts()

        # Should return default structure
        assert data == {"contacts": []}


class TestSaveContact:
    """Tests for saving contacts."""

    def test_save_new_contact_with_name(self, tmp_path: Path):
        """Test saving a new contact with client name."""
        data_file = tmp_path / "contacts.json"
        manager = ContactManager(str(data_file))

        client = ClientDetails(
            name="John Doe",
            company="",
            address_line1="123 Test St",
            city="London",
            postcode="SW1A 1AA",
        )

        manager.save_contact(client)

        contacts = manager.get_all_contacts()
        assert len(contacts) == 1
        assert contacts[0]["contact_name"] == "John Doe"
        assert contacts[0]["name"] == "John Doe"
        assert contacts[0]["company"] == ""

    def test_save_new_contact_with_company(self, tmp_path: Path):
        """Test saving a new contact with company name."""
        data_file = tmp_path / "contacts.json"
        manager = ContactManager(str(data_file))

        client = ClientDetails(
            name="",
            company="Acme Corp",
            address_line1="789 Corporate Blvd",
            city="Birmingham",
            postcode="B33 8TH",
        )

        manager.save_contact(client)

        contacts = manager.get_all_contacts()
        assert len(contacts) == 1
        assert contacts[0]["contact_name"] == "Acme Corp"
        assert contacts[0]["company"] == "Acme Corp"

    def test_save_contact_with_custom_name(self, tmp_path: Path):
        """Test saving contact with custom contact name."""
        data_file = tmp_path / "contacts.json"
        manager = ContactManager(str(data_file))

        client = ClientDetails(
            name="Bob Smith",
            company="Smith & Co",
            address_line1="100 Main St",
            city="Leeds",
            postcode="LS1 1AA",
        )

        manager.save_contact(client, contact_name="Bob's Company")

        contacts = manager.get_all_contacts()
        assert len(contacts) == 1
        assert contacts[0]["contact_name"] == "Bob's Company"

    def test_update_existing_contact(self, tmp_path: Path):
        """Test updating an existing contact."""
        data_file = tmp_path / "contacts.json"
        manager = ContactManager(str(data_file))

        # Save initial contact
        client1 = ClientDetails(
            name="Alice Jones",
            company="Jones Ltd",
            address_line1="Old Address",
            city="Sheffield",
            postcode="S1 1AA",
        )
        manager.save_contact(client1)

        # Update with new address
        client2 = ClientDetails(
            name="Alice Jones",
            company="Jones Ltd",
            address_line1="New Address",
            city="Sheffield",
            postcode="S2 2BB",
        )
        manager.save_contact(client2)

        # Verify only one contact exists with updated info
        contacts = manager.get_all_contacts()
        assert len(contacts) == 1
        assert contacts[0]["address_line1"] == "New Address"
        assert contacts[0]["postcode"] == "S2 2BB"


class TestGetContact:
    """Tests for retrieving contacts."""

    def test_get_existing_contact(self, tmp_path: Path):
        """Test retrieving an existing contact."""
        data_file = tmp_path / "contacts.json"
        manager = ContactManager(str(data_file))

        # Save contact
        client = ClientDetails(
            name="Test User",
            company="Test Corp",
            address_line1="123 Test Ave",
            city="Testville",
            postcode="TE1 1ST",
        )
        manager.save_contact(client, "Test Contact")

        # Retrieve contact
        retrieved = manager.get_contact("Test Contact")

        assert retrieved is not None
        assert retrieved.name == "Test User"
        assert retrieved.company == "Test Corp"
        assert retrieved.postcode == "TE1 1ST"

    def test_get_nonexistent_contact(self, tmp_path: Path):
        """Test retrieving a contact that doesn't exist."""
        data_file = tmp_path / "contacts.json"
        manager = ContactManager(str(data_file))

        result = manager.get_contact("Nonexistent")
        assert result is None


class TestGetAllContacts:
    """Tests for getting all contacts."""

    def test_get_all_with_no_contacts(self, tmp_path: Path):
        """Test getting all contacts when none exist."""
        data_file = tmp_path / "contacts.json"
        manager = ContactManager(str(data_file))

        contacts = manager.get_all_contacts()
        assert contacts == []

    def test_get_all_with_multiple_contacts(self, tmp_path: Path):
        """Test getting all contacts."""
        data_file = tmp_path / "contacts.json"
        manager = ContactManager(str(data_file))

        # Add multiple contacts
        clients = [
            ClientDetails("Client 1", "", "Addr 1", "City 1", "M1 1AA"),
            ClientDetails("", "Company 2", "Addr 2", "City 2", "M2 2BB"),
            ClientDetails("Client 3", "Company 3", "Addr 3", "City 3", "M3 3CC"),
        ]

        for client in clients:
            manager.save_contact(client)

        contacts = manager.get_all_contacts()
        assert len(contacts) == 3


class TestDeleteContact:
    """Tests for deleting contacts."""

    def test_delete_existing_contact(self, tmp_path: Path):
        """Test deleting an existing contact."""
        data_file = tmp_path / "contacts.json"
        manager = ContactManager(str(data_file))

        # Add contact
        client = ClientDetails(
            name="Delete Me",
            company="",
            address_line1="123 Del St",
            city="Deltown",
            postcode="DE1 1TE",
        )
        manager.save_contact(client)

        # Verify it exists
        assert len(manager.get_all_contacts()) == 1

        # Delete it
        result = manager.delete_contact("Delete Me")
        assert result is True

        # Verify it's gone
        assert len(manager.get_all_contacts()) == 0

    def test_delete_nonexistent_contact(self, tmp_path: Path):
        """Test deleting a contact that doesn't exist."""
        data_file = tmp_path / "contacts.json"
        manager = ContactManager(str(data_file))

        result = manager.delete_contact("Nonexistent")
        assert result is False

    def test_delete_one_of_multiple_contacts(self, tmp_path: Path):
        """Test deleting one contact when multiple exist."""
        data_file = tmp_path / "contacts.json"
        manager = ContactManager(str(data_file))

        # Add multiple contacts
        for i in range(3):
            client = ClientDetails(
                name=f"Client {i}",
                company="",
                address_line1=f"Addr {i}",
                city=f"City {i}",
                postcode="M1 1AA",
            )
            manager.save_contact(client)

        # Delete one
        manager.delete_contact("Client 1")

        # Verify correct one was deleted
        contacts = manager.get_all_contacts()
        assert len(contacts) == 2
        names = [c["contact_name"] for c in contacts]
        assert "Client 1" not in names
        assert "Client 0" in names
        assert "Client 2" in names
