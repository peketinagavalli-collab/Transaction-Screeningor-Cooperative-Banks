"""
TransactionScreeningSystem (Master Coordinator & OOPJ Integration).
Combines Statistical Anomaly Detection, DMGT Propositional Logic, NetworkX Graph Analysis, and Multi-Signal Risk Scoring.
"""

import os
import pandas as pd
from typing import Dict, Any, Optional, List, Tuple

from database.db_connection import DatabaseManager
from models.transaction import Transaction
from models.screening_result import ScreeningResult
from services.rule_engine import RuleEngine
from services.anomaly_detector import AnomalyDetector
from services.graph_analyzer import GraphAnalyzer
from services.otp_service import OTPService

class TransactionScreeningSystem:
    """
    Master screening orchestrator coordinating all academic subject modules.
    """

    ACADEMIC_DISCLAIMER = (
        "Disclaimer: This system is an academic prototype for first-level transaction screening in cooperative banks. "
        "It is not a real banking fraud-detection system and does not determine whether a transaction is actually fraudulent. "
        "Any transaction flagged as 'Review Required' or 'Suspicious' requires manual review by authorized cooperative bank personnel."
    )

    def __init__(
        self,
        amount_threshold: float = 50000.0,
        z_threshold: float = 3.0,
        large_withdrawal_threshold: float = 50000.0,
        graph_threshold: float = 0.5,
        weights: Optional[Dict[str, float]] = None,
        decision_bands: Optional[Dict[str, float]] = None
    ):
        self.amount_threshold = float(amount_threshold)
        self.z_threshold = float(z_threshold)
        self.large_withdrawal_threshold = float(large_withdrawal_threshold)
        self.graph_threshold = float(graph_threshold)

        # Default demonstration weights (Sum = 1.0)
        self.weights = weights or {
            "w1_rule": 0.30,
            "w2_statistical": 0.30,
            "w3_graph": 0.20,
            "w4_pattern": 0.20
        }

        # Decision bands (Configurable in Settings)
        self.decision_bands = decision_bands or {
            "normal_max": 39.0,
            "review_max": 69.0
        }

        # Initialize sub-engines
        self.rule_engine = RuleEngine(self.amount_threshold, self.z_threshold, self.graph_threshold)
        self.anomaly_detector = AnomalyDetector(self.z_threshold)
        self.otp_service = OTPService(self.large_withdrawal_threshold, self.z_threshold)
        self.graph_analyzer = self._load_graph_analyzer()

    def _load_graph_analyzer(self) -> GraphAnalyzer:
        """Constructs the NetworkX graph from database transaction history."""
        try:
            df = DatabaseManager.execute_query("""
                SELECT transaction_id, account_id, payee_id, amount, transaction_type, status 
                FROM "TRANSACTION"
            """)
            return GraphAnalyzer(df)
        except Exception:
            return GraphAnalyzer(pd.DataFrame())

    def fetch_account_history(self, account_id: int) -> List[float]:
        """Fetches historical transaction amounts for a specific account."""
        query = """
            SELECT amount FROM "TRANSACTION"
            WHERE account_id = %s
            ORDER BY transaction_date ASC
        """
        df = DatabaseManager.execute_query(query, (account_id,))
        if df.empty:
            return []
        return df["amount"].astype(float).tolist()

    def screen_transaction(
        self,
        account_id: int,
        amount: float,
        payee_id: Optional[int],
        transaction_type: str = "Transfer",
        location: str = "Main Branch",
        save_to_db: bool = True
    ) -> Dict[str, Any]:
        """
        Executes the 11-step academic transaction screening pipeline:
          1. Fetch account history
          2. Calculate mean (μ)
          3. Calculate standard deviation (σ)
          4. Calculate Z-score (z)
          5. Check amount threshold (A)
          6. Check whether payee is new (N)
          7. Apply DMGT propositional logic rules
          8. Analyze NetworkX graph relationships (G)
          9. Calculate multi-signal weighted risk score
          10. Generate final decision band (Normal / Review Required / Suspicious)
          11. Store transaction & screening result in database
        """
        # Step 1: Fetch account history
        history = self.fetch_account_history(account_id)

        # Steps 2, 3, 4: Statistical Anomaly Detection (Mean, Std Dev, Z-Score)
        stat_result = self.anomaly_detector.compute_z_score(amount, history)
        z_score = stat_result["z_score"]
        stat_risk = stat_result["statistical_risk"]

        # Step 5 & 6: Threshold & Graph Novelty Check
        is_new_payee = self.graph_analyzer.is_new_connection(account_id, payee_id)

        # Step 8: NetworkX Graph Analytics
        graph_result = self.graph_analyzer.compute_graph_risk(account_id, payee_id, amount)
        graph_indicator = graph_result["graph_risk_indicator"]
        graph_risk = graph_result["graph_risk_score"]

        # Step 7: DMGT Propositional Logic Evaluation
        logic_result = self.rule_engine.evaluate(amount, is_new_payee, z_score, graph_indicator)
        rule_risk = logic_result["rule_score"]

        # Pattern Risk (Type-specific behaviors e.g. sudden off-hours or unusual transaction types)
        pattern_risk = 15.0
        if transaction_type in ["RTGS", "UPI"] and amount >= self.amount_threshold:
            pattern_risk = 60.0
        elif transaction_type == "Withdrawal" and amount >= self.large_withdrawal_threshold:
            pattern_risk = 75.0

        # Step 9: Multi-Signal Risk Scoring
        w1 = self.weights.get("w1_rule", 0.30)
        w2 = self.weights.get("w2_statistical", 0.30)
        w3 = self.weights.get("w3_graph", 0.20)
        w4 = self.weights.get("w4_pattern", 0.20)

        raw_risk = (
            w1 * rule_risk +
            w2 * stat_risk +
            w3 * graph_risk +
            w4 * pattern_risk
        )
        final_risk_score = min(max(raw_risk, 0.0), 100.0)

        # Step 10: Generate Decision based on bands & Rule Engine override
        if logic_result["rule_decision"] == "Suspicious":
            decision = "Suspicious"
        elif logic_result["rule_decision"] == "Review Required" and final_risk_score < self.decision_bands["review_max"]:
            decision = "Review Required"
        else:
            if final_risk_score <= self.decision_bands["normal_max"]:
                decision = "Normal"
            elif final_risk_score <= self.decision_bands["review_max"]:
                decision = "Review Required"
            else:
                decision = "Suspicious"

        # Combine comprehensive explainability reasons
        all_reasons = []
        all_reasons.extend(logic_result["reasons"])
        if graph_result["factors"]:
            all_reasons.extend(graph_result["factors"])

        clean_reasons_str = "; ".join(dict.fromkeys(all_reasons))

        # Build OOP Result Object
        txn_obj = Transaction(
            transaction_id=None,
            account_id=account_id,
            amount=amount,
            transaction_type=transaction_type,
            payee_id=payee_id,
            location=location,
            status="Under Review" if decision != "Normal" else "Completed"
        )

        screening_obj = ScreeningResult(
            result_id=None,
            transaction_id=0,
            z_score=z_score,
            rule_score=rule_risk,
            graph_score=graph_risk,
            risk_score=final_risk_score,
            decision=decision,
            reasons=clean_reasons_str
        )

        # Step 11: Persist in Database if requested
        txn_id = None
        result_id = None
        if save_to_db:
            txn_id = DatabaseManager.execute_query(
                "INSERT INTO \"TRANSACTION\" (account_id, payee_id, amount, transaction_type, location, status) "
                "VALUES (%s, %s, %s, %s, %s, %s)",
                (account_id, payee_id, amount, transaction_type, location, txn_obj.status),
                commit=True
            )
            txn_obj.transaction_id = txn_id
            screening_obj._transaction_id = txn_id

            result_id = DatabaseManager.execute_query(
                "INSERT INTO SCREENING_RESULT (transaction_id, z_score, rule_score, graph_score, risk_score, decision, reasons) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (txn_id, z_score, rule_risk, graph_risk, final_risk_score, decision, clean_reasons_str),
                commit=True
            )
            screening_obj.result_id = result_id

            # Refresh graph analyzer with the new edge
            self.graph_analyzer = self._load_graph_analyzer()

        return {
            "transaction_id": txn_id,
            "result_id": result_id,
            "decision": decision,
            "risk_score": final_risk_score,
            "z_score": z_score,
            "rule_score": rule_risk,
            "graph_score": graph_risk,
            "pattern_risk": pattern_risk,
            "is_new_payee": is_new_payee,
            "reasons": clean_reasons_str,
            "reasons_list": screening_obj.reasons_list(),
            "propositions": logic_result["propositions"],
            "triggered_rules": logic_result["triggered_rules"],
            "statistical_details": stat_result,
            "graph_details": graph_result,
            "weights_used": {"w1": w1, "w2": w2, "w3": w3, "w4": w4},
            "disclaimer": self.ACADEMIC_DISCLAIMER
        }
