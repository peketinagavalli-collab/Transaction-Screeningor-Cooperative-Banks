"""
AI-Based Suspicious Transaction Screening System for Cooperative Banks.
Main Streamlit Application Entry Point.
"""

import streamlit as st
import os
import sys

# Ensure project root is in sys.path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from database.db_connection import DatabaseManager
from database.init_db import init_database
from services.screening_service import TransactionScreeningSystem

# Configure Streamlit page
st.set_page_config(
    page_title="Coop Bank AI Screening",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for rich aesthetics and clean academic presentation
st.markdown("""
<style>
    /* Global styling */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .main-header {
        background: linear-gradient(135deg, #1E3A8A 0%, #0F172A 100%);
        padding: 1.8rem 2.2rem;
        border-radius: 12px;
        color: #FFFFFF;
        margin-bottom: 1.8rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .main-header h1 {
        color: #FFFFFF !important;
        font-size: 1.9rem;
        font-weight: 800;
        margin-bottom: 0.3rem;
    }
    
    .main-header p {
        color: #93C5FD;
        font-size: 1.0rem;
        margin-bottom: 0;
    }
    
    .academic-disclaimer {
        background-color: #FEF3C7;
        border-left: 5px solid #F59E0B;
        padding: 0.9rem 1.2rem;
        border-radius: 6px;
        color: #92400E;
        font-size: 0.88rem;
        font-weight: 500;
        margin-bottom: 1.5rem;
    }
    
    .metric-card {
        background: #FFFFFF;
        border-radius: 10px;
        padding: 1.2rem 1.4rem;
        border: 1px solid #E2E8F0;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
        text-align: center;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(0, 0, 0, 0.08);
    }
    
    .badge-normal {
        background-color: #D1FAE5;
        color: #065F46;
        padding: 4px 12px;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.85rem;
        display: inline-block;
    }
    
    .badge-review {
        background-color: #FEF3C7;
        color: #92400E;
        padding: 4px 12px;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.85rem;
        display: inline-block;
    }
    
    .badge-suspicious {
        background-color: #FEE2E2;
        color: #991B1B;
        padding: 4px 12px;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.85rem;
        display: inline-block;
    }
    
    .formula-box {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 1.2rem;
        margin: 0.8rem 0;
    }
    
    .step-badge {
        background-color: #1E3A8A;
        color: #FFFFFF;
        border-radius: 50%;
        width: 26px;
        height: 26px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-size: 0.82rem;
        font-weight: 700;
        margin-right: 8px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Session State
if "screening_system" not in st.session_state:
    st.session_state.screening_system = TransactionScreeningSystem()

if "db_initialized" not in st.session_state:
    # Ensure database is bootstrapped
    try:
        df_check = DatabaseManager.execute_query("SELECT COUNT(*) AS c FROM CUSTOMER")
        if df_check.empty or df_check.iloc[0]["c"] == 0:
            init_database(force_recreate=True)
    except Exception:
        init_database(force_recreate=True)
    st.session_state.db_initialized = True

# Sidebar Navigation Header & System Status
st.sidebar.markdown("""
<div style='text-align: center; padding: 1rem 0;'>
    <div style='font-size: 2.2rem;'>🏦</div>
    <div style='font-weight: 800; font-size: 1.15rem; color: #1E3A8A;'>COOP BANK AI</div>
    <div style='font-size: 0.78rem; color: #64748B; font-weight: 600;'>TRANSACTION SCREENING SYSTEM</div>
    <div style='font-size: 0.72rem; color: #94A3B8; margin-top: 4px;'>Academic Prototype v1.0</div>
</div>
""", unsafe_allow_html=True)

# Database Status Indicator in Sidebar
db_status = DatabaseManager.test_connection()
if db_status["connected"]:
    st.sidebar.success(f"🟢 Database: **{db_status['engine']}** Connected", icon="🗄️")
else:
    st.sidebar.error("🔴 Database Disconnected", icon="⚠️")

# Academic Subject Tags in Sidebar
st.sidebar.markdown("---")
st.sidebar.markdown("<p style='font-size:0.8rem; font-weight:700; color:#475569;'>ACADEMIC SUBJECT MODULES</p>", unsafe_allow_html=True)
col_s1, col_s2 = st.sidebar.columns(2)
with col_s1:
    st.markdown("<span style='font-size:0.75rem; background:#EFF6FF; color:#1D4ED8; padding:3px 8px; border-radius:4px; font-weight:600;'>1. DBMS</span>", unsafe_allow_html=True)
    st.markdown("<span style='font-size:0.75rem; background:#F5F3FF; color:#6D28D9; padding:3px 8px; border-radius:4px; font-weight:600;'>3. ADSA</span>", unsafe_allow_html=True)
    st.markdown("<span style='font-size:0.75rem; background:#ECFDF5; color:#047857; padding:3px 8px; border-radius:4px; font-weight:600;'>5. Python</span>", unsafe_allow_html=True)
with col_s2:
    st.markdown("<span style='font-size:0.75rem; background:#FEF2F2; color:#B91C1C; padding:3px 8px; border-radius:4px; font-weight:600;'>2. DMGT</span>", unsafe_allow_html=True)
    st.markdown("<span style='font-size:0.75rem; background:#FFFBEB; color:#B45309; padding:3px 8px; border-radius:4px; font-weight:600;'>4. OOPJ</span>", unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.info(
    "💡 **Academic Prototype Note:**\n\n"
    "This system provides automated first-level screening using propositional logic, statistical Z-scores, "
    "and network graphs. Results do not assert definitive fraud.",
    icon="ℹ️"
)

# Landing / Overview page content when run directly
st.markdown("""
<div class='main-header'>
    <h1>AI-Based Suspicious Transaction Screening System</h1>
    <p>Automated First-Level Screening Prototype for Cooperative Credit Societies & Regional Banks</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class='academic-disclaimer'>
    ⚠️ <b>Academic Disclaimer:</b> This software is an academic prototype for first-level transaction screening. It does not determine whether a transaction is actually fraudulent. Decision classifications ('Normal', 'Review Required', 'Suspicious') indicate the level of recommended manual verification by bank officers.
</div>
""", unsafe_allow_html=True)

st.markdown("### 🎯 System Navigation & Overview")
st.markdown("Please select a module from the **left sidebar** to explore the system:")

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown("""
    #### 📊 Executive & Screener
    - **[01 📊 Dashboard](Dashboard)**: Macro transaction analytics, decision breakdown & risk distribution.
    - **[02 🔍 Screening](Screening)**: Real-time 11-step transaction screening pipeline with deep explainability.
    - **[03 💵 Large Withdrawal OTP](Large_Withdrawal_OTP)**: Customer-specific historical withdrawal anomaly detection & simulated 2FA OTP flow.
    - **[11 📝 Online Loan Application](Online_Loan_Application)**: Customer digital loan application with automated preliminary certificate screening & officer review.
    """)


with c2:
    c2.markdown("""
    #### 📐 Logic & Mathematical Models
    - **[04 📋 Transactions](Transactions)**: Searchable audit ledger with full parameter inspection.
    - **[05 🕸️ Transaction Network](Transaction_Network)**: ADSA NetworkX graph with vertex degrees & hub analysis.
    - **[06 🧮 Formulas Explanation](Formulas_Explanation)**: Step-by-step LaTeX formula derivations & live arithmetic calculator.
    """)

with c3:
    c3.markdown("""
    #### 🎓 Theory & Database Modules
    - **[07 📐 DMGT Logic & Relations](DMGT_Logic_Relations)**: Truth tables (A, N, Z, G) and binary relations ($R_1, R_2, R_3$).
    - **[08 🗄️ DBMS ER and SQL](DBMS_ER_and_SQL)**: Relational schemas, ER diagrams & interactive SQL query console.
    - **[09 🎓 Subject Mapping](Subject_Mapping)**: Academic syllabus alignment matrix for college demonstration.
    - **[10 ⚙️ Admin Settings](Admin_Settings)**: Configurable thresholds, weights, and database resets.
    """)

# Quick Summary Metrics
st.markdown("---")
st.markdown("### 📈 Live System Status")
try:
    df_txns = DatabaseManager.execute_query("""
        SELECT 
            COUNT(*) AS total_txns,
            SUM(amount) AS total_vol,
            AVG(amount) AS avg_amt
        FROM "TRANSACTION"
    """)
    df_decisions = DatabaseManager.execute_query("""
        SELECT decision, COUNT(*) AS count
        FROM SCREENING_RESULT
        GROUP BY decision
    """)
    dec_dict = dict(zip(df_decisions["decision"], df_decisions["count"])) if not df_decisions.empty else {}

    col_m1, col_m2, col_m3, col_m4, col_m5, col_m6 = st.columns(6)
    with col_m1:
        st.metric("Total Transactions", f"{df_txns.iloc[0]['total_txns']:,}")
    with col_m2:
        st.metric("Normal", f"{dec_dict.get('Normal', 0)}")
    with col_m3:
        st.metric("Review Required", f"{dec_dict.get('Review Required', 0)}")
    with col_m4:
        st.metric("Suspicious", f"{dec_dict.get('Suspicious', 0)}")
    with col_m5:
        st.metric("Total Volume", f"₹{df_txns.iloc[0]['total_vol']:,.0f}")
    with col_m6:
        st.metric("Average Transaction", f"₹{df_txns.iloc[0]['avg_amt']:,.0f}")
except Exception as ex:
    st.info(f"Database ready: {ex}")
