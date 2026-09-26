"""
DMGT Subject Module: Propositional Logic & Discrete Binary Relations.
Presents Truth Tables, Formal Propositional Evaluators, and Set-Theoretic Relations (Domain, Range, Ordered Pairs).
"""

import streamlit as st
import pandas as pd
from database.db_connection import DatabaseManager
from services.rule_engine import RuleEngine

st.set_page_config(page_title="DMGT Logic & Relations | Coop Bank AI", page_icon="📐", layout="wide")

# Academic Header
st.markdown("""
<div style='background: linear-gradient(135deg, #1E3A8A 0%, #0F172A 100%); padding: 1.5rem 2rem; border-radius: 10px; color: white; margin-bottom: 1.2rem;'>
    <h1 style='color: white; margin: 0; font-size: 1.8rem; font-weight: 800;'>📐 DMGT Module: Propositional Logic & Binary Relations</h1>
    <p style='color: #93C5FD; margin: 0.3rem 0 0 0; font-size: 0.95rem;'>Discrete Mathematics & Graph Theory Foundations in Banking Risk Analysis</p>
</div>
""", unsafe_allow_html=True)

# Tabs: 1. Propositional Logic, 2. Binary Relations & Set Theory
tab_logic, tab_relations = st.tabs([
    "🧩 Section 1: Propositional Logic & Truth Table",
    "🔗 Section 2: Binary Relations (Domain, Range, Pairs)"
])

# -------------------------------------------------------------
# TAB 1: PROPOSITIONAL LOGIC
# -------------------------------------------------------------
with tab_logic:
    st.markdown("### 🧩 Propositional Logic in Transaction Screening")
    
    st.markdown("""
    In Discrete Mathematics, propositions are declarative statements that are either **True ($T$)** or **False ($F$)**.
    Our screening prototype establishes four atomic propositions:
    """)

    c_p1, c_p2 = st.columns(2)
    with c_p1:
        st.markdown(r"""
        - **$A$ (Amount Exceeds Threshold):**  
          $A = \text{True} \iff \text{Amount } x \ge \text{Threshold } (\text{default ₹50,000})$.
        - **$N$ (Payee is New):**  
          $N = \text{True} \iff (\text{Account}, \text{Payee}) \notin \text{Historical Transfer History}$.
        """)
    with c_p2:
        st.markdown(r"""
        - **$Z$ (Statistical Anomaly is High):**  
          $Z = \text{True} \iff |z| = \left|\frac{x - \mu}{\sigma}\right| \ge 3.0$.
        - **$G$ (Graph/Network Behavior is Unusual):**  
          $G = \text{True} \iff \text{Graph Risk Indicator } \ge 0.5$.
        """)

    st.markdown("---")
    st.markdown("#### 📜 Formal DMGT Logical Rules")
    
    col_r1, col_r2 = st.columns(2)
    with col_r1:
        st.info(r"**Rule 1:** $A \land N \implies \text{Review Required}$" + "\n\n*Meaning:* A high-value transfer to an unprecedented beneficiary warrants first-level verification.")
        st.error(r"**Rule 2:** $A \land N \land Z \implies \text{Suspicious}$" + "\n\n*Meaning:* A high-value transfer to a new beneficiary that also deviates drastically from historical patterns warrants high-priority investigation.")
    with col_r2:
        st.info(r"**Rule 3:** $Z \land G \implies \text{Review Required}$" + "\n\n*Meaning:* Co-occurrence of statistical anomaly and abnormal network graph behavior.")
        st.error(r"**Rule 4:** $A \land N \land Z \land G \implies \text{Suspicious}$" + "\n\n*Meaning:* Simultaneous conjunction of all four risk signals.")

    st.markdown("---")
    st.markdown("#### 📊 Complete 16-Row ($2^4$) Academic Truth Table")
    
    truth_rows = RuleEngine.get_truth_table()
    df_truth = pd.DataFrame(truth_rows)

    # Filter selector
    filter_choice = st.radio("Filter Truth Table by Decision:", ["All 16 Combinations", "Suspicious Only", "Review Required Only", "Normal Only"], horizontal=True)
    
    if filter_choice == "Suspicious Only":
        df_display = df_truth[df_truth["Consequence"] == "Suspicious"]
    elif filter_choice == "Review Required Only":
        df_display = df_truth[df_truth["Consequence"] == "Review Required"]
    elif filter_choice == "Normal Only":
        df_display = df_truth[df_truth["Consequence"] == "Normal"]
    else:
        df_display = df_truth

    st.dataframe(df_display, use_container_width=True, hide_index=True)


# -------------------------------------------------------------
# TAB 2: BINARY RELATIONS & SET THEORY
# -------------------------------------------------------------
with tab_relations:
    st.markdown("### 🔗 DMGT Binary Relations in Banking Database")
    
    st.markdown(r"""
    A **binary relation** $R$ from set $A$ to set $B$ is a subset of the Cartesian product $A \times B$:
    $$R \subseteq A \times B = \{(a, b) \mid a \in A \land b \in B\}$$
    - **Domain ($\text{Dom}(R)$):** The set of all first elements in the ordered pairs.
    - **Range ($\text{Ran}(R)$):** The set of all second elements in the ordered pairs.
    """)

    # Fetch active database data to generate real ordered pairs
    try:
        df_r1_data = DatabaseManager.execute_query("""
            SELECT account_id, transaction_id FROM "TRANSACTION" ORDER BY account_id, transaction_id LIMIT 12
        """)
        df_r2_data = DatabaseManager.execute_query("""
            SELECT transaction_id, payee_id FROM "TRANSACTION" WHERE payee_id IS NOT NULL ORDER BY transaction_id LIMIT 12
        """)
        df_r3_data = DatabaseManager.execute_query("""
            SELECT customer_id, account_id FROM ACCOUNT ORDER BY customer_id, account_id
        """)
    except Exception as e:
        st.error(f"Error extracting relations data: {e}")
        st.stop()

    c_rel1, c_rel2 = st.columns(2)

    with c_rel1:
        st.markdown("#### 1. Relation $R_1$: Account $\\to$ Transaction")
        st.markdown(r"**Definition:** $R_1 = \{(\text{Acc}_i, \text{Tx}_j) \mid \text{Account } i \text{ executed Transaction } j\}$")
        
        # Build ordered pairs set representation
        pairs_r1 = [(f"Acc-{row['account_id']}", f"Tx-{row['transaction_id']}") for _, row in df_r1_data.iterrows()]
        dom_r1 = sorted(list(set(p[0] for p in pairs_r1)))
        ran_r1 = sorted(list(set(p[1] for p in pairs_r1)))

        st.code("R1 = {\n  " + ",\n  ".join([f"({p[0]}, {p[1]})" for p in pairs_r1[:6]]) + ",\n  ...\n}", language="python")
        st.write(f"- **Domain($R_1$):** `{'{' + ', '.join(dom_r1[:5]) + ', ...}'}`")
        st.write(f"- **Range($R_1$):** `{'{' + ', '.join(ran_r1[:5]) + ', ...}'}`")
        st.write(f"- **Relation Cardinality:** $|R_1| = {len(pairs_r1)}$ ordered pairs sampled")

        st.markdown("---")
        st.markdown("#### 3. Relation $R_3$: Customer $\\to$ Account")
        st.markdown(r"**Definition:** $R_3 = \{(\text{Cust}_m, \text{Acc}_i) \mid \text{Customer } m \text{ holds Account } i\}$")
        
        pairs_r3 = [(f"Cust-{row['customer_id']}", f"Acc-{row['account_id']}") for _, row in df_r3_data.iterrows()]
        dom_r3 = sorted(list(set(p[0] for p in pairs_r3)))
        ran_r3 = sorted(list(set(p[1] for p in pairs_r3)))

        st.code("R3 = {\n  " + ",\n  ".join([f"({p[0]}, {p[1]})" for p in pairs_r3]) + "\n}", language="python")
        st.write(f"- **Domain($R_3$):** `{'{' + ', '.join(dom_r3) + '}'}`")
        st.write(f"- **Range($R_3$):** `{'{' + ', '.join(ran_r3) + '}'}`")

    with c_rel2:
        st.markdown("#### 2. Relation $R_2$: Transaction $\\to$ Payee")
        st.markdown(r"**Definition:** $R_2 = \{(\text{Tx}_j, \text{Payee}_k) \mid \text{Transaction } j \text{ transferred funds to Payee } k\}$")
        
        pairs_r2 = [(f"Tx-{row['transaction_id']}", f"Payee-{int(row['payee_id'])}") for _, row in df_r2_data.iterrows()]
        dom_r2 = sorted(list(set(p[0] for p in pairs_r2)))
        ran_r2 = sorted(list(set(p[1] for p in pairs_r2)))

        st.code("R2 = {\n  " + ",\n  ".join([f"({p[0]}, {p[1]})" for p in pairs_r2[:6]]) + ",\n  ...\n}", language="python")
        st.write(f"- **Domain($R_2$):** `{'{' + ', '.join(dom_r2[:5]) + ', ...}'}`")
        st.write(f"- **Range($R_2$):** `{'{' + ', '.join(ran_r2[:5]) + ', ...}'}`")
        st.write(f"- **Relation Cardinality:** $|R_2| = {len(pairs_r2)}$ ordered pairs sampled")

        st.markdown("---")
        st.markdown("#### 🔬 Composition of Relations ($R_1 \\circ R_2$)")
        st.markdown("""
        In DMGT, the **composition** $R_1 \\circ R_2$ maps an Account directly to a Payee through an intermediate Transaction:
        $$R_1 \\circ R_2 = \\{(a, c) \\mid \\exists t \\text{ such that } (a, t) \\in R_1 \\land (t, c) \\in R_2\\}$$
        """)
        st.info("This composite relation directly defines the directed edges in our **ADSA Graph Module**!")
