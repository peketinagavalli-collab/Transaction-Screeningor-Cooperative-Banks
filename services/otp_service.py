"""
OTP Service for Section 19: Large Cash Withdrawal & Authentication Flow.
Compares withdrawals against customer-specific historical patterns and manages secure simulated OTP tokens.
"""

import math
import datetime
from typing import Dict, Any, Tuple, Optional, List
from database.db_connection import DatabaseManager
from models.otp_verification import OTPVerification

class OTPService:
    """Orchestrates large cash withdrawal pattern analysis and OTP lifecycle management."""

    def __init__(self, large_withdrawal_threshold: float = 50000.0, customer_z_threshold: float = 3.0):
        self.large_withdrawal_threshold = float(large_withdrawal_threshold)
        self.customer_z_threshold = float(customer_z_threshold)

    def get_customer_withdrawal_history(self, customer_id: int) -> List[float]:
        """Fetches all past cash withdrawals made by the specified customer across their accounts."""
        query = """
            SELECT t.amount
            FROM "TRANSACTION" t
            JOIN ACCOUNT a ON t.account_id = a.account_id
            WHERE a.customer_id = %s AND t.transaction_type = 'Withdrawal'
            ORDER BY t.transaction_date ASC
        """
        df = DatabaseManager.execute_query(query, (customer_id,))
        if df.empty:
            return []
        return df["amount"].astype(float).tolist()

    def analyze_withdrawal_request(
        self,
        customer_id: int,
        withdrawal_amount: float
    ) -> Dict[str, Any]:
        """
        Evaluates a cash withdrawal request against the customer's personal baseline.
        
        Returns:
            Dictionary with historical mean, standard deviation, customer Z-score, OTP requirement, and flags.
        """
        history = self.get_customer_withdrawal_history(customer_id)
        x = float(withdrawal_amount)
        n = len(history)

        # Baseline calculations
        if n >= 2:
            mu = sum(history) / n
            sq_diff = sum((val - mu) ** 2 for val in history)
            sigma = math.sqrt(sq_diff / n)
            if sigma < 1.0:
                sigma = max(mu * 0.15, 1000.0)
        elif n == 1:
            mu = history[0]
            sigma = max(mu * 0.2, 1000.0)
        else:
            # Fallback for new customer without historical withdrawals
            mu = 7500.0
            sigma = 2500.0

        deviation = x - mu
        z_score = deviation / sigma
        abs_z = abs(z_score)

        is_large = bool(x >= self.large_withdrawal_threshold)
        is_unusual_pattern = bool(abs_z >= self.customer_z_threshold)
        is_otp_required = is_large

        # Categorize the 4 distinct academic withdrawal states
        if not is_large and not is_unusual_pattern:
            classification = "Normal Withdrawal"
            recommended_decision = "Normal"
        elif is_large and not is_unusual_pattern:
            classification = "Large Withdrawal (Standard Pattern)"
            recommended_decision = "Normal"
        elif not is_large and is_unusual_pattern:
            classification = "Unusual Withdrawal Pattern (Below Large Threshold)"
            recommended_decision = "Review Required"
        else:
            classification = "Large + Unusual Withdrawal (High Deviation)"
            recommended_decision = "Review Required"

        return {
            "customer_id": customer_id,
            "current_amount": x,
            "historical_count": n,
            "historical_mean": mu,
            "historical_std_dev": sigma,
            "historical_history": history,
            "customer_z_score": z_score,
            "abs_z_score": abs_z,
            "large_withdrawal_threshold": self.large_withdrawal_threshold,
            "customer_z_threshold": self.customer_z_threshold,
            "is_large_withdrawal": is_large,
            "is_unusual_pattern": is_unusual_pattern,
            "is_otp_required": is_otp_required,
            "classification": classification,
            "recommended_decision": recommended_decision,
            "step_by_step": {
                "formula_mean": r"\mu_{\text{cust}} = \frac{\sum x}{n}",
                "calc_mean": f"\\mu_{{\\text{{cust}}}} = ₹{mu:,.2f} \\text{{ (n={n})}}",
                "formula_std": r"\sigma_{\text{cust}} = \sqrt{\frac{\sum (x - \mu)^2}{n}}",
                "calc_std": f"\\sigma_{{\\text{{cust}}}} = ₹{sigma:,.2f}",
                "formula_z": r"z = \frac{x - \mu_{\text{cust}}}{\sigma_{\text{cust}}}",
                "calc_z": f"z = \\frac{{{x:,.2f} - {mu:,.2f}}}{{{sigma:,.2f}}} = {z_score:.2f}"
            }
        }

    def generate_and_save_otp(
        self,
        customer_id: int,
        mobile_number: str,
        transaction_id: Optional[int] = None
    ) -> Tuple[OTPVerification, str]:
        """
        Creates a new OTPVerification instance, persists its SHA-256 hash in the database,
        and returns the plain OTP string for simulated SMS display.
        """
        otp_obj = OTPVerification(
            otp_id=None,
            customer_id=customer_id,
            mobile_number=mobile_number,
            transaction_id=transaction_id
        )
        plain_token = otp_obj.generate_otp()

        # Insert record into database
        query = """
            INSERT INTO OTP_VERIFICATION 
            (customer_id, transaction_id, mobile_number, otp_hash, created_at, expires_at, verified, attempts)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        otp_id = DatabaseManager.execute_query(
            query,
            (
                customer_id,
                transaction_id,
                mobile_number,
                otp_obj.otp_hash,
                otp_obj._created_at.strftime("%Y-%m-%d %H:%M:%S"),
                otp_obj._expires_at.strftime("%Y-%m-%d %H:%M:%S"),
                0,
                0
            ),
            commit=True
        )
        otp_obj.otp_id = otp_id
        return otp_obj, plain_token

    def verify_otp_token(
        self,
        otp_obj: OTPVerification,
        entered_code: str
    ) -> Tuple[bool, str]:
        """Verifies the token and updates the database record."""
        success, msg = otp_obj.verify_otp(entered_code)

        if otp_obj.otp_id:
            update_query = """
                UPDATE OTP_VERIFICATION
                SET verified = %s, attempts = %s
                WHERE otp_id = %s
            """
            DatabaseManager.execute_query(
                update_query,
                (1 if otp_obj.verified else 0, otp_obj.attempts, otp_obj.otp_id),
                commit=True
            )

        return success, msg
