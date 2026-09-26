"""
DBMS Subject Module: Entity-Relationship (ER) Model & Interactive SQL Query Runner.
Demonstrates Relational Algebra, DDL Constraints, Normalization, and Multi-Table SQL Queries.
"""

import streamlit as st
import pandas as pd
from database.db_connection import DatabaseManager
from database.er_model import ER_ENTITIES, ER_RELATIONSHIPS

st.set_page_config(page_title="DBMS ER Model & SQL | Coop Bank AI", page_icon="🗄️", layout="wide")

# Academic Header
st.markdown("""
<div style='background: linear-gradient(135deg, #1E3A8A 0%, #0F172A 100%); padding: 1.5rem 2rem; border-radius: 10px; color: white; margin-bottom: 1.2rem;'>
    <h1 style='color: white; margin: 0; font-size: 1.8rem; font-weight: 800;'>🗄️ DBMS Module: Relational ER Model & SQL Explorer</h1>
    <p style='color: #93C5FD; margin: 0.3rem 0 0 0; font-size: 0.95rem;'>Relational Schemas, Primary/Foreign Key Constraints & Interactive Query Console</p>
</div>
""", unsafe_allow_html=True)

# Tabs: 1. ER Model & Schemas, 2. Interactive SQL Runner & Preset Queries
tab_er, tab_sql, tab_crud = st.tabs([
    "📐 Section 1: ER Model & Relational Schema",
    "💻 Section 2: Interactive SQL Query Console",
    "📝 Section 3: Academic SQL Demonstration Scripts"
])

# -------------------------------------------------------------
# TAB 1: ER MODEL & RELATIONAL SCHEMAS
# -------------------------------------------------------------
with tab_er:
    st.markdown("### 📐 Entity-Relationship (ER) Architecture")
    
    # ER Diagram using Mermaid
    st.markdown("""
    ```mermaid
    erDiagram
        CUSTOMER ||--o{ ACCOUNT : "1:N (owns)"
        ACCOUNT ||--o{ TRANSACTION : "1:N (initiates)"
        PAYEE ||--o{ TRANSACTION : "1:N (receives)"
        TRANSACTION ||--|| SCREENING_RESULT : "1:1 (evaluated as)"
        CUSTOMER ||--o{ OTP_VERIFICATION : "1:N (authenticates)"

        CUSTOMER {
            int customer_id PK
            string customer_name
            string phone UK
            string email UK
        }
        ACCOUNT {
            int account_id PK
            int customer_id FK
            string account_type
            decimal balance
            string account_status
        }
        PAYEE {
            int payee_id PK
            string payee_name
            string bank_name
            string account_number UK
        }
        TRANSACTION {
            int transaction_id PK
            int account_id FK
            int payee_id FK
            decimal amount
            string transaction_type
            timestamp transaction_date
        }
        SCREENING_RESULT {
            int result_id PK
            int transaction_id FK
            decimal z_score
            decimal risk_score
            string decision
            text reasons
        }
        OTP_VERIFICATION {
            int otp_id PK
            int customer_id FK
            int transaction_id FK
            string otp_hash
            boolean verified
        }
    ```
    """)

    st.markdown("---")
    st.markdown("#### 📋 Database Table Schema & Constraints Breakdown")

    for table_name, meta in ER_ENTITIES.items():
        with st.expander(f"📦 Table: {table_name} (PK: {meta['primary_key']})", expanded=False):
            st.write(f"**Description:** {meta['description']}")
            df_attr = pd.DataFrame(meta["attributes"])
            st.dataframe(
                df_attr,
                column_config={
                    "name": "Attribute Name",
                    "type": "Data Type",
                    "key": "Key Type",
                    "constraint": "Integrity Constraints"
                },
                use_container_width=True,
                hide_index=True
            )

    st.markdown("---")
    st.markdown("#### 🔗 Referential Integrity Relationships")
    df_rel = pd.DataFrame(ER_RELATIONSHIPS)
    st.dataframe(df_rel, use_container_width=True, hide_index=True)


# -------------------------------------------------------------
# TAB 2: INTERACTIVE SQL QUERY CONSOLE
# -------------------------------------------------------------
with tab_sql:
    st.markdown("### 💻 Interactive SQL Query Console")
    st.markdown("Execute customized SQL queries directly against the database with parameterized safety checks:")

    # Preset academic query selector
    preset_queries = {
        "1. Aggregate: Group by Transaction Status (COUNT, SUM, AVG, MAX)": """
SELECT 
    status,
    COUNT(*) AS total_transactions,
    ROUND(SUM(amount), 2) AS total_volume,
    ROUND(AVG(amount), 2) AS average_amount,
    ROUND(MAX(amount), 2) AS maximum_amount
FROM "TRANSACTION"
GROUP BY status;
""",
        "2. Screening Aggregates: Group by Decision (Academic Breakdown)": """
SELECT 
    sr.decision,
    COUNT(*) AS transaction_count,
    ROUND(AVG(sr.risk_score), 2) AS average_risk_score,
    ROUND(AVG(sr.z_score), 4) AS average_z_score,
    ROUND(SUM(t.amount), 2) AS total_screened_amount
FROM SCREENING_RESULT sr
JOIN "TRANSACTION" t ON sr.transaction_id = t.transaction_id
GROUP BY sr.decision;
""",
        "3. Multi-Table Join: Account, Customer, Transaction & Payee": """
SELECT 
    t.transaction_id,
    c.customer_name,
    a.account_type,
    COALESCE(p.payee_name, 'Self / Cash') AS beneficiary,
    t.amount,
    t.transaction_type,
    sr.decision,
    sr.risk_score
FROM "TRANSACTION" t
JOIN ACCOUNT a ON t.account_id = a.account_id
JOIN CUSTOMER c ON a.customer_id = c.customer_id
LEFT JOIN PAYEE p ON t.payee_id = p.payee_id
LEFT JOIN SCREENING_RESULT sr ON t.transaction_id = sr.transaction_id
ORDER BY t.transaction_id DESC;
""",
        "4. High-Priority Alert Query: Suspicious & Review Required Transactions": """
SELECT 
    t.transaction_id,
    c.customer_name,
    t.amount,
    sr.z_score,
    sr.risk_score,
    sr.decision,
    sr.reasons
FROM "TRANSACTION" t
JOIN ACCOUNT a ON t.account_id = a.account_id
JOIN CUSTOMER c ON a.customer_id = c.customer_id
JOIN SCREENING_RESULT sr ON t.transaction_id = sr.transaction_id
WHERE sr.decision IN ('Suspicious', 'Review Required')
ORDER BY sr.risk_score DESC;
""",
        "5. Overall Summary Aggregates (COUNT, AVG, MAX, SUM)": """
SELECT 
    COUNT(*) AS total_transactions,
    ROUND(AVG(amount), 2) AS avg_transaction_amount,
    ROUND(MAX(amount), 2) AS max_transaction_amount,
    ROUND(SUM(amount), 2) AS total_transaction_volume
FROM "TRANSACTION";
"""
    }

    selected_preset = st.selectbox("Choose a Preset Academic SQL Query:", list(preset_queries.keys()))
    default_sql = preset_queries[selected_preset]

    query_input = st.text_area("SQL Editor:", value=default_sql.strip(), height=150)

    if st.button("▶️ RUN SQL QUERY", type="primary"):
        try:
            # Safety check: restrict destructive drop commands in interactive console
            if "DROP DATABASE" in query_input.upper():
                st.error("Operation not permitted in interactive demonstration.")
            else:
                df_out = DatabaseManager.execute_query(query_input)
                if isinstance(df_out, pd.DataFrame):
                    st.success(f"Query returned {len(df_out)} row(s) successfully.")
                    st.dataframe(df_out, use_container_width=True)
                else:
                    st.success("Query executed successfully.")
        except Exception as err:
            st.error(f"SQL Error: {err}")


# -------------------------------------------------------------
# TAB 3: ACADEMIC SQL DEMONSTRATION SCRIPTS
# -------------------------------------------------------------
with tab_crud:
    st.markdown("### 📝 Standard SQL Query Scripts (DBMS Syllabus Mapping)")
    
    st.markdown("""
    Below are the standard SQL scripts implemented across CRUD operations, referential integrity checks, and joins:
    """)

    sql_categories = {
        "1. Insert Transaction (CRUD - Create)": """
INSERT INTO TRANSACTION (account_id, payee_id, amount, transaction_type, transaction_date, location, status)
VALUES (1, 1, 75000.00, 'Transfer', CURRENT_TIMESTAMP, 'Rural Branch A', 'Completed');
""",
        "2. Update Transaction Status (CRUD - Update)": """
UPDATE TRANSACTION 
SET status = 'Under Review'
WHERE transaction_id = 1;
""",
        "3. Delete Transaction (CRUD - Delete)": """
DELETE FROM TRANSACTION 
WHERE transaction_id = 999;
""",
        "4. Search Transaction (CRUD - Read)": """
SELECT * FROM TRANSACTION 
WHERE amount >= 50000.00 
  AND transaction_date >= '2026-01-01 00:00:00'
ORDER BY transaction_date DESC;
""",
        "5. Multi-Table Join Query": """
SELECT 
    t.transaction_id, a.account_id, a.account_type, 
    p.payee_name, p.bank_name, t.amount, t.status
FROM TRANSACTION t
JOIN ACCOUNT a ON t.account_id = a.account_id
LEFT JOIN PAYEE p ON t.payee_id = p.payee_id;
"""
    }

    for cat_title, sql_text in sql_categories.items():
        st.markdown(f"#### {cat_title}")
        st.code(sql_text.strip(), language="sql")
