"""
LoanService (Service Layer Module).
Manages database transactions for online loan applications, document attachments, and officer reviews.
"""

import os
import json
import datetime
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple

from database.db_connection import DatabaseManager
from models.loan_application import LoanApplication
from models.loan_document import LoanDocument
from models.loan_review import LoanReview
from services.document_verification_service import DocumentVerificationService

class LoanService:
    """Service handling CRUD operations and business logic for online loan applications."""

    def __init__(self):
        self.doc_verifier = DocumentVerificationService()

    def submit_loan_application(
        self,
        applicant_data: Dict[str, Any],
        verified_documents: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Persists a newly submitted loan application and all its screened documents atomically.

        Args:
            applicant_data: Form dictionary containing applicant and loan request details.
            verified_documents: List of document screening result dictionaries from DocumentVerificationService.

        Returns:
            Dictionary with generated loan_id, formatted_id, overall score, and status.
        """
        # Calculate composite loan application verification score
        if verified_documents:
            doc_scores = [d.get("verification_score", 0.0) for d in verified_documents]
            overall_score = sum(doc_scores) / len(doc_scores)
        else:
            overall_score = 0.0

        # Determine initial application status based on automated document screening
        passed_count = sum(1 for d in verified_documents if d.get("verification_status") == "PASS")
        review_count = sum(1 for d in verified_documents if d.get("verification_status") == "REVIEW REQUIRED")
        unable_count = sum(1 for d in verified_documents if d.get("verification_status") == "UNABLE TO VERIFY")

        if unable_count > 0:
            initial_status = "More Information Required"
        elif review_count > 0:
            initial_status = "Manual Review"
        elif passed_count > 0 and passed_count == len(verified_documents):
            initial_status = "Document Verification"  # Ready for officer final decision
        else:
            initial_status = "Submitted"

        app_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 1. Insert LOAN_APPLICATION record
        insert_loan_sql = """
            INSERT INTO LOAN_APPLICATION (
                applicant_name, mobile, email, address, dob, occupation,
                income, loan_type, requested_amount, loan_purpose,
                repayment_period, application_date, status, overall_score
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        loan_params = (
            applicant_data["applicant_name"],
            applicant_data["mobile"],
            applicant_data["email"],
            applicant_data["address"],
            applicant_data["dob"],
            applicant_data["occupation"],
            float(applicant_data["income"]),
            applicant_data["loan_type"],
            float(applicant_data["requested_amount"]),
            applicant_data["loan_purpose"],
            applicant_data["repayment_period"],
            app_date,
            initial_status,
            round(overall_score, 2)
        )
        loan_id = DatabaseManager.execute_query(insert_loan_sql, loan_params, commit=True)

        # 2. Insert LOAN_DOCUMENT records
        saved_doc_records = []
        for doc in verified_documents:
            details_json = json.dumps(doc.get("verification_details", {}))
            insert_doc_sql = """
                INSERT INTO LOAN_DOCUMENT (
                    loan_id, document_type, file_name, file_path, file_size, mime_type,
                    sha256_hash, extracted_text, extracted_doc_number, issuing_authority,
                    detected_date, name_match_status, file_validity_score, text_consistency_score,
                    identity_consistency_score, qr_verification_score, signature_check_score,
                    integrity_check_score, verification_score, verification_status,
                    verification_details, uploaded_at
                ) VALUES (
                    %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s,
                    %s, %s, %s, %s,
                    %s, %s, %s,
                    %s, %s, %s,
                    %s, %s
                )
            """
            doc_params = (
                loan_id,
                doc.get("document_type", "Other Supporting Documents"),
                doc.get("file_name", "unnamed_document"),
                doc.get("file_path", ""),
                int(doc.get("file_size", 0)),
                doc.get("mime_type", "application/octet-stream"),
                doc.get("sha256_hash", ""),
                doc.get("extracted_text", ""),
                doc.get("extracted_doc_number", ""),
                doc.get("issuing_authority", ""),
                doc.get("detected_date", ""),
                doc.get("name_match_status", "Pending"),
                float(doc.get("file_validity_score", 0.0)),
                float(doc.get("text_consistency_score", 0.0)),
                float(doc.get("identity_consistency_score", 0.0)),
                float(doc.get("qr_verification_score", 0.0)),
                float(doc.get("signature_check_score", 0.0)),
                float(doc.get("integrity_check_score", 0.0)),
                float(doc.get("verification_score", 0.0)),
                doc.get("verification_status", "UNABLE TO VERIFY"),
                details_json,
                app_date
            )
            doc_id = DatabaseManager.execute_query(insert_doc_sql, doc_params, commit=True)
            saved_doc_records.append(doc_id)

        # 3. Create initial automated system review entry in LOAN_REVIEW
        initial_comments = (
            f"Automated document screening completed. "
            f"Documents submitted: {len(verified_documents)}, Passed: {passed_count}, "
            f"Manual review required: {review_count}, Unable to verify: {unable_count}. "
            f"Preliminary Composite Score: {overall_score:.1f}%."
        )
        insert_review_sql = """
            INSERT INTO LOAN_REVIEW (loan_id, officer_name, officer_status, officer_comments, reviewed_at)
            VALUES (%s, %s, %s, %s, %s)
        """
        DatabaseManager.execute_query(
            insert_review_sql,
            (loan_id, "System Auto-Screening Bot", initial_status, initial_comments, app_date),
            commit=True
        )

        formatted_id = f"LOAN-{datetime.datetime.now().year}-{loan_id:04d}"

        return {
            "loan_id": loan_id,
            "formatted_id": formatted_id,
            "applicant_name": applicant_data["applicant_name"],
            "loan_type": applicant_data["loan_type"],
            "requested_amount": applicant_data["requested_amount"],
            "documents_submitted": len(verified_documents),
            "documents_passed": passed_count,
            "documents_requiring_review": review_count,
            "documents_unable_verify": unable_count,
            "verification_score": round(overall_score, 1),
            "status": initial_status,
            "application_date": app_date
        }

    def get_all_loan_applications(
        self,
        status_filter: Optional[str] = None,
        search_term: Optional[str] = None
    ) -> pd.DataFrame:
        """Fetches all loan applications with optional status and search filtering."""
        query = """
            SELECT 
                la.loan_id,
                la.applicant_name,
                la.mobile,
                la.email,
                la.loan_type,
                la.requested_amount,
                la.income,
                la.loan_purpose,
                la.repayment_period,
                la.application_date,
                la.status,
                la.overall_score,
                COUNT(ld.document_id) AS total_docs,
                SUM(CASE WHEN ld.verification_status = 'PASS' THEN 1 ELSE 0 END) AS passed_docs,
                SUM(CASE WHEN ld.verification_status = 'REVIEW REQUIRED' THEN 1 ELSE 0 END) AS review_docs,
                SUM(CASE WHEN ld.verification_status = 'UNABLE TO VERIFY' THEN 1 ELSE 0 END) AS unable_docs
            FROM LOAN_APPLICATION la
            LEFT JOIN LOAN_DOCUMENT ld ON la.loan_id = ld.loan_id
            WHERE 1=1
        """
        params = []
        if status_filter and status_filter != "All Statuses":
            query += " AND la.status = %s"
            params.append(status_filter)

        if search_term and search_term.strip():
            query += " AND (la.applicant_name LIKE %s OR la.mobile LIKE %s OR la.email LIKE %s OR CAST(la.loan_id AS TEXT) LIKE %s)"
            st_param = f"%{search_term.strip()}%"
            params.extend([st_param, st_param, st_param, st_param])

        query += " GROUP BY la.loan_id ORDER BY la.loan_id DESC"
        
        try:
            df = DatabaseManager.execute_query(query, tuple(params) if params else None)
            return df
        except Exception:
            return pd.DataFrame()

    def get_loan_details(self, loan_id: int) -> Dict[str, Any]:
        """Fetches complete application dossier including documents and review audit history."""
        # 1. Fetch application info
        app_df = DatabaseManager.execute_query(
            "SELECT * FROM LOAN_APPLICATION WHERE loan_id = %s",
            (loan_id,)
        )
        if app_df.empty:
            return {}

        app_dict = app_df.iloc[0].to_dict()
        app_dict["formatted_id"] = f"LOAN-{datetime.datetime.now().year}-{loan_id:04d}"

        # 2. Fetch associated documents
        docs_df = DatabaseManager.execute_query(
            "SELECT * FROM LOAN_DOCUMENT WHERE loan_id = %s ORDER BY document_id ASC",
            (loan_id,)
        )
        docs_list = []
        if not docs_df.empty:
            for _, row in docs_df.iterrows():
                d = row.to_dict()
                try:
                    if isinstance(d.get("verification_details"), str) and d["verification_details"]:
                        d["verification_details"] = json.loads(d["verification_details"])
                except Exception:
                    pass
                docs_list.append(d)

        # 3. Fetch review audit history
        reviews_df = DatabaseManager.execute_query(
            "SELECT * FROM LOAN_REVIEW WHERE loan_id = %s ORDER BY review_id DESC",
            (loan_id,)
        )
        reviews_list = reviews_df.to_dict(orient="records") if not reviews_df.empty else []

        return {
            "application": app_dict,
            "documents": docs_list,
            "reviews": reviews_list
        }

    def add_officer_review(
        self,
        loan_id: int,
        officer_status: str,
        officer_comments: str,
        officer_name: str = "Authorized Bank Officer"
    ) -> bool:
        """Records an official bank officer decision and updates the master application status."""
        rev_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 1. Update LOAN_APPLICATION status
        update_sql = "UPDATE LOAN_APPLICATION SET status = %s WHERE loan_id = %s"
        DatabaseManager.execute_query(update_sql, (officer_status, loan_id), commit=True)

        # 2. Insert LOAN_REVIEW audit record
        insert_sql = """
            INSERT INTO LOAN_REVIEW (loan_id, officer_name, officer_status, officer_comments, reviewed_at)
            VALUES (%s, %s, %s, %s, %s)
        """
        DatabaseManager.execute_query(
            insert_sql,
            (loan_id, officer_name, officer_status, officer_comments, rev_date),
            commit=True
        )
        return True
