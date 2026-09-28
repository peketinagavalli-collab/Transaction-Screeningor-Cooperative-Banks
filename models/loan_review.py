"""
LoanReview Model (OOPJ Subject Module).
Encapsulates bank officer manual inspection actions, comments, and decision outcomes.
"""

from typing import Optional, Dict, Any
import datetime

class LoanReview:
    """Represents an official bank officer audit and review entry for a loan application."""

    ALLOWED_OFFICER_STATUSES = [
        "Approved",
        "Rejected",
        "More Information Required",
        "Manual Review",
        "Document Verification"
    ]

    def __init__(
        self,
        review_id: Optional[int],
        loan_id: int,
        officer_status: str,
        officer_comments: str,
        officer_name: str = "Authorized Bank Officer",
        reviewed_at: Optional[str] = None
    ):
        self.review_id = review_id
        self.loan_id = loan_id
        self.officer_name = officer_name
        self.officer_status = officer_status
        self.officer_comments = officer_comments
        self.reviewed_at = reviewed_at or datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def to_dict(self) -> Dict[str, Any]:
        """Serializes loan review model to dictionary."""
        return {
            "review_id": self.review_id,
            "loan_id": self.loan_id,
            "officer_name": self.officer_name,
            "officer_status": self.officer_status,
            "officer_comments": self.officer_comments,
            "reviewed_at": self.reviewed_at
        }

    def __repr__(self) -> str:
        return f"<LoanReview id={self.review_id} loan_id={self.loan_id} officer='{self.officer_name}' status='{self.officer_status}'>"
