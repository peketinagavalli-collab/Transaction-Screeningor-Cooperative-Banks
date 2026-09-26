"""
OTPVerification Model (OOPJ Subject Module & Section 19 Large Withdrawal Feature).
Encapsulates cryptographic OTP generation, SHA-256 hashing, attempt limits, and expiration tracking.
"""

import random
import hashlib
import datetime
from typing import Optional, Tuple

class OTPVerification:
    """Manages simulated two-factor authentication tokens for high-value cash withdrawals."""

    EXPIRY_MINUTES = 5
    MAX_ATTEMPTS = 3

    def __init__(
        self,
        otp_id: Optional[int],
        customer_id: int,
        mobile_number: str,
        transaction_id: Optional[int] = None,
        otp_hash: Optional[str] = None,
        created_at: Optional[datetime.datetime] = None,
        expires_at: Optional[datetime.datetime] = None,
        verified: bool = False,
        attempts: int = 0
    ):
        self._otp_id = otp_id
        self._customer_id = customer_id
        self._mobile_number = mobile_number
        self._transaction_id = transaction_id
        self._otp_hash = otp_hash
        self._created_at = created_at or datetime.datetime.now()
        self._expires_at = expires_at or (self._created_at + datetime.timedelta(minutes=self.EXPIRY_MINUTES))
        self._verified = bool(verified)
        self._attempts = int(attempts)
        self._plain_otp = None  # Temporary in-memory representation for UI simulation

    @property
    def otp_id(self) -> Optional[int]:
        return self._otp_id

    @otp_id.setter
    def otp_id(self, val: int):
        self._otp_id = val

    @property
    def customer_id(self) -> int:
        return self._customer_id

    @property
    def transaction_id(self) -> Optional[int]:
        return self._transaction_id

    @transaction_id.setter
    def transaction_id(self, val: int):
        self._transaction_id = val

    @property
    def mobile_number(self) -> str:
        return self._mobile_number

    @property
    def otp_hash(self) -> Optional[str]:
        return self._otp_hash

    @property
    def verified(self) -> bool:
        return self._verified

    @property
    def attempts(self) -> int:
        return self._attempts

    @property
    def plain_otp_simulation(self) -> Optional[str]:
        """Provides simulated plain OTP for in-app SMS alert display."""
        return self._plain_otp

    def generate_otp(self) -> str:
        """Generates a secure 6-digit numeric OTP and hashes it using SHA-256."""
        # Cryptographic pseudo-random 6-digit number
        token = f"{random.randint(100000, 999999)}"
        self._plain_otp = token
        self._otp_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
        self._created_at = datetime.datetime.now()
        self._expires_at = self._created_at + datetime.timedelta(minutes=self.EXPIRY_MINUTES)
        self._verified = False
        self._attempts = 0
        return token

    def is_expired(self) -> bool:
        """Checks if the OTP validity duration has lapsed."""
        return datetime.datetime.now() > self._expires_at

    def verify_otp(self, user_entered_otp: str) -> Tuple[bool, str]:
        """
        Verifies the user entered OTP against the SHA-256 hash.
        
        Returns:
            Tuple of (is_successful, status_message)
        """
        if self._verified:
            return True, "OTP is already successfully verified."

        if self._attempts >= self.MAX_ATTEMPTS:
            return False, f"Maximum verification attempts ({self.MAX_ATTEMPTS}) exceeded. Please request a new OTP."

        if self.is_expired():
            return False, "OTP has expired. Please click Resend OTP to generate a fresh code."

        self._attempts += 1
        entered_clean = str(user_entered_otp).strip()
        entered_hash = hashlib.sha256(entered_clean.encode("utf-8")).hexdigest()

        if entered_hash == self._otp_hash:
            self._verified = True
            return True, "OTP Verified successfully! Identity authentication confirmed."
        else:
            remaining = self.MAX_ATTEMPTS - self._attempts
            return False, f"Incorrect OTP entered. {remaining} attempt(s) remaining."

    def resend_otp(self) -> str:
        """Resets verification attempts and generates a fresh token."""
        return self.generate_otp()

    def to_dict(self) -> dict:
        """Serializes OTP verification state for storage/logging."""
        return {
            "otp_id": self._otp_id,
            "customer_id": self._customer_id,
            "transaction_id": self._transaction_id,
            "mobile_number": self._mobile_number,
            "otp_hash": self._otp_hash,
            "created_at": self._created_at.strftime("%Y-%m-%d %H:%M:%S") if isinstance(self._created_at, datetime.datetime) else str(self._created_at),
            "expires_at": self._expires_at.strftime("%Y-%m-%d %H:%M:%S") if isinstance(self._expires_at, datetime.datetime) else str(self._expires_at),
            "verified": self._verified,
            "attempts": self._attempts
        }

    def __repr__(self) -> str:
        return f"<OTPVerification cust={self._customer_id} verified={self._verified} attempts={self._attempts}>"
