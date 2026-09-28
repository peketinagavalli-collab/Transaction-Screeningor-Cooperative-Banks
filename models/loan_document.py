"""
LoanDocument Model (OOPJ Subject Module).
Encapsulates uploaded loan document attributes, automated screening scores, and verification status.
"""

from typing import Optional, Dict, Any
import json
import datetime

class LoanDocument:
    """Represents an uploaded certificate or identity document associated with a loan application."""

    ALLOWED_STATUSES = ["PASS", "REVIEW REQUIRED", "UNABLE TO VERIFY"]

    ALLOWED_DOC_TYPES = [
        "Aadhaar/Identity Proof",
        "Address Proof",
        "Income Certificate",
        "Salary Slip",
        "Bank Statement",
        "Educational Certificate",
        "Other Supporting Documents"
    ]

    STATUS_DESCRIPTIONS = {
        "PASS": "Document passed automated screening",
        "REVIEW REQUIRED": "Document requires manual verification",
        "UNABLE TO VERIFY": "Unable to verify automatically"
    }

    def __init__(
        self,
        document_id: Optional[int],
        loan_id: int,
        document_type: str,
        file_name: str,
        file_path: str,
        file_size: int,
        mime_type: str,
        sha256_hash: str,
        extracted_text: str = "",
        extracted_doc_number: str = "",
        issuing_authority: str = "",
        detected_date: str = "",
        name_match_status: str = "Pending",
        file_validity_score: float = 0.0,
        text_consistency_score: float = 0.0,
        identity_consistency_score: float = 0.0,
        qr_verification_score: float = 0.0,
        signature_check_score: float = 0.0,
        integrity_check_score: float = 0.0,
        verification_score: float = 0.0,
        verification_status: str = "UNABLE TO VERIFY",
        verification_details: Optional[Any] = None,
        uploaded_at: Optional[str] = None
    ):
        self.document_id = document_id
        self.loan_id = loan_id
        self.document_type = document_type
        self.file_name = file_name
        self.file_path = file_path
        self.file_size = int(file_size)
        self.mime_type = mime_type
        self.sha256_hash = sha256_hash
        self.extracted_text = extracted_text or ""
        self.extracted_doc_number = extracted_doc_number or ""
        self.issuing_authority = issuing_authority or ""
        self.detected_date = detected_date or ""
        self.name_match_status = name_match_status
        self.file_validity_score = float(file_validity_score)
        self.text_consistency_score = float(text_consistency_score)
        self.identity_consistency_score = float(identity_consistency_score)
        self.qr_verification_score = float(qr_verification_score)
        self.signature_check_score = float(signature_check_score)
        self.integrity_check_score = float(integrity_check_score)
        self.verification_score = float(verification_score)
        self.verification_status = verification_status
        
        if isinstance(verification_details, dict):
            self.verification_details = verification_details
        elif isinstance(verification_details, str) and verification_details.strip():
            try:
                self.verification_details = json.loads(verification_details)
            except Exception:
                self.verification_details = {"raw_note": verification_details}
        else:
            self.verification_details = {}

        self.uploaded_at = uploaded_at or datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @property
    def status_label(self) -> str:
        """Returns customer-facing screening label without asserting legal authenticity."""
        return self.STATUS_DESCRIPTIONS.get(self.verification_status, "Automated screening evaluation")

    @property
    def badge_style(self) -> Dict[str, str]:
        """Returns visual badge colors and symbols for UI rendering."""
        styles = {
            "PASS": {
                "bg": "#D1FAE5",
                "color": "#065F46",
                "border": "#34D399",
                "icon": "✅",
                "label": "PASS — Automated screening passed"
            },
            "REVIEW REQUIRED": {
                "bg": "#FEF3C7",
                "color": "#92400E",
                "border": "#FBBF24",
                "icon": "⚠️",
                "label": "REVIEW REQUIRED — Document requires manual verification"
            },
            "UNABLE TO VERIFY": {
                "bg": "#FEE2E2",
                "color": "#991B1B",
                "border": "#F87171",
                "icon": "❓",
                "label": "UNABLE TO VERIFY — Unable to verify automatically"
            }
        }
        return styles.get(self.verification_status, {
            "bg": "#F1F5F9",
            "color": "#475569",
            "border": "#CBD5E1",
            "icon": "📄",
            "label": self.verification_status
        })

    def to_dict(self) -> Dict[str, Any]:
        """Serializes loan document instance to dictionary."""
        return {
            "document_id": self.document_id,
            "loan_id": self.loan_id,
            "document_type": self.document_type,
            "file_name": self.file_name,
            "file_path": self.file_path,
            "file_size": self.file_size,
            "mime_type": self.mime_type,
            "sha256_hash": self.sha256_hash,
            "extracted_text": self.extracted_text,
            "extracted_doc_number": self.extracted_doc_number,
            "issuing_authority": self.issuing_authority,
            "detected_date": self.detected_date,
            "name_match_status": self.name_match_status,
            "file_validity_score": self.file_validity_score,
            "text_consistency_score": self.text_consistency_score,
            "identity_consistency_score": self.identity_consistency_score,
            "qr_verification_score": self.qr_verification_score,
            "signature_check_score": self.signature_check_score,
            "integrity_check_score": self.integrity_check_score,
            "verification_score": self.verification_score,
            "verification_status": self.verification_status,
            "status_label": self.status_label,
            "verification_details": self.verification_details,
            "uploaded_at": self.uploaded_at
        }

    def __repr__(self) -> str:
        return f"<LoanDocument id={self.document_id} type='{self.document_type}' score={self.verification_score:.1f}% status='{self.verification_status}'>"
