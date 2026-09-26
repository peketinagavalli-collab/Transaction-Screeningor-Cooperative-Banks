-- ==========================================================
-- AI-Based Suspicious Transaction Screening System
-- Relational Database Schema (MySQL 8.0+ / ANSI SQL)
-- For Cooperative Bank Transaction Monitoring Prototype
-- ==========================================================

-- Drop tables in reverse order of foreign key dependencies
DROP TABLE IF EXISTS OTP_VERIFICATION;
DROP TABLE IF EXISTS SCREENING_RESULT;
DROP TABLE IF EXISTS TRANSACTION;
DROP TABLE IF EXISTS PAYEE;
DROP TABLE IF EXISTS ACCOUNT;
DROP TABLE IF EXISTS CUSTOMER;

-- 1. CUSTOMER TABLE
-- Represents cooperative bank members/account holders
CREATE TABLE CUSTOMER (
    customer_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_name VARCHAR(100) NOT NULL,
    phone VARCHAR(15) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_customer_phone CHECK (LENGTH(phone) >= 10)
);

-- 2. ACCOUNT TABLE
-- Represents bank accounts owned by customers
CREATE TABLE ACCOUNT (
    account_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    account_type VARCHAR(30) NOT NULL DEFAULT 'Savings',
    balance DECIMAL(15, 2) NOT NULL DEFAULT 0.00,
    account_status VARCHAR(20) NOT NULL DEFAULT 'Active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_account_customer FOREIGN KEY (customer_id) 
        REFERENCES CUSTOMER(customer_id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT chk_account_type CHECK (account_type IN ('Savings', 'Current', 'Agricultural Credit', 'Recurring Deposit', 'Fixed Deposit')),
    CONSTRAINT chk_account_status CHECK (account_status IN ('Active', 'Dormant', 'Frozen', 'Closed')),
    CONSTRAINT chk_account_balance CHECK (balance >= 0.00)
);

-- 3. PAYEE TABLE
-- Represents beneficiary entities / third-party accounts
CREATE TABLE PAYEE (
    payee_id INT AUTO_INCREMENT PRIMARY KEY,
    payee_name VARCHAR(100) NOT NULL,
    bank_name VARCHAR(100) NOT NULL,
    account_number VARCHAR(30) NOT NULL UNIQUE,
    ifsc_code VARCHAR(15) NOT NULL DEFAULT 'COOP0001001',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. TRANSACTION TABLE
-- Represents transfers, withdrawals, deposits in the cooperative bank
CREATE TABLE TRANSACTION (
    transaction_id INT AUTO_INCREMENT PRIMARY KEY,
    account_id INT NOT NULL,
    payee_id INT NULL, -- NULL allowed for self-withdrawal/deposit
    amount DECIMAL(15, 2) NOT NULL,
    transaction_type VARCHAR(30) NOT NULL,
    transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    location VARCHAR(100) NOT NULL DEFAULT 'Main Branch',
    status VARCHAR(30) NOT NULL DEFAULT 'Completed',
    CONSTRAINT fk_txn_account FOREIGN KEY (account_id) 
        REFERENCES ACCOUNT(account_id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_txn_payee FOREIGN KEY (payee_id) 
        REFERENCES PAYEE(payee_id) ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT chk_txn_amount CHECK (amount > 0.00),
    CONSTRAINT chk_txn_type CHECK (transaction_type IN ('Transfer', 'Withdrawal', 'Deposit', 'UPI', 'NEFT', 'RTGS', 'IMPS')),
    CONSTRAINT chk_txn_status CHECK (status IN ('Completed', 'Pending', 'Flagged', 'Rejected', 'Under Review'))
);

-- 5. SCREENING_RESULT TABLE
-- Stores academic screening metrics, propositional logic, and decision
CREATE TABLE SCREENING_RESULT (
    result_id INT AUTO_INCREMENT PRIMARY KEY,
    transaction_id INT NOT NULL UNIQUE,
    z_score DECIMAL(8, 4) NOT NULL DEFAULT 0.0000,
    rule_score DECIMAL(5, 2) NOT NULL DEFAULT 0.00,
    graph_score DECIMAL(5, 2) NOT NULL DEFAULT 0.00,
    risk_score DECIMAL(5, 2) NOT NULL DEFAULT 0.00,
    decision VARCHAR(30) NOT NULL DEFAULT 'Normal',
    reasons TEXT NOT NULL,
    screened_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_screening_txn FOREIGN KEY (transaction_id) 
        REFERENCES TRANSACTION(transaction_id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT chk_screening_decision CHECK (decision IN ('Normal', 'Review Required', 'Suspicious')),
    CONSTRAINT chk_risk_score CHECK (risk_score >= 0.00 AND risk_score <= 100.00)
);

-- 6. OTP_VERIFICATION TABLE
-- Stores secure simulated OTP verification attempts for large cash withdrawals
CREATE TABLE OTP_VERIFICATION (
    otp_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    transaction_id INT NULL,
    mobile_number VARCHAR(15) NOT NULL,
    otp_hash VARCHAR(64) NOT NULL, -- SHA-256 hash for security
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    verified BOOLEAN NOT NULL DEFAULT FALSE,
    attempts INT NOT NULL DEFAULT 0,
    CONSTRAINT fk_otp_customer FOREIGN KEY (customer_id) 
        REFERENCES CUSTOMER(customer_id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_otp_txn FOREIGN KEY (transaction_id) 
        REFERENCES TRANSACTION(transaction_id) ON DELETE SET NULL ON UPDATE CASCADE
);

-- Indexes for query optimization
CREATE INDEX idx_txn_account ON TRANSACTION(account_id);
CREATE INDEX idx_txn_date ON TRANSACTION(transaction_date);
CREATE INDEX idx_screening_decision ON SCREENING_RESULT(decision);
