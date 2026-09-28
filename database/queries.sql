-- ==========================================================
-- AI-Based Suspicious Transaction Screening System
-- Standard SQL Queries Demonstration (DBMS Academic Module)
-- ==========================================================

-- ----------------------------------------------------------
-- 1. DATA INSERTION QUERIES (CRUD - Create)
-- ----------------------------------------------------------

-- Insert a new customer
INSERT INTO CUSTOMER (customer_name, phone, email) 
VALUES ('Ramesh Kumar Sharma', '9876543210', 'ramesh.sharma@coopbank.in');

-- Insert a new account for customer 1
INSERT INTO ACCOUNT (customer_id, account_type, balance, account_status)
VALUES (1, 'Savings', 125000.00, 'Active');

-- Insert a new payee
INSERT INTO PAYEE (payee_name, bank_name, account_number, ifsc_code)
VALUES ('Kisan Agro Machinery Ltd', 'State Cooperative Bank', 'COOP987654321', 'COOP0001002');

-- Insert a new transaction
INSERT INTO TRANSACTION (account_id, payee_id, amount, transaction_type, transaction_date, location, status)
VALUES (1, 1, 75000.00, 'Transfer', CURRENT_TIMESTAMP, 'Rural Branch A', 'Completed');

-- Insert a screening result record
INSERT INTO SCREENING_RESULT (transaction_id, z_score, rule_score, graph_score, risk_score, decision, reasons)
VALUES (1, 3.42, 60.00, 40.00, 68.00, 'Review Required', 'Amount exceeds threshold; High statistical z-score');

-- Insert OTP verification record
INSERT INTO OTP_VERIFICATION (customer_id, transaction_id, mobile_number, otp_hash, expires_at, verified, attempts)
VALUES (1, 1, '9876543210', 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', DATE_ADD(CURRENT_TIMESTAMP, INTERVAL 5 MINUTE), FALSE, 0);


-- ----------------------------------------------------------
-- 2. DATA UPDATE QUERIES (CRUD - Update)
-- ----------------------------------------------------------

-- Update transaction status to 'Under Review'
UPDATE TRANSACTION 
SET status = 'Under Review'
WHERE transaction_id = 1;

-- Update account balance following a transaction
UPDATE ACCOUNT
SET balance = balance - 75000.00
WHERE account_id = 1 AND balance >= 75000.00;

-- Update OTP verification status after correct token entry
UPDATE OTP_VERIFICATION
SET verified = TRUE, attempts = attempts + 1
WHERE otp_id = 1;


-- ----------------------------------------------------------
-- 3. DATA DELETION QUERIES (CRUD - Delete)
-- ----------------------------------------------------------

-- Delete an outdated transaction (Cascades to Screening Result if configured)
DELETE FROM TRANSACTION 
WHERE transaction_id = 999;


-- ----------------------------------------------------------
-- 4. SEARCH TRANSACTION QUERIES (CRUD - Read / Filter)
-- ----------------------------------------------------------

-- Search transaction by ID
SELECT * FROM TRANSACTION 
WHERE transaction_id = 1;

-- Search transactions by date range and minimum amount
SELECT * FROM TRANSACTION 
WHERE amount >= 50000.00 
  AND transaction_date >= '2026-01-01 00:00:00'
ORDER BY transaction_date DESC;

-- Search transactions by Account ID
SELECT * FROM TRANSACTION 
WHERE account_id = 1
ORDER BY transaction_date DESC;


-- ----------------------------------------------------------
-- 5. DISPLAY SUSPICIOUS / FLAGGED TRANSACTIONS
-- ----------------------------------------------------------

SELECT 
    t.transaction_id,
    c.customer_name,
    a.account_id,
    p.payee_name,
    p.bank_name AS payee_bank,
    t.amount,
    t.transaction_type,
    t.transaction_date,
    sr.z_score,
    sr.risk_score,
    sr.decision,
    sr.reasons
FROM TRANSACTION t
INNER JOIN ACCOUNT a ON t.account_id = a.account_id
INNER JOIN CUSTOMER c ON a.customer_id = c.customer_id
LEFT JOIN PAYEE p ON t.payee_id = p.payee_id
INNER JOIN SCREENING_RESULT sr ON t.transaction_id = sr.transaction_id
WHERE sr.decision IN ('Suspicious', 'Review Required')
ORDER BY sr.risk_score DESC, t.transaction_date DESC;


-- ----------------------------------------------------------
-- 6. AGGREGATE QUERIES (GROUP BY, AVG, MAX, SUM, COUNT)
-- ----------------------------------------------------------

-- Group by transaction status with count and sum
SELECT 
    status,
    COUNT(*) AS total_transactions,
    SUM(amount) AS total_volume,
    AVG(amount) AS average_amount,
    MAX(amount) AS highest_amount,
    MIN(amount) AS lowest_amount
FROM TRANSACTION
GROUP BY status;

-- Group by screening decision (Academic categorization)
SELECT 
    decision,
    COUNT(*) AS count_of_transactions,
    ROUND(AVG(risk_score), 2) AS avg_risk_score,
    ROUND(AVG(z_score), 4) AS avg_z_score,
    ROUND(SUM(t.amount), 2) AS total_screened_amount
FROM SCREENING_RESULT sr
JOIN TRANSACTION t ON sr.transaction_id = t.transaction_id
GROUP BY decision;

-- Overall aggregates
SELECT 
    COUNT(*) AS total_screened_count,
    ROUND(AVG(amount), 2) AS avg_transaction_amount,
    MAX(amount) AS max_transaction_amount,
    ROUND(SUM(amount), 2) AS total_transaction_volume
FROM TRANSACTION;


-- ----------------------------------------------------------
-- 7. MULTI-TABLE JOIN QUERIES
-- ----------------------------------------------------------

-- Join Account, Transaction, and Payee tables
SELECT 
    t.transaction_id,
    a.account_id,
    a.account_type,
    a.balance,
    p.payee_name,
    p.bank_name,
    p.account_number AS payee_account_num,
    t.amount,
    t.transaction_type,
    t.transaction_date,
    t.location,
    t.status
FROM TRANSACTION t
JOIN ACCOUNT a ON t.account_id = a.account_id
LEFT JOIN PAYEE p ON t.payee_id = p.payee_id
ORDER BY t.transaction_date DESC;

-- Comprehensive 5-table Join for Complete Transaction Audit
SELECT 
    c.customer_id,
    c.customer_name,
    c.phone,
    a.account_id,
    a.account_type,
    t.transaction_id,
    t.amount,
    t.transaction_type,
    t.transaction_date,
    COALESCE(p.payee_name, 'Self / ATM') AS payee_name,
    sr.z_score,
    sr.rule_score,
    sr.graph_score,
    sr.risk_score,
    sr.decision,
    sr.reasons
FROM CUSTOMER c
JOIN ACCOUNT a ON c.customer_id = a.customer_id
JOIN TRANSACTION t ON a.account_id = t.account_id
LEFT JOIN PAYEE p ON t.payee_id = p.payee_id
LEFT JOIN SCREENING_RESULT sr ON t.transaction_id = sr.transaction_id
ORDER BY t.transaction_id DESC;


-- ----------------------------------------------------------
-- 8. CUSTOMER WITHDRAWAL HISTORY (For OTP & Z-Score Analysis)
-- ----------------------------------------------------------

SELECT 
    t.transaction_id,
    t.amount,
    t.transaction_date,
    t.location
FROM TRANSACTION t
JOIN ACCOUNT a ON t.account_id = a.account_id
WHERE a.customer_id = 1 
  AND t.transaction_type = 'Withdrawal'
ORDER BY t.transaction_date DESC;


-- ----------------------------------------------------------
-- 9. ONLINE LOAN APPLICATION & DOCUMENT VERIFICATION QUERIES
-- ----------------------------------------------------------

-- Fetch all loan applications with composite scores and document counts
SELECT 
    la.loan_id,
    la.applicant_name,
    la.mobile,
    la.loan_type,
    la.requested_amount,
    la.income,
    la.status,
    la.overall_score,
    COUNT(ld.document_id) AS total_documents,
    SUM(CASE WHEN ld.verification_status = 'PASS' THEN 1 ELSE 0 END) AS passed_documents
FROM LOAN_APPLICATION la
LEFT JOIN LOAN_DOCUMENT ld ON la.loan_id = ld.loan_id
GROUP BY la.loan_id
ORDER BY la.loan_id DESC;

-- Detailed Document Verification Score Breakdown for a specific loan
SELECT 
    ld.document_id,
    ld.loan_id,
    ld.document_type,
    ld.file_name,
    ld.extracted_doc_number,
    ld.name_match_status,
    ld.file_validity_score,
    ld.text_consistency_score,
    ld.identity_consistency_score,
    ld.qr_verification_score,
    ld.signature_check_score,
    ld.integrity_check_score,
    ld.verification_score,
    ld.verification_status
FROM LOAN_DOCUMENT ld
WHERE ld.loan_id = 1;

-- Fetch Bank Officer Audit Trail for Loan Reviews
SELECT 
    lr.review_id,
    lr.loan_id,
    la.applicant_name,
    lr.officer_name,
    lr.officer_status,
    lr.officer_comments,
    lr.reviewed_at
FROM LOAN_REVIEW lr
JOIN LOAN_APPLICATION la ON lr.loan_id = la.loan_id
ORDER BY lr.reviewed_at DESC;

