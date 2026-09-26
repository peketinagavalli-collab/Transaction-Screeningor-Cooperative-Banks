"""
Subject Mapping Academic Page.
Explicitly documents how each computer science subject syllabus maps to the implemented software prototype.
"""

import streamlit as st
import pandas as pd

st.set_page_config(page_title="Subject Mapping | Coop Bank AI", page_icon="🎓", layout="wide")

# Academic Header
st.markdown("""
<div style='background: linear-gradient(135deg, #1E3A8A 0%, #0F172A 100%); padding: 1.5rem 2rem; border-radius: 10px; color: white; margin-bottom: 1.2rem;'>
    <h1 style='color: white; margin: 0; font-size: 1.8rem; font-weight: 800;'>🎓 Academic Subject Mapping Matrix</h1>
    <p style='color: #93C5FD; margin: 0.3rem 0 0 0; font-size: 0.95rem;'>Curriculum Alignment & Syllabus Cross-Reference for External Examiners & Faculty Review</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
This project was constructed as an interdisciplinary computer science capstone prototype demonstrating practical applications of **five core subjects**:
""")

# 5 Subject Cards Layout
c_sub1, c_sub2 = st.columns(2)

with c_sub1:
    st.markdown(r"""
    ### 🗄️ 1. DBMS (Database Management Systems)
    - **Relational Data Modeling:** 3NF normalized relational schema (`CUSTOMER`, `ACCOUNT`, `PAYEE`, `TRANSACTION`, `SCREENING_RESULT`, `OTP_VERIFICATION`).
    - **Keys & Constraints:** Primary Keys (`AUTO_INCREMENT`), Foreign Keys with `ON DELETE CASCADE / SET NULL`, `UNIQUE` phone/email/account constraints, and `CHECK` constraints on amounts, balances, and enumerated types.
    - **SQL Operations:**
      - CRUD Operations (`INSERT`, `SELECT`, `UPDATE`, `DELETE`).
      - Aggregations: `COUNT(*)`, `AVG(amount)`, `MAX(amount)`, `SUM(amount)`.
      - Grouping: `GROUP BY status`, `GROUP BY decision`.
      - Complex Multi-Table Relational `JOIN` queries.
    - **Referential Integrity & Transaction ACID:** Automated rollback/commit transaction management and parameterized SQL execution.
    """)

    st.markdown(r"""
    ### 🕸️ 3. ADSA (Algorithms & Data Structures Analysis)
    - **Graph Data Structures:** NetworkX Directed Weighted Graph $\mathcal{G} = (\mathcal{V}, \mathcal{E}, \mathcal{W})$.
    - **Vertices ($\mathcal{V}$):** Accounts and Payee Beneficiaries.
    - **Directed Edges ($\mathcal{E}$):** Flow of transaction funds ($u \to v$).
    - **Weighted Edges ($\mathcal{W}$):** Financial volume transferred in INR (₹).
    - **Algorithmic Graph Metrics:**
      - In-degree ($d_{\text{in}}$) and Out-degree ($d_{\text{out}}$) calculations.
      - Degree Centrality and identification of high-connectivity Hub nodes.
      - Path search and detection of novel vs. recurring edges.
      - Graph risk indicator synthesis for structural anomaly estimation.
    """)

    st.markdown(r"""
    ### 🐍 5. Python & Statistics
    - **Gaussian Standardization:** Implementation of standard score Z-Score algorithm.
    - **Mathematical Formulations:** Arithmetic Mean ($\mu$), Standard Deviation ($\sigma$), and Variance calculations.
    - **Data Wrangling:** High-performance tabular transformation with Pandas & NumPy.
    - **Data Visualization:** Multi-modal interactive charts using Plotly Express and Graph Objects.
    - **Interactive Web Architecture:** Streamlit multi-page reactive application framework.
    """)

with c_sub2:
    st.markdown(r"""
    ### 📐 2. DMGT (Discrete Mathematics & Graph Theory)
    - **Propositional Logic:**
      - Atomic Propositions:
        - $A$: Amount exceeds threshold ($x \ge \text{Threshold}$)
        - $N$: Payee is new ($(\text{Acc}, \text{Payee}) \notin \text{History}$)
        - $Z$: Statistical anomaly is high ($|z| \ge 3.0$)
        - $G$: Graph/network behavior is unusual ($\text{Risk} \ge 0.5$)
      - Compound Logical Rules:
        - Rule 1: $A \land N \implies \text{Review Required}$
        - Rule 2: $A \land N \land Z \implies \text{Suspicious}$
        - Rule 3: $Z \land G \implies \text{Review Required}$
        - Rule 4: $A \land N \land Z \land G \implies \text{Suspicious}$
      - Full 16-Row ($2^4$) Academic Truth Table.
    - **Binary Relations & Set Theory:**
      - Relation $R_1 \subseteq \text{Account} \times \text{Transaction}$
      - Relation $R_2 \subseteq \text{Transaction} \times \text{Payee}$
      - Relation $R_3 \subseteq \text{Customer} \times \text{Account}$
      - Formal definitions and display of Domain, Range, and Ordered Pairs.
      - Composition of Relations: $R_1 \circ R_2$.
    """)

    st.markdown("""
    ### ☕ 4. OOPJ (Object-Oriented Programming Principles)
    - **Class Encapsulation:** Private attributes (`_customer_id`, `_balance`, `_otp_hash`) protected with `@property` getters and validation setters.
    - **Domain Entities:** `Customer`, `Account`, `Payee`, `Transaction`, `ScreeningResult`, `OTPVerification`.
    - **Service Composition:** `RuleEngine`, `AnomalyDetector`, `GraphAnalyzer`, `OTPService`, `TransactionScreeningSystem`.
    - **State Management & Methods:** `Account.debit()`, `Account.credit()`, `OTPVerification.verify_otp()`, `RuleEngine.evaluate()`.
    - **Security Best Practices:** Cryptographic SHA-256 OTP hashing avoiding plain-text database persistence.
    """)

st.markdown("---")

# Summary Table for Quick Viva Review
st.markdown("### 📊 Subject-to-Code Implementation Matrix")

matrix_data = [
    {"Subject": "1. DBMS", "Theoretical Concept": "Relational Model, ER Diagrams, Normalization, SQL Aggregates, Joins", "Source Code Files": "`database/schema.sql`, `database/queries.sql`, `database/db_connection.py`, `pages/08_🗄️_DBMS_ER_and_SQL.py`"},
    {"Subject": "2. DMGT", "Theoretical Concept": "Propositional Logic, Truth Tables, Compound Rules, Binary Relations, Set Theory", "Source Code Files": "`services/rule_engine.py`, `pages/07_📐_DMGT_Logic_Relations.py`"},
    {"Subject": "3. ADSA", "Theoretical Concept": "NetworkX Directed Weighted Graphs, Degree Centrality, Hub Detection, Graph Density", "Source Code Files": "`services/graph_analyzer.py`, `pages/05_🕸️_Transaction_Network.py`"},
    {"Subject": "4. OOPJ", "Theoretical Concept": "Encapsulation, Constructors, Properties, Composition, Domain Models", "Source Code Files": "`models/*.py`, `services/*.py`"},
    {"Subject": "5. Python", "Theoretical Concept": "Descriptive Statistics, Z-Score, Data Analysis, Reactive UI", "Source Code Files": "`services/anomaly_detector.py`, `app.py`, `pages/*.py`"},
]

st.dataframe(pd.DataFrame(matrix_data), use_container_width=True, hide_index=True)
