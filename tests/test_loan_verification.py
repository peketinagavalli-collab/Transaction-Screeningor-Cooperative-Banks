"""
Unit and Integration Tests for Online Loan Application & Certificate Verification.
Validates Document Verification Academic Formula, QR Code Extraction, Identity Consistency, and Officer Review.
"""

import os
import io
import unittest
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from database.db_connection import DatabaseManager
from database.init_db import init_database
from models.loan_application import LoanApplication
from models.loan_document import LoanDocument
from models.loan_review import LoanReview
from services.document_verification_service import DocumentVerificationService
from services.loan_service import LoanService

try:
    import qrcode
    QRCODE_AVAILABLE = True
except ImportError:
    QRCODE_AVAILABLE = False


class TestLoanVerification(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        init_database(force_recreate=True)
        cls.verifier = DocumentVerificationService()
        cls.loan_service = LoanService()

    def test_01_document_scoring_formula(self):
        """Validates that DocumentScore = 0.20*V + 0.20*T + 0.20*I + 0.15*Q + 0.10*S + 0.15*M."""
        weights = DocumentVerificationService.WEIGHTS
        self.assertAlmostEqual(weights["w_file_validity"], 0.20)
        self.assertAlmostEqual(weights["w_text_consistency"], 0.20)
        self.assertAlmostEqual(weights["w_identity_consistency"], 0.20)
        self.assertAlmostEqual(weights["w_qr_verification"], 0.15)
        self.assertAlmostEqual(weights["w_signature_check"], 0.10)
        self.assertAlmostEqual(weights["w_integrity_check"], 0.15)
        self.assertAlmostEqual(sum(weights.values()), 1.00)

    def test_02_loan_application_crud(self):
        """Validates creating and retrieving a loan application with documents and officer review."""
        applicant_data = {
            "applicant_name": "Test Farmer Rajesh",
            "mobile": "9811223344",
            "email": "rajesh.test@coopbank.in",
            "address": "Village Shrirampur, District Pune, Maharashtra - 411001",
            "dob": "1985-06-15",
            "occupation": "Farmer",
            "income": 50000.0,
            "loan_type": "Agricultural Credit Loan",
            "requested_amount": 300000.0,
            "loan_purpose": "Purchase of solar pump equipment",
            "repayment_period": "36 Months"
        }

        # Mock verified document
        mock_docs = [
            {
                "document_type": "Aadhaar/Identity Proof",
                "file_name": "rajesh_aadhaar.pdf",
                "file_path": "data/uploads/loan_documents/test_aadhaar.pdf",
                "file_size": 120000,
                "mime_type": "application/pdf",
                "sha256_hash": "ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff",
                "extracted_text": "Government of India UIDAI Name: Test Farmer Rajesh DOB: 15/06/1985 9182-3819-2819",
                "extracted_doc_number": "9182-3819-2819",
                "issuing_authority": "Unique Identification Authority of India",
                "detected_date": "15/06/1985",
                "name_match_status": "Matched (Exact/Complete)",
                "file_validity_score": 1.0,
                "text_consistency_score": 0.95,
                "identity_consistency_score": 1.0,
                "qr_verification_score": 0.90,
                "signature_check_score": 0.85,
                "integrity_check_score": 1.0,
                "verification_score": 95.0,
                "verification_status": "PASS",
                "verification_details": {"note": "Test passed"}
            }
        ]

        result = self.loan_service.submit_loan_application(applicant_data, mock_docs)
        self.assertIsNotNone(result["loan_id"])
        self.assertEqual(result["applicant_name"], "Test Farmer Rajesh")
        self.assertEqual(result["documents_passed"], 1)
        self.assertEqual(result["verification_score"], 95.0)

        # Verify fetching loan details
        dossier = self.loan_service.get_loan_details(result["loan_id"])
        self.assertIn("application", dossier)
        self.assertEqual(dossier["application"]["applicant_name"], "Test Farmer Rajesh")
        self.assertEqual(len(dossier["documents"]), 1)

        # Officer Review action
        success = self.loan_service.add_officer_review(
            loan_id=result["loan_id"],
            officer_status="Approved",
            officer_comments="Identity verified against land registry deeds. Approved.",
            officer_name="Credit Officer S. Patil"
        )
        self.assertTrue(success)

        # Re-fetch dossier to verify status update
        updated_dossier = self.loan_service.get_loan_details(result["loan_id"])
        self.assertEqual(updated_dossier["application"]["status"], "Approved")
        self.assertGreaterEqual(len(updated_dossier["reviews"]), 2)

    def test_03_qr_code_verification_image(self):
        """Generates an in-memory image with a QR code and tests OpenCV QR decoding."""
        if not QRCODE_AVAILABLE:
            self.skipTest("qrcode library not installed")

        # Create a test QR code with applicant name payload
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data("Aadhaar:9988-7766-5544;Name:Govind Narain;DOB:1980-01-01")
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")

        # Save to buffer
        buf = io.BytesIO()
        qr_img.save(buf, format="PNG")
        png_bytes = buf.getvalue()

        # Run verification
        applicant_info = {
            "applicant_name": "Govind Narain",
            "dob": "1980-01-01",
            "address": "Main Street",
            "income": 60000.0
        }

        ver_res = self.verifier.verify_document(
            file_bytes=png_bytes,
            original_filename="govind_aadhaar_qr.png",
            document_type="Aadhaar/Identity Proof",
            applicant_info=applicant_info
        )

        self.assertEqual(ver_res["file_validity_score"], 1.0)
        self.assertTrue(ver_res["verification_details"]["qr_details"]["qr_detected"])
        self.assertGreaterEqual(ver_res["qr_verification_score"], 0.90)

    def test_04_identity_consistency_name_mismatch(self):
        """Validates that a severe name mismatch is flagged with low identity score and manual review."""
        # Create text with a completely different name
        mock_text = "Unique Identification Authority of India Name: Vikramaditya Chauhan DOB: 1975-04-12 8888-9999-0000"
        
        applicant_info = {
            "applicant_name": "Suresh Patel",
            "dob": "1978-11-22",
            "address": "Anand, Gujarat",
            "income": 75000.0
        }

        id_score, id_details = self.verifier._check_identity_consistency(
            extracted_text=mock_text,
            extracted_name="Vikramaditya Chauhan",
            applicant_info=applicant_info,
            entities={"applicant_name": "Vikramaditya Chauhan", "document_number": "8888-9999-0000"}
        )

        self.assertLessEqual(id_score, 0.35)
        self.assertIn("Mismatch", id_details["name_match_status"])


if __name__ == "__main__":
    unittest.main()
