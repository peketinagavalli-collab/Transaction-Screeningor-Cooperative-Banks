"""
Admin & Prototype Configuration Page.
Allows calibrating mathematical thresholds, weights, decision bands, and database state.
"""

import streamlit as st
from database.init_db import init_database
from services.screening_service import TransactionScreeningSystem

st.set_page_config(page_title="Admin Settings | Coop Bank AI", page_icon="⚙️", layout="wide")

# Academic Header
st.markdown("""
<div style='background: linear-gradient(135deg, #1E3A8A 0%, #0F172A 100%); padding: 1.5rem 2rem; border-radius: 10px; color: white; margin-bottom: 1.2rem;'>
    <h1 style='color: white; margin: 0; font-size: 1.8rem; font-weight: 800;'>⚙️ System Settings & Prototype Parameters</h1>
    <p style='color: #93C5FD; margin: 0.3rem 0 0 0; font-size: 0.95rem;'>Configure Academic Thresholds, Risk Weights, Decision Bands & Database State</p>
</div>
""", unsafe_allow_html=True)

if "screening_system" not in st.session_state:
    st.session_state.screening_system = TransactionScreeningSystem()

sys_instance: TransactionScreeningSystem = st.session_state.screening_system

# Configuration Form
with st.form("settings_form"):
    st.markdown("### 🎛️ 1. Detection Thresholds")
    c_th1, c_th2 = st.columns(2)
    
    with c_th1:
        new_amt_threshold = st.number_input(
            "General Transaction Amount Threshold (₹)",
            min_value=1000.0,
            max_value=500000.0,
            value=float(sys_instance.amount_threshold),
            step=5000.0,
            help="Threshold for Proposition A (Amount exceeds threshold)."
        )
        new_z_threshold = st.number_input(
            "Statistical Z-Score Anomaly Threshold (|z|)",
            min_value=1.0,
            max_value=10.0,
            value=float(sys_instance.z_threshold),
            step=0.5,
            help="Threshold for Proposition Z (|z| >= threshold indicates statistical anomaly)."
        )
    
    with c_th2:
        new_large_with_threshold = st.number_input(
            "Large Cash Withdrawal 2FA Threshold (₹)",
            min_value=5000.0,
            max_value=500000.0,
            value=float(sys_instance.large_withdrawal_threshold),
            step=5000.0,
            help="Threshold above which cash withdrawals mandate simulated OTP verification (Section 19)."
        )
        new_graph_threshold = st.number_input(
            "Graph Network Risk Indicator Threshold",
            min_value=0.1,
            max_value=1.0,
            value=float(sys_instance.graph_threshold),
            step=0.05,
            help="Threshold for Proposition G (Graph risk indicator >= threshold)."
        )

    st.markdown("---")
    st.markdown("### ⚖️ 2. Multi-Signal Risk Score Weights (Convex Combination)")
    st.caption("Demonstration weights combining individual risk signals into the composite 0-100 risk score.")

    w_c1, w_c2, w_c3, w_c4 = st.columns(4)
    with w_c1:
        w_rule = st.slider("Rule Risk Weight (w1)", 0.0, 1.0, float(sys_instance.weights.get("w1_rule", 0.30)), 0.05)
    with w_c2:
        w_stat = st.slider("Statistical Weight (w2)", 0.0, 1.0, float(sys_instance.weights.get("w2_statistical", 0.30)), 0.05)
    with w_c3:
        w_graph = st.slider("Graph Weight (w3)", 0.0, 1.0, float(sys_instance.weights.get("w3_graph", 0.20)), 0.05)
    with w_c4:
        w_pattern = st.slider("Pattern Weight (w4)", 0.0, 1.0, float(sys_instance.weights.get("w4_pattern", 0.20)), 0.05)

    sum_weights = w_rule + w_stat + w_graph + w_pattern
    if abs(sum_weights - 1.0) > 0.01:
        st.warning(f"⚠️ Current weight sum: {sum_weights:.2f}. For rigorous mathematical convex combination, sum should be 1.00.")

    st.markdown("---")
    st.markdown("### 🎯 3. Prototype Decision Bands")
    b_c1, b_c2 = st.columns(2)
    with b_c1:
        band_norm = st.slider("Normal Max Boundary (Score 0 to X)", 10.0, 50.0, float(sys_instance.decision_bands.get("normal_max", 39.0)), 1.0)
    with b_c2:
        band_rev = st.slider("Review Required Max Boundary (Score X to Y)", 50.0, 90.0, float(sys_instance.decision_bands.get("review_max", 69.0)), 1.0)

    st.markdown(f"**Current Bands:** 🟢 Normal: `0 - {band_norm:.0f}` | 🟡 Review Required: `{band_norm+1:.0f} - {band_rev:.0f}` | 🔴 Suspicious: `{band_rev+1:.0f} - 100`")

    st.markdown("---")
    save_settings = st.form_submit_button("💾 SAVE SETTINGS & RECONFIGURE ENGINES", type="primary", use_container_width=True)

if save_settings:
    st.session_state.screening_system = TransactionScreeningSystem(
        amount_threshold=new_amt_threshold,
        z_threshold=new_z_threshold,
        large_withdrawal_threshold=new_large_with_threshold,
        graph_threshold=new_graph_threshold,
        weights={"w1_rule": w_rule, "w2_statistical": w_stat, "w3_graph": w_graph, "w4_pattern": w_pattern},
        decision_bands={"normal_max": band_norm, "review_max": band_rev}
    )
    st.success("✅ System thresholds and risk weights updated successfully!")

st.markdown("---")
st.markdown("### 🔄 Database Management & Sample Seeder")

c_db1, c_db2 = st.columns([1, 1])

with c_db1:
    st.markdown("#### 🔄 Reset & Re-Seed Database")
    st.markdown("Restores all tables to pristine initial state with realistic cooperative banking customers, member accounts, and academic test cases.")
    if st.button("♻️ RESET DATABASE & RE-SEED DEMO DATA", type="secondary", use_container_width=True):
        with st.spinner("Re-initializing database schema and seeding sample data..."):
            init_database(force_recreate=True)
            st.session_state.screening_system = TransactionScreeningSystem()
        st.success("✅ Database re-initialized and populated successfully!")

with c_db2:
    st.markdown("#### ⚙️ Reset Configurations to Defaults")
    st.markdown("Resets all thresholds, weights, and decision bands to standard academic defaults.")
    if st.button("🔄 RESTORE DEFAULT SETTINGS", use_container_width=True):
        st.session_state.screening_system = TransactionScreeningSystem()
        st.success("✅ Restored default thresholds and weights.")
        st.rerun()
