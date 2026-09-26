"""
Transaction Screening Page (Interactive Real-Time Pipeline).
Evaluates transactions through DMGT Propositional Logic, Statistical Anomaly Detection, and NetworkX Graph Analytics.
"""

import streamlit as st
import datetime
import plotly.graph_objects as go
from database.db_connection import DatabaseManager
from services.screening_service import TransactionScreeningSystem

st.set_page_config(page_title="Screen Transaction | Coop Bank AI", page_icon="🔍", layout="wide")

# Academic Header
st.markdown("""
<div style='background: linear-gradient(135deg, #1E3A8A 0%, #0F172A 100%); padding: 1.5rem 2rem; border-radius: 10px; color: white; margin-bottom: 1.2rem;'>
    <h1 style='color: white; margin: 0; font-size: 1.8rem; font-weight: 800;'>🔍 Live Transaction Screening Engine</h1>
    <p style='color: #93C5FD; margin: 0.3rem 0 0 0; font-size: 0.95rem;'>Interactive 11-Step First-Level Screening Pipeline with Multi-Modal Explainability</p>
</div>
""", unsafe_allow_html=True)

# Academic Disclaimer Banner
st.markdown("""
<div style='background-color: #FEF3C7; border-left: 4px solid #F59E0B; padding: 0.7rem 1rem; border-radius: 6px; color: #92400E; font-size: 0.85rem; margin-bottom: 1.2rem;'>
    ⚠️ <b>Academic Disclaimer:</b> This screening engine produces indicative risk scores ('Normal', 'Review Required', 'Suspicious') for academic evaluation. It does not determine legal fraud.
</div>
""", unsafe_allow_html=True)

# Fetch Accounts and Payees from Database for Form Inputs
try:
    df_accounts = DatabaseManager.execute_query("""
        SELECT a.account_id, a.account_type, a.balance, c.customer_name, c.customer_id
        FROM ACCOUNT a
        JOIN CUSTOMER c ON a.customer_id = c.customer_id
        WHERE a.account_status = 'Active'
        ORDER BY a.account_id ASC
    """)

    df_payees = DatabaseManager.execute_query("""
        SELECT payee_id, payee_name, bank_name, account_number
        FROM PAYEE
        ORDER BY payee_id ASC
    """)
except Exception as e:
    st.error(f"Error loading reference data from database: {e}")
    st.stop()

# Initialize or retrieve screening system from session state
if "screening_system" not in st.session_state:
    st.session_state.screening_system = TransactionScreeningSystem()
screener: TransactionScreeningSystem = st.session_state.screening_system

# Two-column layout: Left = Input Form, Right = Screening Result & Explainability
col_form, col_result = st.columns([1, 1.1])

with col_form:
    st.markdown("### 📝 Enter Transaction Details")
    
    with st.form(key="screening_form"):
        # 1. Source Account Dropdown
        acc_options = {
            f"Acc #{row['account_id']} - {row['customer_name']} ({row['account_type']}, Bal: ₹{row['balance']:,.2f})": row['account_id']
            for _, row in df_accounts.iterrows()
        }
        selected_acc_label = st.selectbox("1. Select Source Account (Member)", options=list(acc_options.keys()))
        selected_account_id = acc_options[selected_acc_label]

        # 2. Transaction Amount
        col_amt, col_type = st.columns(2)
        with col_amt:
            amount_input = st.number_input(
                "2. Amount (INR ₹)",
                min_value=100.0,
                max_value=10000000.0,
                value=75000.0,
                step=5000.0,
                help="Transfer or withdrawal amount in Indian Rupees."
            )
        with col_type:
            txn_type_input = st.selectbox(
                "3. Transaction Type",
                options=["Transfer", "RTGS", "NEFT", "UPI", "Withdrawal", "Deposit"],
                index=0
            )

        # 3. Payee / Beneficiary
        payee_options = {"None (Self / Cash / ATM Withdrawal)": None}
        for _, row in df_payees.iterrows():
            payee_options[f"Payee #{row['payee_id']} - {row['payee_name']} ({row['bank_name']})"] = row['payee_id']

        selected_payee_label = st.selectbox("4. Select Beneficiary / Payee", options=list(payee_options.keys()), index=1)
        selected_payee_id = payee_options[selected_payee_label]

        # 4. Location & Timestamp
        col_loc, col_date = st.columns(2)
        with col_loc:
            location_input = st.selectbox(
                "5. Branch / Channel",
                options=["Main Branch", "Rural Taluka Branch A", "Rural Taluka Branch B", "NetBanking Portal", "Mobile Banking UPI", "ATM Counter"]
            )
        with col_date:
            date_input = st.date_input("6. Date", value=datetime.date.today())

        st.markdown("---")
        screen_button = st.form_submit_button("🚀 SCREEN TRANSACTION", use_container_width=True, type="primary")

with col_result:
    st.markdown("### 📊 Screening Pipeline Output")

    if screen_button:
        with st.spinner("Executing 11-step academic screening pipeline..."):
            result = screener.screen_transaction(
                account_id=selected_account_id,
                amount=amount_input,
                payee_id=selected_payee_id,
                transaction_type=txn_type_input,
                location=location_input,
                save_to_db=True
            )

        # Store latest result in session state for cross-inspection
        st.session_state.latest_screening_result = result

        # Display Pipeline Execution Progress
        st.success(f"✅ Transaction #{result['transaction_id']} processed and saved to database!")

        # Prominent Decision Badge & Risk Meter
        decision = result["decision"]
        risk_score = result["risk_score"]

        if decision == "Normal":
            badge_color = "#10B981"
            badge_bg = "#D1FAE5"
            badge_icon = "🟢"
        elif decision == "Review Required":
            badge_color = "#D97706"
            badge_bg = "#FEF3C7"
            badge_icon = "🟡"
        else:
            badge_color = "#DC2626"
            badge_bg = "#FEE2E2"
            badge_icon = "🔴"

        # Verdict Banner
        st.markdown(f"""
        <div style='background-color: {badge_bg}; border: 2px solid {badge_color}; padding: 1.2rem; border-radius: 10px; margin-bottom: 1rem; text-align: center;'>
            <div style='font-size: 0.85rem; font-weight: 700; color: {badge_color}; text-transform: uppercase;'>Screening Classification</div>
            <div style='font-size: 2rem; font-weight: 900; color: {badge_color}; margin: 0.2rem 0;'>{badge_icon} {decision.upper()}</div>
            <div style='font-size: 0.95rem; font-weight: 600; color: #374151;'>Composite Risk Score: <b>{risk_score:.1f} / 100</b></div>
        </div>
        """, unsafe_allow_html=True)

        # Plotly Risk Score Gauge
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=risk_score,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Multi-Signal Risk Score", 'font': {'size': 14}},
            gauge={
                'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
                'bar': {'color': badge_color},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "gray",
                'steps': [
                    {'range': [0, screener.decision_bands['normal_max']], 'color': '#ECFDF5'},
                    {'range': [screener.decision_bands['normal_max'], screener.decision_bands['review_max']], 'color': '#FFFBEB'},
                    {'range': [screener.decision_bands['review_max'], 100], 'color': '#FEF2F2'}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': screener.decision_bands['review_max']
                }
            }
        ))
        fig_gauge.update_layout(height=200, margin=dict(t=25, b=10, l=25, r=25))
        st.plotly_chart(fig_gauge, use_container_width=True)

        # Explainability Tabs
        tab_reasons, tab_logic, tab_stats, tab_graph = st.tabs([
            "📋 Reasons & Verdict",
            "📐 DMGT Logic",
            "🧮 Statistical Math",
            "🕸️ ADSA Graph"
        ])

        with tab_reasons:
            st.markdown("#### 🎯 Explainability Audit Trail")
            for reason in result["reasons_list"]:
                st.markdown(f"- {reason}")
            
            st.markdown("---")
            st.markdown("##### ⚖️ Weight Breakdown")
            w = result["weights_used"]
            st.write(f"- **Rule Weight ($w_1$):** {w['w1']*100:.0f}% (Score: {result['rule_score']:.1f})")
            st.write(f"- **Statistical Weight ($w_2$):** {w['w2']*100:.0f}% (Score: {result['statistical_details']['statistical_risk']:.1f})")
            st.write(f"- **Graph Weight ($w_3$):** {w['w3']*100:.0f}% (Score: {result['graph_score']:.1f})")
            st.write(f"- **Pattern Weight ($w_4$):** {w['w4']*100:.0f}% (Score: {result['pattern_risk']:.1f})")

        with tab_logic:
            st.markdown("#### 📐 DMGT Propositional Logic Evaluation")
            props = result["propositions"]
            
            p_col1, p_col2 = st.columns(2)
            with p_col1:
                st.write(f"**A** (Amount $\\ge$ ₹{screener.amount_threshold:,.0f}): `{'TRUE' if props['A'] else 'FALSE'}`")
                st.write(f"**N** (New Payee): `{'TRUE' if props['N'] else 'FALSE'}`")
            with p_col2:
                st.write(f"**Z** (|z| $\\ge$ {screener.z_threshold:.1f}): `{'TRUE' if props['Z'] else 'FALSE'}`")
                st.write(f"**G** (Graph Risk $\\ge$ {screener.graph_threshold:.1f}): `{'TRUE' if props['G'] else 'FALSE'}`")

            st.markdown("##### 📜 Triggered Compound Rules:")
            if result["triggered_rules"]:
                for r_id in result["triggered_rules"]:
                    st.info(f"Triggered: **{r_id}**", icon="⚡")
            else:
                st.write("No compound propositional logic rules triggered.")

        with tab_stats:
            st.markdown("#### 🧮 Statistical Z-Score Calculation")
            step = result["statistical_details"]["step_by_step"]
            st.latex(step["formula_mean"])
            st.latex(step["calc_mean_str"])
            st.latex(step["formula_std"])
            st.latex(step["calc_std_str"])
            st.latex(step["formula_z"])
            st.latex(step["calc_z_str"])
            st.latex(step["decision_str"])

        with tab_graph:
            st.markdown("#### 🕸️ NetworkX Graph Context")
            g_det = result["graph_details"]
            st.write(f"- **Is Novel Edge (New Connection):** `{'YES' if g_det['is_new_connection'] else 'NO'}`")
            st.write(f"- **Source Node Degree:** {g_det['source_degree']}")
            st.write(f"- **Destination Node Degree:** {g_det['dest_degree']}")
            st.write(f"- **Graph Risk Indicator:** {g_det['graph_risk_indicator']:.2f}")

    else:
        st.info("👈 Fill out the transaction parameters on the left and click **SCREEN TRANSACTION** to execute the pipeline.", icon="💡")
