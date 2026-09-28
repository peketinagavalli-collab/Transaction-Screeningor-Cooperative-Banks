"""
LoanApplication Model (OOPJ Subject Module).
Encapsulates online loan application attributes, validation rules, and state management.
"""

from typing import Optional, Dict, Any, List
import datetime

class LoanApplication:
    """Represents an online bank loan application submitted by a cooperative bank customer."""

    ALLOWED_STATUSES = [
        "Submitted",
        "Document Verification",
        "Manual Review",
        "Approved",
        "Rejected",
        "More Information Required"
    ]

    ALLOWED_LOAN_TYPES = [
        "Agricultural Credit Loan",
        "Crop & Seasonal Agricultural Loan",
        "Dairy & Farm Equipment Loan",
        "Small Business / MSME Loan",
        "Personal Loan",
        "Home / Rural Housing Loan",
        "Vehicle Loan",
        "Education Loan",
        "Gold / Micro-Enterprise Loan"
    ]

    def __init__(
        self,
        loan_id: Optional[int],
        applicant_name: str,
        mobile: str,
        email: str,
        address: str,
        dob: str,
        occupation: str,
        income: float,
        loan_type: str,
        requested_amount: float,
        loan_purpose: str,
        repayment_period: str,
        application_date: Optional[str] = None,
        status: str = "Submitted",
        overall_score: float = 0.0
    ):
        self.loan_id = loan_id
        self.applicant_name = applicant_name
        self.mobile = mobile
        self.email = email
        self.address = address
        self.dob = dob
        self.occupation = occupation
        self.income = float(income)
        self.loan_type = loan_type
        self.requested_amount = float(requested_amount)
        self.loan_purpose = loan_purpose
        self.repayment_period = repayment_period
        self.application_date = application_date or datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.status = status
        self.overall_score = float(overall_score)

    @property
    def formatted_id(self) -> str:
        """Returns human-readable application reference code (e.g. LOAN-2026-0042)."""
        if self.loan_id:
            return f"LOAN-{datetime.datetime.now().year}-{self.loan_id:04d}"
        return "LOAN-NEW-PENDING"

    @property
    def status_badge_info(self) -> Dict[str, str]:
        """Returns color and icon information for UI status rendering."""
        status_styles = {
            "Submitted": {"bg": "#E0F2FE", "color": "#0369A1", "icon": "📥", "border": "#7DD3FC"},
            "Document Verification": {"bg": "#FEF3C7", "color": "#B45309", "icon": "🔍", "border": "#FCD34D"},
            "Manual Review": {"bg": "#EDE9FE", "color": "#6D28D9", "icon": "👨‍💼", "border": "#C4B5FD"},
            "Approved": {"bg": "#DCFCE7", "color": "#15803D", "icon": "✅", "border": "#86EFAC"},
            "Rejected": {"bg": "#FEE2E2", "color": "#B91C1C", "icon": "❌", "border": "#FCA5A5"},
            "More Information Required": {"bg": "#FFEDD5", "color": "#C2410C", "icon": "⚠️", "border": "#FDBA74"},
        }
        return status_styles.get(self.status, {"bg": "#F1F5F9", "color": "#475569", "icon": "📄", "border": "#CBD5E1"})

    def to_dict(self) -> Dict[str, Any]:
        """Serializes loan application model into a clean dictionary."""
        return {
            "loan_id": self.loan_id,
            "formatted_id": self.formatted_id,
            "applicant_name": self.applicant_name,
            "mobile": self.mobile,
            "email": self.email,
            "address": self.address,
            "dob": self.dob,
            "occupation": self.occupation,
            "income": self.income,
            "loan_type": self.loan_type,
            "requested_amount": self.requested_amount,
            "loan_purpose": self.loan_purpose,
            "repayment_period": self.repayment_period,
            "application_date": self.application_date,
            "status": self.status,
            "overall_score": self.overall_score
        }

    def __repr__(self) -> str:
        return f"<LoanApplication {self.formatted_id} applicant='{self.applicant_name}' amount=₹{self.requested_amount:,.2f} status='{self.status}'>"
