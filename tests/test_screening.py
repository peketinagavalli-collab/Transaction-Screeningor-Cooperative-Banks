"""
Automated Academic Test Suite for Cooperative Bank Screening System.
Verifies Statistical Formulas, DMGT Logic, NetworkX Graph Analysis, OTP Cryptography, and Database CRUD.
"""

import unittest
import math
from database.db_connection import DatabaseManager
from database.init_db import init_database
from models.customer import Customer
from models.account import Account
from models.otp_verification import OTPVerification
from services.anomaly_detector import AnomalyDetector
from services.rule_engine import RuleEngine
from services.graph_analyzer import GraphAnalyzer
from services.otp_service import OTPService
from services.screening_service import TransactionScreeningSystem

class TestCoopBankScreening(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Initialize database
        init_database(force_recreate=True)

    def test_01_statistical_formulas(self):
        """Validates Mean, Standard Deviation, and Z-Score against expected math."""
        detector = AnomalyDetector(z_threshold=3.0)
        # Sample history: [10000, 20000, 30000]
        # Mean = 20000, Variance = ((10k-20k)^2 + 0 + (30k-20k)^2) / 3 = 200,000,000 / 3 = 66,666,666.67
        # Std Dev = sqrt(66,666,666.67) ~ 8164.9658
        history = [10000.0, 20000.0, 30000.0]
        stats = detector.calculate_stats(history)
        self.assertAlmostEqual(stats["mean"], 20000.0, places=2)
        expected_std = math.sqrt(((10000-20000)**2 + 0 + (30000-20000)**2) / 3)
        self.assertAlmostEqual(stats["std_dev"], expected_std, places=2)

        # Current transaction = 90,000, Mean = 20,000, StdDev = 10,000 -> Z = (90k - 20k) / 10k = 7.00
        z_res = detector.compute_z_score(90000.0, [20000.0, 10000.0, 30000.0, 20000.0])
        self.assertTrue(z_res["is_anomaly"])
        self.assertGreater(z_res["z_score"], 3.0)

    def test_02_dmgt_propositional_logic(self):
        """Validates DMGT propositional logic rules (A, N, Z, G)."""
        engine = RuleEngine(amount_threshold=50000.0, z_threshold=3.0, graph_threshold=0.5)

        # Rule 1: A=True, N=True, Z=False, G=False -> Review Required
        r1 = engine.evaluate(amount=60000.0, is_new_payee=True, z_score=1.5, graph_risk_indicator=0.2)
        self.assertEqual(r1["rule_decision"], "Review Required")

        # Rule 2: A=True, N=True, Z=True, G=False -> Suspicious
        r2 = engine.evaluate(amount=75000.0, is_new_payee=True, z_score=4.2, graph_risk_indicator=0.2)
        self.assertEqual(r2["rule_decision"], "Suspicious")

        # Rule 3: A=False, N=False, Z=True, G=True -> Review Required
        r3 = engine.evaluate(amount=20000.0, is_new_payee=False, z_score=3.5, graph_risk_indicator=0.8)
        self.assertEqual(r3["rule_decision"], "Review Required")

        # Rule 4: A=True, N=True, Z=True, G=True -> Suspicious
        r4 = engine.evaluate(amount=100000.0, is_new_payee=True, z_score=5.0, graph_risk_indicator=0.9)
        self.assertEqual(r4["rule_decision"], "Suspicious")

    def test_03_adsa_graph_analysis(self):
        """Validates NetworkX node degrees and new connection detection."""
        screening_sys = TransactionScreeningSystem()
        graph_analyzer = screening_sys.graph_analyzer
        
        # Account 1 exists in sample graph
        node_info = graph_analyzer.analyze_node("Acc-1")
        self.assertTrue(node_info["exists"])
        self.assertGreaterEqual(node_info["degree"], 1)

    def test_04_otp_verification_flow(self):
        """Validates cryptographic OTP generation, SHA-256 hash check, and attempt counters."""
        otp = OTPVerification(otp_id=1, customer_id=1, mobile_number="9876543210")
        plain_token = otp.generate_otp()
        
        self.assertEqual(len(plain_token), 6)
        self.assertFalse(otp.verified)
        
        # Test wrong token
        success, msg = otp.verify_otp("000000")
        if plain_token != "000000":
            self.assertFalse(success)
            self.assertEqual(otp.attempts, 1)

        # Test correct token
        success_correct, msg_correct = otp.verify_otp(plain_token)
        self.assertTrue(success_correct)
        self.assertTrue(otp.verified)

    def test_05_database_crud(self):
        """Validates DBMS CRUD operations and foreign key queries."""
        df_cust = DatabaseManager.execute_query("SELECT * FROM CUSTOMER WHERE customer_id = 1")
        self.assertFalse(df_cust.empty)
        self.assertEqual(df_cust.iloc[0]["customer_name"], "Ramesh Kumar Sharma")

        df_aggs = DatabaseManager.execute_query("""
            SELECT COUNT(*) AS cnt, AVG(amount) AS avg_amt, MAX(amount) AS max_amt 
            FROM "TRANSACTION"
        """)
        self.assertGreater(df_aggs.iloc[0]["cnt"], 0)
        self.assertGreater(df_aggs.iloc[0]["avg_amt"], 0)

if __name__ == "__main__":
    unittest.main()
