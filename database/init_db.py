"""
Database Initializer and Realistic Cooperative Bank Data Generator.
Creates relational tables and populates with representative academic test cases.
"""

import os
import sys
import hashlib
import datetime
import pandas as pd

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from database.db_connection import DatabaseManager, SQLITE_DB_PATH

def init_database(force_recreate: bool = False):
    """Initializes tables and populates base sample data."""
    engine = DatabaseManager.get_engine_name()
    print(f"Initializing database with engine: {engine}")

    # Read schema script
    schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
    with open(schema_path, "r") as f:
        schema_sql = f.read()

    # If using SQLite, adapt DDL statements (remove constraints/syntax specific to MySQL)
    if "SQLite" in engine:
        sqlite_ddl = """
        DROP TABLE IF EXISTS OTP_VERIFICATION;
        DROP TABLE IF EXISTS SCREENING_RESULT;
        DROP TABLE IF EXISTS "TRANSACTION";
        DROP TABLE IF EXISTS PAYEE;
        DROP TABLE IF EXISTS ACCOUNT;
        DROP TABLE IF EXISTS CUSTOMER;

        CREATE TABLE CUSTOMER (
            customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT NOT NULL,
            phone TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE ACCOUNT (
            account_id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL,
            account_type TEXT NOT NULL DEFAULT 'Savings',
            balance REAL NOT NULL DEFAULT 0.0,
            account_status TEXT NOT NULL DEFAULT 'Active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (customer_id) REFERENCES CUSTOMER(customer_id) ON DELETE CASCADE
        );

        CREATE TABLE PAYEE (
            payee_id INTEGER PRIMARY KEY AUTOINCREMENT,
            payee_name TEXT NOT NULL,
            bank_name TEXT NOT NULL,
            account_number TEXT NOT NULL UNIQUE,
            ifsc_code TEXT NOT NULL DEFAULT 'COOP0001001',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE "TRANSACTION" (
            transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_id INTEGER NOT NULL,
            payee_id INTEGER NULL,
            amount REAL NOT NULL,
            transaction_type TEXT NOT NULL,
            transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            location TEXT NOT NULL DEFAULT 'Main Branch',
            status TEXT NOT NULL DEFAULT 'Completed',
            FOREIGN KEY (account_id) REFERENCES ACCOUNT(account_id) ON DELETE CASCADE,
            FOREIGN KEY (payee_id) REFERENCES PAYEE(payee_id) ON DELETE SET NULL
        );

        CREATE TABLE SCREENING_RESULT (
            result_id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_id INTEGER NOT NULL UNIQUE,
            z_score REAL NOT NULL DEFAULT 0.0,
            rule_score REAL NOT NULL DEFAULT 0.0,
            graph_score REAL NOT NULL DEFAULT 0.0,
            risk_score REAL NOT NULL DEFAULT 0.0,
            decision TEXT NOT NULL DEFAULT 'Normal',
            reasons TEXT NOT NULL,
            screened_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (transaction_id) REFERENCES "TRANSACTION"(transaction_id) ON DELETE CASCADE
        );

        CREATE TABLE OTP_VERIFICATION (
            otp_id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL,
            transaction_id INTEGER NULL,
            mobile_number TEXT NOT NULL,
            otp_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP NOT NULL,
            verified INTEGER NOT NULL DEFAULT 0,
            attempts INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY (customer_id) REFERENCES CUSTOMER(customer_id) ON DELETE CASCADE,
            FOREIGN KEY (transaction_id) REFERENCES "TRANSACTION"(transaction_id) ON DELETE SET NULL
        );
        """
        DatabaseManager.execute_raw(sqlite_ddl)
    else:
        DatabaseManager.execute_raw(schema_sql)

    # Seed initial entities and realistic transactions
    seed_sample_data()
    print("Database successfully initialized and seeded with sample data.")

def seed_sample_data():
    """Seeds realistic cooperative banking entities, transactions, and screening results."""
    
    # 1. Customers (Members of the Cooperative Credit Society)
    customers = [
        ("Ramesh Kumar Sharma", "9876543210", "ramesh.sharma@coopbank.in"),
        ("Suresh Patel", "9823456781", "suresh.patel@coopbank.in"),
        ("Anjali Deshmukh", "9765432109", "anjali.deshmukh@coopbank.in"),
        ("Balwanth Singh", "9812345678", "balwanth.singh@coopbank.in"),
        ("Meena Kumari", "9945678123", "meena.kumari@coopbank.in"),
        ("Govind Narain", "9834567890", "govind.narain@coopbank.in"),
        ("Lakshmi Devi", "9789012345", "lakshmi.devi@coopbank.in"),
        ("Rajesh Varma", "9845012398", "rajesh.varma@coopbank.in"),
    ]
    for name, phone, email in customers:
        DatabaseManager.execute_query(
            "INSERT INTO CUSTOMER (customer_name, phone, email) VALUES (%s, %s, %s)",
            (name, phone, email),
            commit=True
        )

    # 2. Accounts (Savings, Agricultural Credit, Current)
    accounts = [
        (1, "Savings", 185000.00, "Active"),               # Ramesh (Account 1)
        (1, "Agricultural Credit", 250000.00, "Active"),   # Ramesh (Account 2)
        (2, "Savings", 95000.00, "Active"),                # Suresh (Account 3)
        (3, "Current", 450000.00, "Active"),               # Anjali (Account 4)
        (4, "Agricultural Credit", 120000.00, "Active"),   # Balwanth (Account 5)
        (5, "Savings", 60000.00, "Active"),                # Meena (Account 6)
        (6, "Savings", 80000.00, "Active"),                # Govind (Account 7)
        (7, "Recurring Deposit", 45000.00, "Active"),      # Lakshmi (Account 8)
        (8, "Current", 320000.00, "Active"),               # Rajesh (Account 9)
    ]
    for cust_id, acc_type, bal, status in accounts:
        DatabaseManager.execute_query(
            "INSERT INTO ACCOUNT (customer_id, account_type, balance, account_status) VALUES (%s, %s, %s, %s)",
            (cust_id, acc_type, bal, status),
            commit=True
        )

    # 3. Payees / Beneficiaries
    payees = [
        ("Kisan Agro Seeds & Fertilizers", "State Cooperative Apex Bank", "COOP0001099281", "COOP0001002"),
        ("Gramin Solar Pumps Ltd", "District Central Coop Bank", "COOP0001099452", "COOP0001003"),
        ("Shreeji Dairy Machinery", "National Agricultural Bank", "NAB0004928102", "NAB0002001"),
        ("Apex Cotton Mills", "State Cooperative Apex Bank", "COOP0001099781", "COOP0001002"),
        ("Siddhivinayak Tractor Spares", "District Central Coop Bank", "COOP0001099611", "COOP0001003"),
        ("Unknown Shell Entity Alpha", "Offshore Commercial Bank", "OFF0098716253", "OFF9900112"),
        ("FastCash P2P Merchant", "Private Payments Bank", "PAY0087612349", "PAY0001199")
    ]
    for pname, bname, acc_num, ifsc in payees:
        DatabaseManager.execute_query(
            "INSERT INTO PAYEE (payee_name, bank_name, account_number, ifsc_code) VALUES (%s, %s, %s, %s)",
            (pname, bname, acc_num, ifsc),
            commit=True
        )

    # 4. Realistic Seed Transactions & Historical Cash Withdrawals
    # Customer 1 (Ramesh, Account 1) Historical Cash Withdrawals (₹5,000 - ₹10,000 typical)
    # Plus regular inter-account and vendor transfers.
    base_txns = [
        # Customer 1 withdrawal history for pattern comparison
        (1, None, 5000.00, "Withdrawal", "2026-01-10 10:30:00", "Main Branch ATM", "Completed", 0.12, 10.0, 10.0, 12.0, "Normal", "Routine ATM withdrawal"),
        (1, None, 7000.00, "Withdrawal", "2026-01-25 11:15:00", "Main Branch ATM", "Completed", 0.28, 10.0, 10.0, 15.0, "Normal", "Routine ATM withdrawal"),
        (1, None, 10000.00, "Withdrawal", "2026-02-12 14:20:00", "Taluka Branch Counter", "Completed", 0.65, 15.0, 10.0, 18.0, "Normal", "Normal cash withdrawal"),
        (1, None, 6000.00, "Withdrawal", "2026-02-28 09:45:00", "Main Branch ATM", "Completed", 0.18, 10.0, 10.0, 14.0, "Normal", "Routine cash withdrawal"),
        (1, None, 8000.00, "Withdrawal", "2026-03-15 16:00:00", "Main Branch ATM", "Completed", 0.42, 10.0, 10.0, 16.0, "Normal", "Routine cash withdrawal"),
        
        # Customer 1 regular transfers to known vendor (Payee 1)
        (1, 1, 15000.00, "Transfer", "2026-02-05 11:00:00", "NetBanking", "Completed", 0.35, 10.0, 15.0, 18.0, "Normal", "Regular vendor payment"),
        (1, 1, 18000.00, "Transfer", "2026-03-02 12:30:00", "NetBanking", "Completed", 0.48, 10.0, 15.0, 20.0, "Normal", "Regular vendor payment"),
        
        # Account 2 (Agricultural Credit) transactions
        (2, 1, 22000.00, "Transfer", "2026-02-10 15:10:00", "Branch Counter", "Completed", 0.50, 15.0, 15.0, 22.0, "Normal", "Fertilizer purchase"),
        (2, 2, 35000.00, "Transfer", "2026-03-01 10:00:00", "Branch Counter", "Completed", 0.85, 20.0, 20.0, 28.0, "Normal", "Solar pump equipment payment"),
        
        # Account 3 (Suresh) regular transactions
        (3, 1, 12000.00, "Transfer", "2026-02-14 11:40:00", "UPI", "Completed", 0.20, 10.0, 15.0, 16.0, "Normal", "Routine agriculture supply"),
        (3, None, 6000.00, "Withdrawal", "2026-03-10 17:15:00", "Main Branch ATM", "Completed", 0.15, 10.0, 10.0, 14.0, "Normal", "Personal cash withdrawal"),

        # Account 4 (Anjali - Current Account) regular business transactions
        (4, 4, 45000.00, "Transfer", "2026-02-18 16:30:00", "NEFT", "Completed", 0.90, 20.0, 20.0, 25.0, "Normal", "Cotton mill supply batch 1"),
        (4, 4, 48000.00, "Transfer", "2026-03-05 14:10:00", "NEFT", "Completed", 0.95, 20.0, 20.0, 26.0, "Normal", "Cotton mill supply batch 2"),

        # Academic Case 1: Rule 1 (A AND N -> Review Required)
        # Suresh (Acc 3) transfers ₹75,000 (A=True) to New Payee 3 (N=True), moderate Z-score
        (3, 3, 75000.00, "Transfer", "2026-03-18 10:15:00", "NetBanking", "Under Review", 2.15, 60.0, 30.0, 52.0, "Review Required", "Amount exceeds threshold (₹50,000); New payee detected for this account"),

        # Academic Case 2: Rule 2 (A AND N AND Z -> Suspicious)
        # Ramesh (Acc 1) suddenly transfers ₹90,000 (A=True) to New Payee 6 (N=True) with Z-score 7.00 (Z=True)
        (1, 6, 90000.00, "Transfer", "2026-03-20 18:45:00", "NetBanking", "Flagged", 7.00, 85.0, 65.0, 82.0, "Suspicious", "Amount exceeds threshold; New payee detected; Statistical anomaly is high (Z=7.00); DMGT Rule 2 fired (A ∧ N ∧ Z)"),

        # Academic Case 3: Rule 3 (Z AND G -> Review Required)
        # Govind (Acc 7) transfers ₹45,000 (A=False) to Payee 7, but rapid out-degree spike (G=True) and Z-score 3.8 (Z=True)
        (7, 7, 45000.00, "Transfer", "2026-03-21 12:00:00", "UPI", "Under Review", 3.80, 40.0, 80.0, 62.0, "Review Required", "High statistical Z-score anomaly (Z=3.80); Graph network behavior is unusual (DMGT Rule 3 fired: Z ∧ G)"),

        # Academic Case 4: Rule 4 (A AND N AND Z AND G -> Suspicious)
        # Balwanth (Acc 5) transfers ₹150,000 to New Payee 6, rapid hub connection, Z-score 8.2 (All 4 propositions True)
        (5, 6, 150000.00, "Transfer", "2026-03-22 14:30:00", "RTGS", "Flagged", 8.20, 95.0, 90.0, 94.0, "Suspicious", "All conditions met: High Amount, New Payee, High Z-Score (Z=8.20), High Graph Centrality Risk (DMGT Rule 4 fired: A ∧ N ∧ Z ∧ G)")
    ]

    for acc_id, payee_id, amt, t_type, t_date, loc, status, z_val, r_score, g_score, risk_val, decision, reasons in base_txns:
        txn_id = DatabaseManager.execute_query(
            "INSERT INTO TRANSACTION (account_id, payee_id, amount, transaction_type, transaction_date, location, status) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (acc_id, payee_id, amt, t_type, t_date, loc, status),
            commit=True
        )
        
        DatabaseManager.execute_query(
            "INSERT INTO SCREENING_RESULT (transaction_id, z_score, rule_score, graph_score, risk_score, decision, reasons, screened_at) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            (txn_id, z_val, r_score, g_score, risk_val, decision, reasons, t_date),
            commit=True
        )

    # 5. Seed an OTP Verification record for demonstration
    demo_otp = "482910"
    otp_hash = hashlib.sha256(demo_otp.encode("utf-8")).hexdigest()
    expires = (datetime.datetime.now() + datetime.timedelta(minutes=5)).strftime("%Y-%m-%d %H:%M:%S")
    
    DatabaseManager.execute_query(
        "INSERT INTO OTP_VERIFICATION (customer_id, transaction_id, mobile_number, otp_hash, expires_at, verified, attempts) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s)",
        (1, 1, "9876543210", otp_hash, expires, 1, 1),
        commit=True
    )

    # Also export to sample_transactions.csv for easy reference
    export_sample_csv()

def export_sample_csv():
    """Exports seeded transactions to data/sample_transactions.csv."""
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    os.makedirs(data_dir, exist_ok=True)
    csv_path = os.path.join(data_dir, "sample_transactions.csv")
    
    df = DatabaseManager.execute_query("""
        SELECT 
            t.transaction_id,
            c.customer_id,
            c.customer_name,
            a.account_id,
            a.account_type,
            COALESCE(p.payee_name, 'Self / Cash') AS payee_name,
            COALESCE(p.bank_name, 'N/A') AS payee_bank,
            t.amount,
            t.transaction_type,
            t.transaction_date,
            t.location,
            t.status,
            sr.z_score,
            sr.rule_score,
            sr.graph_score,
            sr.risk_score,
            sr.decision,
            sr.reasons
        FROM TRANSACTION t
        JOIN ACCOUNT a ON t.account_id = a.account_id
        JOIN CUSTOMER c ON a.customer_id = c.customer_id
        LEFT JOIN PAYEE p ON t.payee_id = p.payee_id
        LEFT JOIN SCREENING_RESULT sr ON t.transaction_id = sr.transaction_id
        ORDER BY t.transaction_id ASC
    """)
    df.to_csv(csv_path, index=False)

if __name__ == "__main__":
    init_database(force_recreate=True)
