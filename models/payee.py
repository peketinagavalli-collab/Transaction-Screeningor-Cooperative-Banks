"""
Payee Model (OOPJ Subject Module).
Encapsulates beneficiary details, IFSC validation, and masked banking identifiers.
"""

from typing import Optional

class Payee:
    """Represents a beneficiary or destination entity for financial transfers."""

    def __init__(
        self,
        payee_id: Optional[int],
        payee_name: str,
        bank_name: str,
        account_number: str,
        ifsc_code: str = "COOP0001001",
        created_at: Optional[str] = None
    ):
        self._payee_id = payee_id
        self._payee_name = payee_name.strip()
        self._bank_name = bank_name.strip()
        self._account_number = account_number.strip()
        self._ifsc_code = ifsc_code.strip()
        self._created_at = created_at

    @property
    def payee_id(self) -> Optional[int]:
        return self._payee_id

    @payee_id.setter
    def payee_id(self, val: int):
        self._payee_id = val

    @property
    def payee_name(self) -> str:
        return self._payee_name

    @property
    def bank_name(self) -> str:
        return self._bank_name

    @property
    def account_number(self) -> str:
        return self._account_number

    @property
    def ifsc_code(self) -> str:
        return self._ifsc_code

    @property
    def created_at(self) -> Optional[str]:
        return self._created_at

    def masked_account_number(self) -> str:
        """Returns account number masked except last 4 digits."""
        if len(self._account_number) > 4:
            return "X" * (len(self._account_number) - 4) + self._account_number[-4:]
        return self._account_number

    def to_dict(self) -> dict:
        """Serializes payee object to dictionary."""
        return {
            "payee_id": self._payee_id,
            "payee_name": self._payee_name,
            "bank_name": self._bank_name,
            "account_number": self._account_number,
            "ifsc_code": self._ifsc_code,
            "created_at": self._created_at
        }

    def __repr__(self) -> str:
        return f"<Payee id={self._payee_id} name='{self._payee_name}' bank='{self._bank_name}'>"
