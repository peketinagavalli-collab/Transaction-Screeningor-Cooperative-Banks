"""
Formula & Decision Explanation Page (Academic Presentation Module).
Dedicated mathematical derivation and step-by-step arithmetic breakdown for examiners and students.
"""

import streamlit as st
import pandas as pd
from database.db_connection import DatabaseManager
from services.anomaly_detector import AnomalyDetector
from services.rule_engine import RuleEngine

st.set_page_config(page_title="Formulas & Decision Explanation | Coop Bank AI", page_icon="🧮", layout="wide")

# Academic Header
st.markdown("""
<div style='background: linear-gradient(135deg, #1E3A8A 0%, #0F172A 100%); padding: 1.5rem 2rem; border-radius: 10px; color: white; margin-bottom: 1.2rem;'>
    <h1 style='color: white; margin: 0; font-size: 1.8rem; font-weight: 800;'>🧮 Mathematical Formulas & Decision Explanation</h1>
    <p style='color: #93C5FD; margin: 0.3rem 0 0 0; font-size: 0.95rem;'>Academic Derivations, Statistical Gaussian Standardization & Propositional Logic Synthesis</p>
</div>
""", unsafe_allow_html=True)

# Academic Disclaimer Banner
st.markdown("""
<div style='background-color: #FEF3C7; border-left: 4px solid #F59E0B; padding: 0.7rem 1rem; border-radius: 6px; color: #92400E; font-size: 0.85rem; margin-bottom: 1.2rem;'>
    ⚠️ <b>Academic Disclaimer:</b> The mathematical models presented below represent standard undergraduate statistics and discrete logic formulations implemented for transaction risk estimation.
</div>
""", unsafe_allow_html=True)

# 1. CORE FORMULAS MASTER DISPLAY
st.markdown("### 📚 Core Academic Formulas Used by the System")

f_col1, f_col2 = st.columns(2)

with f_col1:
    st.markdown(r"""
    #### 📐 FORMULA 1: Sample Arithmetic Mean ($\mu$)
    Calculates the central tendency of the member's historical transaction amounts:
    """)
    st.latex(r"\mu = \frac{\sum_{i=1}^{n} x_i}{n} = \frac{x_1 + x_2 + \dots + x_n}{n}")
    st.caption(r"Where $n$ is the total historical transaction count and $x_i$ is each recorded transaction amount.")

    st.markdown(r"""
    #### 📐 FORMULA 2: Sample Standard Deviation ($\sigma$)
    Measures the dispersion or volatility of transaction amounts around the mean:
    """)
    st.latex(r"\sigma = \sqrt{\frac{\sum_{i=1}^{n} (x_i - \mu)^2}{n}}")
    st.caption(r"Where $(x_i - \mu)^2$ represents the squared deviation of each transaction from the average.")

    st.markdown(r"""
    #### 📐 FORMULA 3: Standard Score / Z-Score ($z$)
    Standardizes the current transaction amount against the historical Gaussian distribution:
    """)
    st.latex(r"z = \frac{x - \mu}{\sigma}")
    st.caption(r"Academic Threshold Rule: If $|z| \ge 3.0 \implies \text{Statistical Anomaly} = \text{TRUE}$, else $\text{FALSE}$.")

with f_col2:
    st.markdown(r"""
    #### 📐 FORMULA 4: DMGT Propositional Logic Rules
    Formal logical implications mapping atomic proposition truth values to screening decisions:
    """)
    st.latex(r"\text{Rule 1: } A \land N \implies \text{Review Required}")
    st.latex(r"\text{Rule 2: } A \land N \land Z \implies \text{Suspicious}")
    st.latex(r"\text{Rule 3: } Z \land G \implies \text{Review Required}")
    st.latex(r"\text{Rule 4: } A \land N \land Z \land G \implies \text{Suspicious}")
    st.caption(r"Where $A = (x \ge \text{Threshold})$, $N = (\text{New Payee})$, $Z = (|z| \ge 3.0)$, $G = (\text{Graph Risk} \ge 0.5)$.")

    st.markdown(r"""
    #### 📐 FORMULA 5: Multi-Signal Composite Risk Score
    Linear convex combination of multi-modal risk indicators normalized to $[0, 100]$:
    """)
    st.latex(r"\text{RiskScore} = w_1(\text{RuleRisk}) + w_2(\text{StatisticalRisk}) + w_3(\text{GraphRisk}) + w_4(\text{PatternRisk})")
    st.caption(r"Where default demonstration weights satisfy: $w_1 = 0.30, w_2 = 0.30, w_3 = 0.20, w_4 = 0.20$ and $\sum w_i = 1.0$.")

st.markdown("---")

# 2. LIVE STEP-BY-STEP CALCULATION DEMONSTRATION
st.markdown("### 🔬 Live Mathematical & Logical Calculation for Selected Transaction")

try:
    df_txns = DatabaseManager.execute_query("""
        SELECT 
            t.transaction_id,
            c.customer_name,
            a.account_id,
            COALESCE(p.payee_name, 'Self / ATM') AS payee_name,
            t.amount,
            t.transaction_type,
            t.transaction_date,
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
        JOIN SCREENING_RESULT sr ON t.transaction_id = sr.transaction_id
        ORDER BY t.transaction_id DESC
    """)
except Exception as e:
    st.error(f"Error fetching data: {e}")
    st.stop()

if not df_txns.empty:
    txn_id_choice = st.selectbox(
        "Choose a transaction from the database to inspect exact step-by-step arithmetic:",
        options=df_txns["transaction_id"].tolist(),
        format_func=lambda tid: f"Txn #{tid} - {df_txns[df_txns['transaction_id'] == tid].iloc[0]['customer_name']} (₹{df_txns[df_txns['transaction_id'] == tid].iloc[0]['amount']:,.2f} - {df_txns[df_txns['transaction_id'] == tid].iloc[0]['decision']})"
    )

    t_data = df_txns[df_txns["transaction_id"] == txn_id_choice].iloc[0]
    acc_id = t_data["account_id"]
    current_x = float(t_data["amount"])

    # Fetch historical amounts prior to this transaction
    hist_query = """
        SELECT amount FROM "TRANSACTION"
        WHERE account_id = %s AND transaction_id < %s
        ORDER BY transaction_date ASC
    """
    df_hist = DatabaseManager.execute_query(hist_query, (acc_id, txn_id_choice))
    hist_amounts = df_hist["amount"].astype(float).tolist() if not df_hist.empty else [20000.0, 10000.0, 30000.0]

    # Run fresh AnomalyDetector & RuleEngine for explicit derivation
    detector = AnomalyDetector(z_threshold=3.0)
    stat_eval = detector.compute_z_score(current_x, hist_amounts)
    step = stat_eval["step_by_step"]

    c_calc1, c_calc2 = st.columns(2)

    with c_calc1:
        st.markdown("#### 1️⃣ Statistical Calculation Steps")
        st.write(f"- **Current Transaction Amount ($x$):** ₹{current_x:,.2f}")
        st.write(f"- **Historical Sample Size ($n$):** {step['n']} past transactions")
        st.write(rf"- **Sum of Past Amounts ($\sum x_i$):** ₹{step['sum_x']:,.2f}")
        
        st.markdown("**Mean Evaluation:**")
        st.latex(step["calc_mean_str"])

        st.markdown("**Standard Deviation Evaluation:**")
        st.latex(step["calc_std_str"])

        st.markdown("**Z-Score Evaluation:**")
        st.latex(step["calc_z_str"])
        st.latex(step["decision_str"])

    with c_calc2:
        st.markdown("#### 2️⃣ DMGT Logic & Composite Decision")
        
        # Determine propositions
        A_val = current_x >= 50000.0
        N_val = "New" in t_data["reasons"] or t_data["payee_name"] != "Self / ATM"
        Z_val = abs(stat_eval["z_score"]) >= 3.0
        G_val = float(t_data["graph_score"]) >= 50.0

        st.markdown(rf"""
        **Atomic Propositions Truth Values:**
        - $A$ (Amount $\ge$ ₹50,000): **{'TRUE' if A_val else 'FALSE'}**
        - $N$ (New Payee): **{'TRUE' if N_val else 'FALSE'}**
        - $Z$ (Z-Score $\ge$ 3.0): **{'TRUE' if Z_val else 'FALSE'}**
        - $G$ (Graph Risk $\ge$ 0.5): **{'TRUE' if G_val else 'FALSE'}**
        """)

        st.markdown("---")
        st.markdown("##### 📜 Compound Logic Rules Evaluation:")
        r1_val = A_val and N_val
        r2_val = A_val and N_val and Z_val
        r3_val = Z_val and G_val
        r4_val = A_val and N_val and Z_val and G_val

        st.write(rf"- $A \land N$ (Rule 1): `{'TRUE ⟹ Review Required' if r1_val else 'FALSE'}`")
        st.write(rf"- $A \land N \land Z$ (Rule 2): `{'TRUE ⟹ Suspicious' if r2_val else 'FALSE'}`")
        st.write(rf"- $Z \land G$ (Rule 3): `{'TRUE ⟹ Review Required' if r3_val else 'FALSE'}`")
        st.write(rf"- $A \land N \land Z \land G$ (Rule 4): `{'TRUE ⟹ Suspicious' if r4_val else 'FALSE'}`")

        # Final verdict banner
        dec_str = t_data["decision"]
        risk_val = float(t_data["risk_score"])
        
        st.markdown(f"""
        <div style='background: #1E293B; color: white; padding: 1rem; border-radius: 8px; margin-top: 1rem;'>
            <div style='font-size: 0.8rem; color: #94A3B8;'>FINAL SYSTEM VERDICT:</div>
            <div style='font-size: 1.6rem; font-weight: 800; color: #F59E0B;'>{dec_str.upper()}</div>
            <div style='font-size: 0.9rem; color: #CBD5E1;'>Calculated Risk Score: <b>{risk_val:.1f} / 100</b></div>
            <div style='font-size: 0.8rem; color: #93C5FD; margin-top: 0.5rem;'><b>Reasons:</b> {t_data['reasons']}</div>
        </div>
        """, unsafe_allow_html=True)

# 3. CLASSIC WORKED ACADEMIC EXAMPLE SLIDE
st.markdown("---")
st.markdown("### 🎓 Academic Standard Worked Example (For Presentation / Viva)")

st.markdown("""
<div class='formula-box'>
    <b>Academic Scenario:</b><br>
    A member who regularly transacts around ₹20,000 (with standard deviation ₹10,000) suddenly initiates a ₹90,000 transfer to a brand new beneficiary.
    <br><br>
    <b>1. Statistical Z-Score:</b><br>
    $$z = \\frac{90,000 - 20,000}{10,000} = \\frac{70,000}{10,000} = 7.00$$
    $$\\text{Since } |z| = 7.00 \\ge 3.00 \\implies \\text{STATISTICAL ANOMALY } (Z) = \\text{TRUE}$$
    <br>
    <b>2. Proposition Truth Values:</b><br>
    $$A = \\text{TRUE} \\quad (₹90,000 \\ge ₹50,000)$$
    $$N = \\text{TRUE} \\quad (\\text{First-time Payee})$$
    $$Z = \\text{TRUE} \\quad (|z| = 7.00 \\ge 3.0)$$
    $$G = \\text{FALSE} \\quad (\\text{Normal Hub Behavior})$$
    <br>
    <b>3. Propositional Logic Synthesis:</b><br>
    $$A \\land N \\land Z = \\text{TRUE} \\land \\text{TRUE} \\land \\text{TRUE} = \\text{TRUE} \\implies \\text{Rule 2 Fires: } \\mathbf{SUSPICIOUS}$$
    <br>
    <b>4. Output Reasons:</b><br>
    &bull; Amount exceeds threshold<br>
    &bull; New payee detected<br>
    &bull; High statistical anomaly (Z = 7.00)<br>
    &bull; DMGT Rule 2 fired ($A \\land N \\land Z$)
</div>
""", unsafe_allow_html=True)
