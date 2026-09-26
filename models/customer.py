"""
Customer Model (OOPJ Subject Module).
Encapsulates bank member attributes, contact validation, and account linkages.
"""

from typing import Optional

class Customer:
    """Represents a member/account holder in the cooperative bank."""

    def __init__(
        self,
        customer_id: Optional[int],
        customer_name: str,
        phone: str,
        email: str,
        created_at: Optional[str] = None
    ):
        self._customer_id = customer_id
        self._customer_name = customer_name
        self._phone = phone
        self._email = email
        self._created_at = created_at

    # Property Getters and Setters (Encapsulation)
    @property
    def customer_id(self) -> Optional[int]:
        return self._customer_id

    @customer_id.setter
    def customer_id(self, val: int):
        self._customer_id = val

    @property
    def customer_name(self) -> str:
        return self._customer_name

    @customer_name.setter
    def customer_name(self, val: str):
        if not val or not val.strip():
            raise ValueError("Customer name cannot be empty.")
        self._customer_name = val.strip()

    @property
    def phone(self) -> str:
        return self._phone

    @phone.setter
    def phone(self, val: str):
        if len(val) < 10:
            raise ValueError("Phone number must have at least 10 digits.")
        self._phone = val

    @property
    def email(self) -> str:
        return self._email

    @email.setter
    def email(self, val: str):
        if "@" not in val:
            raise ValueError("Invalid email format.")
        self._email = val

    @property
    def created_at(self) -> Optional[str]:
        return self._created_at

    def masked_phone(self) -> str:
        """Returns phone number with leading digits masked for privacy (e.g., '******3210')."""
        if len(self._phone) >= 4:
            return "*" * (len(self._phone) - 4) + self._phone[-4:]
        return self._phone

    def to_dict(self) -> dict:
        """Serializes customer object to dictionary."""
        return {
            "customer_id": self._customer_id,
            "customer_name": self._customer_name,
            "phone": self._phone,
            "email": self._email,
            "created_at": self._created_at
        }

    def __repr__(self) -> str:
        return f"<Customer id={self._customer_id} name='{self._customer_name}' phone='{self.masked_phone()}'>"
