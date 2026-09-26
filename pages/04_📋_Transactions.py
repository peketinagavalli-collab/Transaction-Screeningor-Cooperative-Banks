"""
Transaction Ledger & Deep Audit Details Page.
Allows searching, filtering, and deep multi-modal parameter inspection of any transaction.
"""

import streamlit as st
import pandas as pd
from database.db_connection import DatabaseManager

st.set_page_config(page_title="Transactions | Coop Bank AI", page_icon="📋", layout="wide")

# Academic Header
st.markdown("""
<div style='background: linear-gradient(135deg, #1E3A8A 0%, #0F172A 100%); padding: 1.5rem 2rem; border-radius: 10px; color: white; margin-bottom: 1.2rem;'>
    <h1 style='color: white; margin: 0; font-size: 1.8rem; font-weight: 800;'>📋 Transaction Audit Ledger & Inspection</h1>
    <p style='color: #93C5FD; margin: 0.3rem 0 0 0; font-size: 0.95rem;'>Comprehensive Multi-Table Search & In-Depth Parameter Breakdown</p>
</div>
""", unsafe_allow_html=True)

# Fetch all transactions with joined Customer, Account, Payee, and Screening Result
try:
    df_txns = DatabaseManager.execute_query("""
        SELECT 
            t.transaction_id,
            c.customer_id,
            c.customer_name,
            c.phone,
            a.account_id,
            a.account_type,
            a.balance,
            COALESCE(p.payee_id, 0) AS payee_id,
            COALESCE(p.payee_name, 'Self / Cash / ATM') AS payee_name,
            COALESCE(p.bank_name, 'N/A') AS payee_bank,
            t.amount,
            t.transaction_type,
            t.transaction_date,
            t.location,
            t.status,
            COALESCE(sr.z_score, 0.0) AS z_score,
            COALESCE(sr.rule_score, 0.0) AS rule_score,
            COALESCE(sr.graph_score, 0.0) AS graph_score,
            COALESCE(sr.risk_score, 0.0) AS risk_score,
            COALESCE(sr.decision, 'Normal') AS decision,
            COALESCE(sr.reasons, 'Routine transaction') AS reasons
        FROM "TRANSACTION" t
        JOIN ACCOUNT a ON t.account_id = a.account_id
        JOIN CUSTOMER c ON a.customer_id = c.customer_id
        LEFT JOIN PAYEE p ON t.payee_id = p.payee_id
        LEFT JOIN SCREENING_RESULT sr ON t.transaction_id = sr.transaction_id
        ORDER BY t.transaction_date DESC, t.transaction_id DESC
    """)
except Exception as e:
    st.error(f"Error querying transactions from database: {e}")
    st.stop()

# Filter Bar
st.markdown("### 🔍 Search & Filter Filters")
c_f1, c_f2, c_f3, c_f4 = st.columns(4)

with c_f1:
    search_term = st.text_input("Search Customer / Payee / ID", placeholder="e.g. Ramesh or 1")
with c_f2:
    decision_filter = st.multiselect("Filter Decision", ["Normal", "Review Required", "Suspicious"], default=["Normal", "Review Required", "Suspicious"])
with c_f3:
    type_filter = st.multiselect("Transaction Type", sorted(df_txns["transaction_type"].unique()), default=sorted(df_txns["transaction_type"].unique()))
with c_f4:
    min_amt, max_amt = st.slider(
        "Amount Range (₹)",
        min_value=0.0,
        max_value=float(df_txns["amount"].max() if not df_txns.empty else 200000.0),
        value=(0.0, float(df_txns["amount"].max() if not df_txns.empty else 200000.0)),
        step=5000.0
    )

# Apply filters
filtered_df = df_txns.copy()
if search_term:
    s = search_term.lower()
    filtered_df = filtered_df[
        filtered_df["customer_name"].str.lower().str.contains(s) |
        filtered_df["payee_name"].str.lower().str.contains(s) |
        filtered_df["transaction_id"].astype(str).str.contains(s)
    ]
if decision_filter:
    filtered_df = filtered_df[filtered_df["decision"].isin(decision_filter)]
if type_filter:
    filtered_df = filtered_df[filtered_df["transaction_type"].isin(type_filter)]
filtered_df = filtered_df[(filtered_df["amount"] >= min_amt) & (filtered_df["amount"] <= max_amt)]

st.markdown(f"**Showing {len(filtered_df)} of {len(df_txns)} transactions:**")

# Format columns for display
display_table = filtered_df[[
    "transaction_id", "customer_name", "account_id", "payee_name",
    "amount", "transaction_type", "transaction_date", "z_score", "risk_score", "decision"
]].copy()

display_table["amount"] = display_table["amount"].apply(lambda x: f"₹{x:,.2f}")
display_table["z_score"] = display_table["z_score"].apply(lambda x: f"{x:.2f}")
display_table["risk_score"] = display_table["risk_score"].apply(lambda x: f"{x:.1f}")

st.dataframe(
    display_table,
    column_config={
        "transaction_id": "Tx ID",
        "customer_name": "Customer",
        "account_id": "Account ID",
        "payee_name": "Beneficiary",
        "amount": "Amount",
        "transaction_type": "Type",
        "transaction_date": "Timestamp",
        "z_score": "Z-Score",
        "risk_score": "Risk Score",
        "decision": "Screening Verdict"
    },
    use_container_width=True,
    hide_index=True
)

st.markdown("---")

# 2. DEEP AUDIT INSPECTION PANEL
st.markdown("### 🔬 In-Depth Transaction Audit Inspector")

txn_id_list = filtered_df["transaction_id"].tolist() if not filtered_df.empty else df_txns["transaction_id"].tolist()

if txn_id_list:
    selected_inspect_id = st.selectbox(
        "Select Transaction ID to Inspect Details:",
        options=txn_id_list,
        format_func=lambda tid: f"Txn #{tid} - {df_txns[df_txns['transaction_id'] == tid].iloc[0]['customer_name']} (₹{df_txns[df_txns['transaction_id'] == tid].iloc[0]['amount']:,.2f} - {df_txns[df_txns['transaction_id'] == tid].iloc[0]['decision']})"
    )

    t_row = df_txns[df_txns["transaction_id"] == selected_inspect_id].iloc[0]

    col_t1, col_t2, col_t3 = st.columns(3)

    with col_t1:
        st.markdown("#### 👤 Transaction Details")
        st.write(f"**Transaction ID:** #{t_row['transaction_id']}")
        st.write(f"**Customer:** {t_row['customer_name']} (Cust #{t_row['customer_id']})")
        st.write(f"**Account:** #{t_row['account_id']} ({t_row['account_type']})")
        st.write(f"**Beneficiary / Payee:** {t_row['payee_name']}")
        st.write(f"**Amount:** **₹{t_row['amount']:,.2f}**")
        st.write(f"**Type / Channel:** {t_row['transaction_type']} ({t_row['location']})")
        st.write(f"**Date:** {t_row['transaction_date']}")

    with col_t2:
        st.markdown("#### 🧮 Multi-Signal Scores")
        st.write(f"**Statistical Z-Score:** `{t_row['z_score']:.2f}`")
        st.write(f"**Rule Risk Score:** `{t_row['rule_score']:.1f} / 100`")
        st.write(f"**Graph Risk Score:** `{t_row['graph_score']:.1f} / 100`")
        st.write(f"**Composite Risk Score:** `{t_row['risk_score']:.1f} / 100`")
        
        dec = t_row["decision"]
        if dec == "Normal":
            st.success(f"Classification: **{dec}**")
        elif dec == "Review Required":
            st.warning(f"Classification: **{dec}**")
        else:
            st.error(f"Classification: **{dec}**")

    with col_t3:
        st.markdown("#### 📋 Explainability Audit")
        reasons_list = [r.strip() for r in str(t_row['reasons']).replace(";", "\n").split("\n") if r.strip()]
        for r in reasons_list:
            st.markdown(f"- {r}")

        st.markdown("""
        <div style='font-size:0.75rem; color:#64748B; margin-top:1rem; border-top:1px solid #E2E8F0; padding-top:6px;'>
            *Academic Note: First-level surveillance indicators are preserved for regulatory compliance review.*
        </div>
        """, unsafe_allow_html=True)
