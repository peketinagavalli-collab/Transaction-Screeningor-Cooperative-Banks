"""
Transaction Model (OOPJ Subject Module).
Encapsulates financial transaction attributes, timestamps, and execution parameters.
"""

from typing import Optional

class Transaction:
    """Represents a transaction event processed by the cooperative bank."""

    ALLOWED_TYPES = ["Transfer", "Withdrawal", "Deposit", "UPI", "NEFT", "RTGS", "IMPS"]
    ALLOWED_STATUSES = ["Completed", "Pending", "Flagged", "Rejected", "Under Review"]

    def __init__(
        self,
        transaction_id: Optional[int],
        account_id: int,
        amount: float,
        transaction_type: str = "Transfer",
        payee_id: Optional[int] = None,
        transaction_date: Optional[str] = None,
        location: str = "Main Branch",
        status: str = "Completed"
    ):
        self._transaction_id = transaction_id
        self._account_id = account_id
        self._payee_id = payee_id
        self._amount = float(amount)
        self.transaction_type = transaction_type
        self._transaction_date = transaction_date
        self._location = location
        self.status = status

    @property
    def transaction_id(self) -> Optional[int]:
        return self._transaction_id

    @transaction_id.setter
    def transaction_id(self, val: int):
        self._transaction_id = val

    @property
    def account_id(self) -> int:
        return self._account_id

    @property
    def payee_id(self) -> Optional[int]:
        return self._payee_id

    @property
    def amount(self) -> float:
        return self._amount

    @amount.setter
    def amount(self, val: float):
        if val <= 0:
            raise ValueError("Transaction amount must be strictly positive.")
        self._amount = float(val)

    @property
    def transaction_type(self) -> str:
        return self._transaction_type

    @transaction_type.setter
    def transaction_type(self, val: str):
        if val not in self.ALLOWED_TYPES:
            raise ValueError(f"Invalid transaction type: '{val}'. Allowed: {self.ALLOWED_TYPES}")
        self._transaction_type = val

    @property
    def transaction_date(self) -> Optional[str]:
        return self._transaction_date

    @property
    def location(self) -> str:
        return self._location

    @property
    def status(self) -> str:
        return self._status

    @status.setter
    def status(self, val: str):
        if val not in self.ALLOWED_STATUSES:
            raise ValueError(f"Invalid status: '{val}'. Allowed: {self.ALLOWED_STATUSES}")
        self._status = val

    def to_dict(self) -> dict:
        """Serializes transaction object to dictionary."""
        return {
            "transaction_id": self._transaction_id,
            "account_id": self._account_id,
            "payee_id": self._payee_id,
            "amount": self._amount,
            "transaction_type": self._transaction_type,
            "transaction_date": self._transaction_date,
            "location": self._location,
            "status": self._status
        }

    def __repr__(self) -> str:
        return f"<Transaction id={self._transaction_id} acc={self._account_id} amt=₹{self._amount:,.2f} status='{self._status}'>"
