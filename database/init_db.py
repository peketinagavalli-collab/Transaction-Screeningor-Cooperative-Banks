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
        DROP TABLE IF EXISTS LOAN_REVIEW;
        DROP TABLE IF EXISTS LOAN_DOCUMENT;
        DROP TABLE IF EXISTS LOAN_APPLICATION;
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

        CREATE TABLE LOAN_APPLICATION (
            loan_id INTEGER PRIMARY KEY AUTOINCREMENT,
            applicant_name TEXT NOT NULL,
            mobile TEXT NOT NULL,
            email TEXT NOT NULL,
            address TEXT NOT NULL,
            dob TEXT NOT NULL,
            occupation TEXT NOT NULL,
            income REAL NOT NULL,
            loan_type TEXT NOT NULL,
            requested_amount REAL NOT NULL,
            loan_purpose TEXT NOT NULL,
            repayment_period TEXT NOT NULL,
            application_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT NOT NULL DEFAULT 'Submitted',
            overall_score REAL NOT NULL DEFAULT 0.0
        );

        CREATE TABLE LOAN_DOCUMENT (
            document_id INTEGER PRIMARY KEY AUTOINCREMENT,
            loan_id INTEGER NOT NULL,
            document_type TEXT NOT NULL,
            file_name TEXT NOT NULL,
            file_path TEXT NOT NULL,
            file_size INTEGER NOT NULL,
            mime_type TEXT NOT NULL,
            sha256_hash TEXT NOT NULL,
            extracted_text TEXT,
            extracted_doc_number TEXT,
            issuing_authority TEXT,
            detected_date TEXT,
            name_match_status TEXT DEFAULT 'Pending',
            file_validity_score REAL NOT NULL DEFAULT 0.0,
            text_consistency_score REAL NOT NULL DEFAULT 0.0,
            identity_consistency_score REAL NOT NULL DEFAULT 0.0,
            qr_verification_score REAL NOT NULL DEFAULT 0.0,
            signature_check_score REAL NOT NULL DEFAULT 0.0,
            integrity_check_score REAL NOT NULL DEFAULT 0.0,
            verification_score REAL NOT NULL DEFAULT 0.0,
            verification_status TEXT NOT NULL DEFAULT 'UNABLE TO VERIFY',
            verification_details TEXT,
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (loan_id) REFERENCES LOAN_APPLICATION(loan_id) ON DELETE CASCADE
        );

        CREATE TABLE LOAN_REVIEW (
            review_id INTEGER PRIMARY KEY AUTOINCREMENT,
            loan_id INTEGER NOT NULL,
            officer_name TEXT NOT NULL DEFAULT 'Bank Officer',
            officer_status TEXT NOT NULL,
            officer_comments TEXT NOT NULL,
            reviewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (loan_id) REFERENCES LOAN_APPLICATION(loan_id) ON DELETE CASCADE
        );
        """
        DatabaseManager.execute_raw(sqlite_ddl)
    else:
        DatabaseManager.execute_raw(schema_sql)

    # Seed initial entities, transactions, and sample loan applications
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
        (3, 3, 75000.00, "Transfer", "2026-03-18 10:15:00", "NetBanking", "Under Review", 2.15, 60.0, 30.0, 52.0, "Review Required", "Amount exceeds threshold (₹50,000); New payee detected for this account"),

        # Academic Case 2: Rule 2 (A AND N AND Z -> Suspicious)
        (1, 6, 90000.00, "Transfer", "2026-03-20 18:45:00", "NetBanking", "Flagged", 7.00, 85.0, 65.0, 82.0, "Suspicious", "Amount exceeds threshold; New payee detected; Statistical anomaly is high (Z=7.00); DMGT Rule 2 fired (A ∧ N ∧ Z)"),

        # Academic Case 3: Rule 3 (Z AND G -> Review Required)
        (7, 7, 45000.00, "Transfer", "2026-03-21 12:00:00", "UPI", "Under Review", 3.80, 40.0, 80.0, 62.0, "Review Required", "High statistical Z-score anomaly (Z=3.80); Graph network behavior is unusual (DMGT Rule 3 fired: Z ∧ G)"),

        # Academic Case 4: Rule 4 (A AND N AND Z AND G -> Suspicious)
        (5, 6, 150000.00, "Transfer", "2026-03-22 14:30:00", "RTGS", "Flagged", 8.20, 95.0, 90.0, 94.0, "Suspicious", "All conditions met: High Amount, New Payee, High Z-Score (Z=8.20), High Graph Centrality Risk (DMGT Rule 4 fired: A ∧ N ∧ Z ∧ G)")
    ]

    for acc_id, payee_id, amt, t_type, t_date, loc, status, z_val, r_score, g_score, risk_val, decision, reasons in base_txns:
        txn_id = DatabaseManager.execute_query(
            "INSERT INTO \"TRANSACTION\" (account_id, payee_id, amount, transaction_type, transaction_date, location, status) "
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

    # 6. Seed Sample Realistic Loan Applications with Documents & Officer Reviews
    seed_loan_applications()

    # Also export to sample_transactions.csv for easy reference
    export_sample_csv()

def seed_loan_applications():
    """Seeds realistic cooperative bank loan applications for instant testing."""
    sample_loans = [
        # Loan 1: Farmer Agricultural Credit (Approved)
        {
            "applicant_name": "Ramesh Kumar Sharma",
            "mobile": "9876543210",
            "email": "ramesh.sharma@coopbank.in",
            "address": "Village Pipariya, Tehsil Hoshangabad, MP - 461001",
            "dob": "1982-05-14",
            "occupation": "Farmer / Agriculturalist",
            "income": 45000.00,
            "loan_type": "Agricultural Credit Loan",
            "requested_amount": 250000.00,
            "loan_purpose": "Purchase of high-yield wheat seeds, drip irrigation equipment, and organic fertilizer for Rabi harvest season.",
            "repayment_period": "36 Months",
            "application_date": "2026-03-10 11:20:00",
            "status": "Approved",
            "overall_score": 92.5,
            "documents": [
                {
                    "document_type": "Aadhaar/Identity Proof",
                    "file_name": "ramesh_aadhaar_card.pdf",
                    "file_path": "data/uploads/loan_documents/seed_ramesh_aadhaar.pdf",
                    "file_size": 142850,
                    "mime_type": "application/pdf",
                    "sha256_hash": "a1b2c3d4e5f60718293a4b5c6d7e8f90123456789abcdef0123456789abcdef0",
                    "extracted_text": "Government of India Unique Identification Authority of India UIDAI Name: Ramesh Kumar Sharma DOB: 14/05/1982 Gender: Male 9821-4820-1928",
                    "extracted_doc_number": "9821-4820-1928",
                    "issuing_authority": "Unique Identification Authority of India",
                    "detected_date": "14/05/1982",
                    "name_match_status": "Matched (Exact/Complete)",
                    "file_validity_score": 1.0,
                    "text_consistency_score": 0.95,
                    "identity_consistency_score": 1.0,
                    "qr_verification_score": 0.95,
                    "signature_check_score": 0.85,
                    "integrity_check_score": 1.0,
                    "verification_score": 96.0,
                    "verification_status": "PASS"
                },
                {
                    "document_type": "Income Certificate",
                    "file_name": "ramesh_income_cert_2026.pdf",
                    "file_path": "data/uploads/loan_documents/seed_ramesh_income.pdf",
                    "file_size": 218900,
                    "mime_type": "application/pdf",
                    "sha256_hash": "b2c3d4e5f60718293a4b5c6d7e8f90123456789abcdef0123456789abcdef01",
                    "extracted_text": "Revenue Department Government Certificate of Annual Income Tahsildar Certified that Shri Ramesh Kumar Sharma Annual Income Rs 5,40,000 Digitally signed by Tahsildar Ref: REV-2026-89102",
                    "extracted_doc_number": "REV-2026-89102",
                    "issuing_authority": "Revenue Department",
                    "detected_date": "10/02/2026",
                    "name_match_status": "Matched (Exact/Complete)",
                    "file_validity_score": 1.0,
                    "text_consistency_score": 0.90,
                    "identity_consistency_score": 0.95,
                    "qr_verification_score": 0.80,
                    "signature_check_score": 0.85,
                    "integrity_check_score": 0.95,
                    "verification_score": 89.0,
                    "verification_status": "PASS"
                }
            ],
            "reviews": [
                {
                    "officer_name": "A. K. Mukherjee (Chief Credit Manager)",
                    "officer_status": "Approved",
                    "officer_comments": "Verified land revenue records (Khasra/Khatauni) and crop yield history. Automated screening score 92.5% passed. Agricultural loan approved under priority sector lending guidelines.",
                    "reviewed_at": "2026-03-12 14:30:00"
                }
            ]
        },
        # Loan 2: Small Business Loan (Under Manual Review)
        {
            "applicant_name": "Suresh Patel",
            "mobile": "9823456781",
            "email": "suresh.patel@coopbank.in",
            "address": "Shop No 14, Main Market, Anand, Gujarat - 388001",
            "dob": "1978-11-22",
            "occupation": "Small Business Owner / Dairy Distributor",
            "income": 75000.00,
            "loan_type": "Small Business / MSME Loan",
            "requested_amount": 500000.00,
            "loan_purpose": "Expansion of commercial milk chilling unit and cold storage delivery van.",
            "repayment_period": "48 Months",
            "application_date": "2026-03-22 09:15:00",
            "status": "Manual Review",
            "overall_score": 68.5,
            "documents": [
                {
                    "document_type": "Bank Statement",
                    "file_name": "suresh_bank_statement_6m.pdf",
                    "file_path": "data/uploads/loan_documents/seed_suresh_bank.pdf",
                    "file_size": 312000,
                    "mime_type": "application/pdf",
                    "sha256_hash": "c3d4e5f60718293a4b5c6d7e8f90123456789abcdef0123456789abcdef012",
                    "extracted_text": "District Central Cooperative Bank Account Statement Suresh Patel Account 3091823901 IFSC COOP0001003 Balance 95000",
                    "extracted_doc_number": "3091823901",
                    "issuing_authority": "District Central Cooperative Bank",
                    "detected_date": "15/03/2026",
                    "name_match_status": "Matched (Exact/Complete)",
                    "file_validity_score": 1.0,
                    "text_consistency_score": 0.85,
                    "identity_consistency_score": 0.90,
                    "qr_verification_score": 0.70,
                    "signature_check_score": 0.65,
                    "integrity_check_score": 0.90,
                    "verification_score": 83.0,
                    "verification_status": "PASS"
                },
                {
                    "document_type": "Income Certificate",
                    "file_name": "suresh_tax_returns_scan.jpg",
                    "file_path": "data/uploads/loan_documents/seed_suresh_tax.jpg",
                    "file_size": 195000,
                    "mime_type": "image/jpeg",
                    "sha256_hash": "d4e5f60718293a4b5c6d7e8f90123456789abcdef0123456789abcdef0123",
                    "extracted_text": "Scanned income return summary document. Text resolution is low.",
                    "extracted_doc_number": "ITR-2025-981",
                    "issuing_authority": "Revenue Department",
                    "detected_date": "2025-10-15",
                    "name_match_status": "Partial Match (Requires Verification)",
                    "file_validity_score": 0.85,
                    "text_consistency_score": 0.45,
                    "identity_consistency_score": 0.60,
                    "qr_verification_score": 0.50,
                    "signature_check_score": 0.50,
                    "integrity_check_score": 0.60,
                    "verification_score": 54.0,
                    "verification_status": "REVIEW REQUIRED"
                }
            ],
            "reviews": [
                {
                    "officer_name": "System Auto-Screening Bot",
                    "officer_status": "Manual Review",
                    "officer_comments": "Automated screening detected 1 document requiring manual verification (Tax returns scan has lower contrast). Routed to Senior Loan Officer for branch inspection.",
                    "reviewed_at": "2026-03-22 09:16:00"
                }
            ]
        },
        # Loan 3: New Customer Loan (Submitted / Document Verification Stage)
        {
            "applicant_name": "Anjali Deshmukh",
            "mobile": "9765432109",
            "email": "anjali.deshmukh@coopbank.in",
            "address": "Plot 45, Cotton Market Road, Wardha, Maharashtra - 442001",
            "dob": "1990-08-19",
            "occupation": "Salaried / Textile Engineer",
            "income": 95000.00,
            "loan_type": "Home / Rural Housing Loan",
            "requested_amount": 1200000.00,
            "loan_purpose": "Construction of residential rural housing on ancestral land plot.",
            "repayment_period": "120 Months",
            "application_date": "2026-03-25 15:40:00",
            "status": "Document Verification",
            "overall_score": 88.0,
            "documents": [
                {
                    "document_type": "Salary Slip",
                    "file_name": "anjali_salary_slip_feb2026.pdf",
                    "file_path": "data/uploads/loan_documents/seed_anjali_salary.pdf",
                    "file_size": 178000,
                    "mime_type": "application/pdf",
                    "sha256_hash": "e5f60718293a4b5c6d7e8f90123456789abcdef0123456789abcdef01234",
                    "extracted_text": "Apex Cotton Mills Ltd Pay Slip for February 2026 Employee Name: Anjali Deshmukh Designation: Senior Engineer Basic Pay: 65000 Gross: 95000 Net Pay: 84200",
                    "extracted_doc_number": "EMP-9821",
                    "issuing_authority": "Apex Cotton Mills",
                    "detected_date": "28/02/2026",
                    "name_match_status": "Matched (Exact/Complete)",
                    "file_validity_score": 1.0,
                    "text_consistency_score": 0.95,
                    "identity_consistency_score": 1.0,
                    "qr_verification_score": 0.70,
                    "signature_check_score": 0.75,
                    "integrity_check_score": 0.95,
                    "verification_score": 88.0,
                    "verification_status": "PASS"
                }
            ],
            "reviews": [
                {
                    "officer_name": "System Auto-Screening Bot",
                    "officer_status": "Document Verification",
                    "officer_comments": "Automated document screening passed with score 88.0%. Awaiting bank officer inspection of land registry deeds.",
                    "reviewed_at": "2026-03-25 15:41:00"
                }
            ]
        }
    ]

    for loan_data in sample_loans:
        loan_id = DatabaseManager.execute_query("""
            INSERT INTO LOAN_APPLICATION (
                applicant_name, mobile, email, address, dob, occupation,
                income, loan_type, requested_amount, loan_purpose,
                repayment_period, application_date, status, overall_score
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            loan_data["applicant_name"],
            loan_data["mobile"],
            loan_data["email"],
            loan_data["address"],
            loan_data["dob"],
            loan_data["occupation"],
            loan_data["income"],
            loan_data["loan_type"],
            loan_data["requested_amount"],
            loan_data["loan_purpose"],
            loan_data["repayment_period"],
            loan_data["application_date"],
            loan_data["status"],
            loan_data["overall_score"]
        ), commit=True)

        for doc in loan_data.get("documents", []):
            import json
            details_json = json.dumps({
                "formula_breakdown": {
                    "file_validity": {"weight": 0.20, "score": doc["file_validity_score"], "component_pct": doc["file_validity_score"] * 20},
                    "text_consistency": {"weight": 0.20, "score": doc["text_consistency_score"], "component_pct": doc["text_consistency_score"] * 20},
                    "identity_consistency": {"weight": 0.20, "score": doc["identity_consistency_score"], "component_pct": doc["identity_consistency_score"] * 20},
                    "qr_verification": {"weight": 0.15, "score": doc["qr_verification_score"], "component_pct": doc["qr_verification_score"] * 15},
                    "signature_check": {"weight": 0.10, "score": doc["signature_check_score"], "component_pct": doc["signature_check_score"] * 10},
                    "integrity_check": {"weight": 0.15, "score": doc["integrity_check_score"], "component_pct": doc["integrity_check_score"] * 15}
                },
                "status_message": "Document passed automated screening" if doc["verification_status"] == "PASS" else "Document requires manual verification"
            })
            DatabaseManager.execute_query("""
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
            """, (
                loan_id,
                doc["document_type"],
                doc["file_name"],
                doc["file_path"],
                doc["file_size"],
                doc["mime_type"],
                doc["sha256_hash"],
                doc["extracted_text"],
                doc["extracted_doc_number"],
                doc["issuing_authority"],
                doc["detected_date"],
                doc["name_match_status"],
                doc["file_validity_score"],
                doc["text_consistency_score"],
                doc["identity_consistency_score"],
                doc["qr_verification_score"],
                doc["signature_check_score"],
                doc["integrity_check_score"],
                doc["verification_score"],
                doc["verification_status"],
                details_json,
                loan_data["application_date"]
            ), commit=True)

        for rev in loan_data.get("reviews", []):
            DatabaseManager.execute_query("""
                INSERT INTO LOAN_REVIEW (loan_id, officer_name, officer_status, officer_comments, reviewed_at)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                loan_id,
                rev["officer_name"],
                rev["officer_status"],
                rev["officer_comments"],
                rev["reviewed_at"]
            ), commit=True)

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
        FROM "TRANSACTION" t
        JOIN ACCOUNT a ON t.account_id = a.account_id
        JOIN CUSTOMER c ON a.customer_id = c.customer_id
        LEFT JOIN PAYEE p ON t.payee_id = p.payee_id
        LEFT JOIN SCREENING_RESULT sr ON t.transaction_id = sr.transaction_id
        ORDER BY t.transaction_id ASC
    """)
    df.to_csv(csv_path, index=False)

if __name__ == "__main__":
    init_database(force_recreate=True)

