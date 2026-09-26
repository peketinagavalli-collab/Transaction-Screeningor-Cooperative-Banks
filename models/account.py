"""
Account Model (OOPJ Subject Module).
Encapsulates cooperative bank account state, balance validation, and transaction limits.
"""

from typing import Optional

class Account:
    """Represents a member's bank account with state management and business rules."""

    ALLOWED_TYPES = ["Savings", "Current", "Agricultural Credit", "Recurring Deposit", "Fixed Deposit"]
    ALLOWED_STATUSES = ["Active", "Dormant", "Frozen", "Closed"]

    def __init__(
        self,
        account_id: Optional[int],
        customer_id: int,
        account_type: str = "Savings",
        balance: float = 0.0,
        account_status: str = "Active",
        created_at: Optional[str] = None
    ):
        self._account_id = account_id
        self._customer_id = customer_id
        self.account_type = account_type
        self._balance = float(balance)
        self.account_status = account_status
        self._created_at = created_at

    @property
    def account_id(self) -> Optional[int]:
        return self._account_id

    @account_id.setter
    def account_id(self, val: int):
        self._account_id = val

    @property
    def customer_id(self) -> int:
        return self._customer_id

    @property
    def account_type(self) -> str:
        return self._account_type

    @account_type.setter
    def account_type(self, val: str):
        if val not in self.ALLOWED_TYPES:
            raise ValueError(f"Invalid account type. Allowed: {self.ALLOWED_TYPES}")
        self._account_type = val

    @property
    def balance(self) -> float:
        return self._balance

    @property
    def account_status(self) -> str:
        return self._account_status

    @account_status.setter
    def account_status(self, val: str):
        if val not in self.ALLOWED_STATUSES:
            raise ValueError(f"Invalid account status. Allowed: {self.ALLOWED_STATUSES}")
        self._account_status = val

    @property
    def created_at(self) -> Optional[str]:
        return self._created_at

    def can_transact(self, amount: float) -> tuple[bool, str]:
        """Validates if the account is in good standing and has sufficient balance."""
        if self._account_status != "Active":
            return False, f"Account is {self._account_status}. Transactions are blocked."
        if amount <= 0:
            return False, "Transaction amount must be strictly greater than zero."
        if self._account_type != "Agricultural Credit" and amount > self._balance:
            return False, f"Insufficient balance (Available: ₹{self._balance:,.2f}, Requested: ₹{amount:,.2f})"
        return True, "Account eligible for transaction."

    def credit(self, amount: float):
        """Credits funds to the account balance."""
        if amount <= 0:
            raise ValueError("Credit amount must be positive.")
        self._balance += amount

    def debit(self, amount: float):
        """Debits funds from the account balance."""
        eligible, reason = self.can_transact(amount)
        if not eligible:
            raise ValueError(reason)
        self._balance -= amount

    def to_dict(self) -> dict:
        """Serializes account object to dictionary."""
        return {
            "account_id": self._account_id,
            "customer_id": self._customer_id,
            "account_type": self._account_type,
            "balance": self._balance,
            "account_status": self._account_status,
            "created_at": self._created_at
        }

    def __repr__(self) -> str:
        return f"<Account id={self._account_id} type='{self._account_type}' balance=₹{self._balance:,.2f}>"
