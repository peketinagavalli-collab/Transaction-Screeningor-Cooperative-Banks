"""
ER Model and Relational Metadata for the Cooperative Bank Transaction Screening System.
Used in the DBMS Subject Module and DMGT Relations Module.
"""

# ER Model entities and structural definitions
ER_ENTITIES = {
    "CUSTOMER": {
        "description": "Represents cooperative bank members and primary account holders.",
        "primary_key": "customer_id",
        "attributes": [
            {"name": "customer_id", "type": "INT", "key": "PK", "constraint": "AUTO_INCREMENT, PRIMARY KEY"},
            {"name": "customer_name", "type": "VARCHAR(100)", "key": "", "constraint": "NOT NULL"},
            {"name": "phone", "type": "VARCHAR(15)", "key": "UQ", "constraint": "NOT NULL, UNIQUE, CHECK (len >= 10)"},
            {"name": "email", "type": "VARCHAR(100)", "key": "UQ", "constraint": "NOT NULL, UNIQUE"},
            {"name": "created_at", "type": "TIMESTAMP", "key": "", "constraint": "DEFAULT CURRENT_TIMESTAMP"}
        ]
    },
    "ACCOUNT": {
        "description": "Represents bank accounts held by members (Savings, Agricultural Credit, Current, etc.).",
        "primary_key": "account_id",
        "attributes": [
            {"name": "account_id", "type": "INT", "key": "PK", "constraint": "AUTO_INCREMENT, PRIMARY KEY"},
            {"name": "customer_id", "type": "INT", "key": "FK", "constraint": "NOT NULL, REFERENCES CUSTOMER(customer_id)"},
            {"name": "account_type", "type": "VARCHAR(30)", "key": "", "constraint": "CHECK (Savings, Current, Agricultural, etc.)"},
            {"name": "balance", "type": "DECIMAL(15,2)", "key": "", "constraint": "NOT NULL, CHECK (balance >= 0)"},
            {"name": "account_status", "type": "VARCHAR(20)", "key": "", "constraint": "NOT NULL, DEFAULT 'Active'"},
            {"name": "created_at", "type": "TIMESTAMP", "key": "", "constraint": "DEFAULT CURRENT_TIMESTAMP"}
        ]
    },
    "PAYEE": {
        "description": "Represents beneficiary accounts in inter-bank or intra-bank transfers.",
        "primary_key": "payee_id",
        "attributes": [
            {"name": "payee_id", "type": "INT", "key": "PK", "constraint": "AUTO_INCREMENT, PRIMARY KEY"},
            {"name": "payee_name", "type": "VARCHAR(100)", "key": "", "constraint": "NOT NULL"},
            {"name": "bank_name", "type": "VARCHAR(100)", "key": "", "constraint": "NOT NULL"},
            {"name": "account_number", "type": "VARCHAR(30)", "key": "UQ", "constraint": "NOT NULL, UNIQUE"},
            {"name": "ifsc_code", "type": "VARCHAR(15)", "key": "", "constraint": "NOT NULL"}
        ]
    },
    "TRANSACTION": {
        "description": "Represents financial events (transfers, cash withdrawals, deposits).",
        "primary_key": "transaction_id",
        "attributes": [
            {"name": "transaction_id", "type": "INT", "key": "PK", "constraint": "AUTO_INCREMENT, PRIMARY KEY"},
            {"name": "account_id", "type": "INT", "key": "FK", "constraint": "NOT NULL, REFERENCES ACCOUNT(account_id)"},
            {"name": "payee_id", "type": "INT", "key": "FK", "constraint": "NULLABLE, REFERENCES PAYEE(payee_id)"},
            {"name": "amount", "type": "DECIMAL(15,2)", "key": "", "constraint": "NOT NULL, CHECK (amount > 0)"},
            {"name": "transaction_type", "type": "VARCHAR(30)", "key": "", "constraint": "NOT NULL, CHECK (Transfer, Withdrawal, etc.)"},
            {"name": "transaction_date", "type": "TIMESTAMP", "key": "", "constraint": "DEFAULT CURRENT_TIMESTAMP"},
            {"name": "location", "type": "VARCHAR(100)", "key": "", "constraint": "NOT NULL"},
            {"name": "status", "type": "VARCHAR(30)", "key": "", "constraint": "DEFAULT 'Completed'"}
        ]
    },
    "SCREENING_RESULT": {
        "description": "Stores mathematical & logical screening metrics for each evaluated transaction.",
        "primary_key": "result_id",
        "attributes": [
            {"name": "result_id", "type": "INT", "key": "PK", "constraint": "AUTO_INCREMENT, PRIMARY KEY"},
            {"name": "transaction_id", "type": "INT", "key": "FK", "constraint": "NOT NULL, UNIQUE, REFERENCES TRANSACTION"},
            {"name": "z_score", "type": "DECIMAL(8,4)", "key": "", "constraint": "NOT NULL, DEFAULT 0.00"},
            {"name": "rule_score", "type": "DECIMAL(5,2)", "key": "", "constraint": "NOT NULL, DEFAULT 0.00"},
            {"name": "graph_score", "type": "DECIMAL(5,2)", "key": "", "constraint": "NOT NULL, DEFAULT 0.00"},
            {"name": "risk_score", "type": "DECIMAL(5,2)", "key": "", "constraint": "NOT NULL, CHECK (0 <= risk_score <= 100)"},
            {"name": "decision", "type": "VARCHAR(30)", "key": "", "constraint": "CHECK (Normal, Review Required, Suspicious)"},
            {"name": "reasons", "type": "TEXT", "key": "", "constraint": "NOT NULL"},
            {"name": "screened_at", "type": "TIMESTAMP", "key": "", "constraint": "DEFAULT CURRENT_TIMESTAMP"}
        ]
    },
    "OTP_VERIFICATION": {
        "description": "Stores cryptographic SHA-256 OTP verification tokens for high-value cash withdrawals.",
        "primary_key": "otp_id",
        "attributes": [
            {"name": "otp_id", "type": "INT", "key": "PK", "constraint": "AUTO_INCREMENT, PRIMARY KEY"},
            {"name": "customer_id", "type": "INT", "key": "FK", "constraint": "NOT NULL, REFERENCES CUSTOMER"},
            {"name": "transaction_id", "type": "INT", "key": "FK", "constraint": "NULLABLE, REFERENCES TRANSACTION"},
            {"name": "mobile_number", "type": "VARCHAR(15)", "key": "", "constraint": "NOT NULL"},
            {"name": "otp_hash", "type": "VARCHAR(64)", "key": "", "constraint": "NOT NULL (SHA-256 Hash)"},
            {"name": "created_at", "type": "TIMESTAMP", "key": "", "constraint": "DEFAULT CURRENT_TIMESTAMP"},
            {"name": "expires_at", "type": "TIMESTAMP", "key": "", "constraint": "NOT NULL"},
            {"name": "verified", "type": "BOOLEAN", "key": "", "constraint": "DEFAULT FALSE"},
            {"name": "attempts", "type": "INT", "key": "", "constraint": "DEFAULT 0, MAX 3"}
        ]
    },
    "LOAN_APPLICATION": {
        "description": "Represents digital customer loan applications with personal profile, financial parameters, and status.",
        "primary_key": "loan_id",
        "attributes": [
            {"name": "loan_id", "type": "INT", "key": "PK", "constraint": "AUTO_INCREMENT, PRIMARY KEY"},
            {"name": "applicant_name", "type": "VARCHAR(100)", "key": "", "constraint": "NOT NULL"},
            {"name": "mobile", "type": "VARCHAR(15)", "key": "", "constraint": "NOT NULL"},
            {"name": "email", "type": "VARCHAR(100)", "key": "", "constraint": "NOT NULL"},
            {"name": "address", "type": "TEXT", "key": "", "constraint": "NOT NULL"},
            {"name": "dob", "type": "VARCHAR(20)", "key": "", "constraint": "NOT NULL"},
            {"name": "occupation", "type": "VARCHAR(50)", "key": "", "constraint": "NOT NULL"},
            {"name": "income", "type": "DECIMAL(15,2)", "key": "", "constraint": "NOT NULL, CHECK (income >= 0)"},
            {"name": "loan_type", "type": "VARCHAR(50)", "key": "", "constraint": "NOT NULL"},
            {"name": "requested_amount", "type": "DECIMAL(15,2)", "key": "", "constraint": "NOT NULL, CHECK (amount > 0)"},
            {"name": "loan_purpose", "type": "TEXT", "key": "", "constraint": "NOT NULL"},
            {"name": "repayment_period", "type": "VARCHAR(30)", "key": "", "constraint": "NOT NULL"},
            {"name": "application_date", "type": "TIMESTAMP", "key": "", "constraint": "DEFAULT CURRENT_TIMESTAMP"},
            {"name": "status", "type": "VARCHAR(40)", "key": "", "constraint": "DEFAULT 'Submitted'"},
            {"name": "overall_score", "type": "DECIMAL(5,2)", "key": "", "constraint": "DEFAULT 0.00"}
        ]
    },
    "LOAN_DOCUMENT": {
        "description": "Represents uploaded certificates and automated 6-parameter preliminary verification screening records.",
        "primary_key": "document_id",
        "attributes": [
            {"name": "document_id", "type": "INT", "key": "PK", "constraint": "AUTO_INCREMENT, PRIMARY KEY"},
            {"name": "loan_id", "type": "INT", "key": "FK", "constraint": "NOT NULL, REFERENCES LOAN_APPLICATION(loan_id)"},
            {"name": "document_type", "type": "VARCHAR(50)", "key": "", "constraint": "NOT NULL"},
            {"name": "file_name", "type": "VARCHAR(255)", "key": "", "constraint": "NOT NULL"},
            {"name": "file_path", "type": "VARCHAR(500)", "key": "", "constraint": "NOT NULL"},
            {"name": "file_size", "type": "INT", "key": "", "constraint": "NOT NULL"},
            {"name": "mime_type", "type": "VARCHAR(100)", "key": "", "constraint": "NOT NULL"},
            {"name": "sha256_hash", "type": "VARCHAR(64)", "key": "", "constraint": "NOT NULL"},
            {"name": "extracted_doc_number", "type": "VARCHAR(100)", "key": "", "constraint": ""},
            {"name": "issuing_authority", "type": "VARCHAR(150)", "key": "", "constraint": ""},
            {"name": "detected_date", "type": "VARCHAR(50)", "key": "", "constraint": ""},
            {"name": "name_match_status", "type": "VARCHAR(50)", "key": "", "constraint": "DEFAULT 'Pending'"},
            {"name": "verification_score", "type": "DECIMAL(5,2)", "key": "", "constraint": "DEFAULT 0.00"},
            {"name": "verification_status", "type": "VARCHAR(50)", "key": "", "constraint": "CHECK (PASS, REVIEW REQUIRED, UNABLE TO VERIFY)"},
            {"name": "uploaded_at", "type": "TIMESTAMP", "key": "", "constraint": "DEFAULT CURRENT_TIMESTAMP"}
        ]
    },
    "LOAN_REVIEW": {
        "description": "Stores official bank officer manual review audits, decisions, and comments.",
        "primary_key": "review_id",
        "attributes": [
            {"name": "review_id", "type": "INT", "key": "PK", "constraint": "AUTO_INCREMENT, PRIMARY KEY"},
            {"name": "loan_id", "type": "INT", "key": "FK", "constraint": "NOT NULL, REFERENCES LOAN_APPLICATION(loan_id)"},
            {"name": "officer_name", "type": "VARCHAR(100)", "key": "", "constraint": "NOT NULL"},
            {"name": "officer_status", "type": "VARCHAR(40)", "key": "", "constraint": "NOT NULL"},
            {"name": "officer_comments", "type": "TEXT", "key": "", "constraint": "NOT NULL"},
            {"name": "reviewed_at", "type": "TIMESTAMP", "key": "", "constraint": "DEFAULT CURRENT_TIMESTAMP"}
        ]
    }
}

# ER Relationships
ER_RELATIONSHIPS = [
    {
        "source": "CUSTOMER",
        "target": "ACCOUNT",
        "cardinality": "1 : N (One-to-Many)",
        "foreign_key": "ACCOUNT.customer_id -> CUSTOMER.customer_id",
        "description": "One Customer can hold multiple Accounts (Savings, Agriculture Loan, Fixed Deposit)."
    },
    {
        "source": "ACCOUNT",
        "target": "TRANSACTION",
        "cardinality": "1 : N (One-to-Many)",
        "foreign_key": "TRANSACTION.account_id -> ACCOUNT.account_id",
        "description": "One Account can execute multiple debit/credit Transactions over time."
    },
    {
        "source": "PAYEE",
        "target": "TRANSACTION",
        "cardinality": "1 : N (One-to-Many)",
        "foreign_key": "TRANSACTION.payee_id -> PAYEE.payee_id",
        "description": "One Payee/Beneficiary can receive transfers from multiple transactions."
    },
    {
        "source": "TRANSACTION",
        "target": "SCREENING_RESULT",
        "cardinality": "1 : 1 (One-to-One)",
        "foreign_key": "SCREENING_RESULT.transaction_id -> TRANSACTION.transaction_id",
        "description": "Each evaluated Transaction has exactly one corresponding Screening Result record."
    },
    {
        "source": "CUSTOMER",
        "target": "OTP_VERIFICATION",
        "cardinality": "1 : N (One-to-Many)",
        "foreign_key": "OTP_VERIFICATION.customer_id -> CUSTOMER.customer_id",
        "description": "A Customer may undergo multiple high-value withdrawal OTP verifications."
    },
    {
        "source": "LOAN_APPLICATION",
        "target": "LOAN_DOCUMENT",
        "cardinality": "1 : N (One-to-Many)",
        "foreign_key": "LOAN_DOCUMENT.loan_id -> LOAN_APPLICATION.loan_id",
        "description": "One Loan Application contains multiple uploaded certificates and verification records."
    },
    {
        "source": "LOAN_APPLICATION",
        "target": "LOAN_REVIEW",
        "cardinality": "1 : N (One-to-Many)",
        "foreign_key": "LOAN_REVIEW.loan_id -> LOAN_APPLICATION.loan_id",
        "description": "One Loan Application tracks an immutable history of bank officer review decisions."
    }
]

