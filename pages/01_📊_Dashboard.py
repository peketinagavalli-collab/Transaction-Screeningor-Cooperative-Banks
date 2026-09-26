"""
Main Dashboard Page (Executive Overview & Statistical Visualization).
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from database.db_connection import DatabaseManager

st.set_page_config(page_title="Dashboard | Coop Bank AI", page_icon="📊", layout="wide")

# Academic Header
st.markdown("""
<div style='background: linear-gradient(135deg, #1E3A8A 0%, #0F172A 100%); padding: 1.5rem 2rem; border-radius: 10px; color: white; margin-bottom: 1.2rem;'>
    <h1 style='color: white; margin: 0; font-size: 1.8rem; font-weight: 800;'>📊 Transaction Screening Dashboard</h1>
    <p style='color: #93C5FD; margin: 0.3rem 0 0 0; font-size: 0.95rem;'>First-Level Surveillance & Quantitative Overview for Cooperative Bank Operations</p>
</div>
""", unsafe_allow_html=True)

# Academic Disclaimer Banner
st.markdown("""
<div style='background-color: #FEF3C7; border-left: 4px solid #F59E0B; padding: 0.7rem 1rem; border-radius: 6px; color: #92400E; font-size: 0.85rem; margin-bottom: 1.2rem;'>
    ⚠️ <b>Academic Disclaimer:</b> This dashboard displays prototype screening classifications based on propositional logic, statistical deviations, and network topology. It does not definitively identify fraud.
</div>
""", unsafe_allow_html=True)

# Fetch Aggregated Data
try:
    df_metrics = DatabaseManager.execute_query("""
        SELECT 
            COUNT(*) AS total_count,
            COALESCE(SUM(amount), 0) AS total_amount,
            COALESCE(AVG(amount), 0) AS avg_amount,
            COALESCE(MAX(amount), 0) AS max_amount
        FROM "TRANSACTION"
    """)

    df_decisions = DatabaseManager.execute_query("""
        SELECT 
            decision, 
            COUNT(*) AS count,
            COALESCE(SUM(t.amount), 0) AS total_val,
            COALESCE(AVG(sr.risk_score), 0) AS avg_risk
        FROM SCREENING_RESULT sr
        JOIN "TRANSACTION" t ON sr.transaction_id = t.transaction_id
        GROUP BY decision
    """)

    df_recent = DatabaseManager.execute_query("""
        SELECT 
            t.transaction_id,
            c.customer_name,
            t.account_id,
            COALESCE(p.payee_name, 'Self / ATM') AS payee_name,
            t.amount,
            t.transaction_type,
            t.transaction_date,
            sr.z_score,
            sr.risk_score,
            sr.decision,
            sr.reasons
        FROM "TRANSACTION" t
        JOIN ACCOUNT a ON t.account_id = a.account_id
        JOIN CUSTOMER c ON a.customer_id = c.customer_id
        LEFT JOIN PAYEE p ON t.payee_id = p.payee_id
        JOIN SCREENING_RESULT sr ON t.transaction_id = sr.transaction_id
        ORDER BY t.transaction_date DESC, t.transaction_id DESC
    """)

except Exception as e:
    st.error(f"Error fetching dashboard data: {e}")
    st.stop()

# 1. KPI CARDS
dec_map = dict(zip(df_decisions["decision"], df_decisions["count"])) if not df_decisions.empty else {}
total_txns = int(df_metrics.iloc[0]["total_count"])
total_vol = float(df_metrics.iloc[0]["total_amount"])
avg_amt = float(df_metrics.iloc[0]["avg_amount"])

col1, col2, col3, col4, col5, col6 = st.columns(6)
with col1:
    st.metric("Total Transactions", f"{total_txns:,}", help="Total number of evaluated transactions")
with col2:
    st.metric("Normal", f"{dec_map.get('Normal', 0)}", delta="Safe", delta_color="normal")
with col3:
    st.metric("Review Required", f"{dec_map.get('Review Required', 0)}", delta="Medium Alert", delta_color="off")
with col4:
    st.metric("Suspicious", f"{dec_map.get('Suspicious', 0)}", delta="High Priority", delta_color="inverse")
with col5:
    st.metric("Total Amount Screened", f"₹{total_vol:,.0f}")
with col6:
    st.metric("Average Transaction", f"₹{avg_amt:,.0f}")

st.markdown("---")

# 2. CHARTS ROW
c_chart1, c_chart2 = st.columns([1, 1])

with c_chart1:
    st.markdown("#### 🎯 Decision Distribution")
    if not df_decisions.empty:
        color_map = {
            "Normal": "#10B981",
            "Review Required": "#F59E0B",
            "Suspicious": "#EF4444"
        }
        fig_pie = px.pie(
            df_decisions,
            values="count",
            names="decision",
            color="decision",
            color_discrete_map=color_map,
            hole=0.45
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        fig_pie.update_layout(margin=dict(t=20, b=20, l=20, r=20), height=320)
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.info("No decision records found.")

with c_chart2:
    st.markdown("#### 📈 Transaction Volume by Type")
    if not df_recent.empty:
        df_type = df_recent.groupby("transaction_type")["amount"].agg(["sum", "count"]).reset_index()
        fig_bar = px.bar(
            df_type,
            x="transaction_type",
            y="sum",
            color="transaction_type",
            text="count",
            labels={"sum": "Total Volume (₹)", "transaction_type": "Type", "count": "Tx Count"},
            color_discrete_sequence=px.colors.qualitative.Prism
        )
        fig_bar.update_layout(margin=dict(t=20, b=20, l=20, r=20), height=320, showlegend=False)
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("No transaction data available.")

# 3. STATISTICAL Z-SCORE DISTRIBUTION
st.markdown("---")
c_stat1, c_stat2 = st.columns([1, 1])

with c_stat1:
    st.markdown("#### 📊 Statistical Z-Score Distribution (Python Gaussian Anomaly)")
    if not df_recent.empty:
        fig_hist = px.histogram(
            df_recent,
            x="z_score",
            color="decision",
            nbins=15,
            color_discrete_map={"Normal": "#10B981", "Review Required": "#F59E0B", "Suspicious": "#EF4444"},
            labels={"z_score": "Z-Score (Standard Deviations from Mean)", "count": "Frequency"}
        )
        # Add threshold indicator line
        fig_hist.add_vline(x=3.0, line_dash="dash", line_color="#DC2626", annotation_text="|z| = 3.0 Threshold")
        fig_hist.update_layout(margin=dict(t=20, b=20, l=20, r=20), height=300)
        st.plotly_chart(fig_hist, use_container_width=True)
    else:
        st.info("No statistical records available.")

with c_stat2:
    st.markdown("#### ⚖️ Multi-Signal Risk Score Distribution")
    if not df_recent.empty:
        fig_risk = px.box(
            df_recent,
            x="decision",
            y="risk_score",
            color="decision",
            color_discrete_map={"Normal": "#10B981", "Review Required": "#F59E0B", "Suspicious": "#EF4444"},
            labels={"risk_score": "Composite Risk Score (0 - 100)", "decision": "Decision"}
        )
        fig_risk.update_layout(margin=dict(t=20, b=20, l=20, r=20), height=300, showlegend=False)
        st.plotly_chart(fig_risk, use_container_width=True)

# 4. RECENT PRIORITY ALERTS TABLE
st.markdown("---")
st.markdown("### 🚨 Recent High-Priority & Review-Required Transactions")

df_alerts = df_recent[df_recent["decision"].isin(["Suspicious", "Review Required"])]

if not df_alerts.empty:
    display_df = df_alerts[[
        "transaction_id", "customer_name", "account_id", "payee_name", 
        "amount", "transaction_type", "z_score", "risk_score", "decision", "reasons"
    ]].copy()
    
    display_df["amount"] = display_df["amount"].apply(lambda x: f"₹{x:,.2f}")
    display_df["z_score"] = display_df["z_score"].apply(lambda x: f"{x:.2f}")
    display_df["risk_score"] = display_df["risk_score"].apply(lambda x: f"{x:.1f}/100")
    
    st.dataframe(
        display_df,
        column_config={
            "transaction_id": "Tx ID",
            "customer_name": "Customer",
            "account_id": "Account",
            "payee_name": "Beneficiary",
            "amount": "Amount (INR)",
            "transaction_type": "Type",
            "z_score": "Z-Score",
            "risk_score": "Risk Score",
            "decision": st.column_config.TextColumn(
                "Screening Verdict",
                help="Academic Classification"
            ),
            "reasons": "Explainability Reasons"
        },
        use_container_width=True,
        hide_index=True
    )
else:
    st.success("✅ No suspicious or review-required transactions found in the database.")
