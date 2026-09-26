"""
Large Cash Withdrawal & Simulated OTP Verification Page (Section 19 Feature).
Compares cash withdrawals against individual customer baselines and executes simulated cryptographic 2FA verification.
"""

import streamlit as st
import pandas as pd
import datetime
from database.db_connection import DatabaseManager
from models.otp_verification import OTPVerification
from services.otp_service import OTPService

st.set_page_config(page_title="Large Withdrawal & OTP | Coop Bank AI", page_icon="💵", layout="wide")

# Academic Header
st.markdown("""
<div style='background: linear-gradient(135deg, #1E3A8A 0%, #0F172A 100%); padding: 1.5rem 2rem; border-radius: 10px; color: white; margin-bottom: 1.2rem;'>
    <h1 style='color: white; margin: 0; font-size: 1.8rem; font-weight: 800;'>💵 Large Cash Withdrawal & OTP Verification</h1>
    <p style='color: #93C5FD; margin: 0.3rem 0 0 0; font-size: 0.95rem;'>Customer Historical Baseline Comparison & Simulated Two-Factor Authentication Flow</p>
</div>
""", unsafe_allow_html=True)

# Academic Disclaimer Banner
st.markdown("""
<div style='background-color: #FEF3C7; border-left: 4px solid #F59E0B; padding: 0.7rem 1rem; border-radius: 6px; color: #92400E; font-size: 0.85rem; margin-bottom: 1.2rem;'>
    ⚠️ <b>Simulated Security Feature:</b> OTP verification in this project is a simulated academic security feature. It is not connected to a real telecom SMS gateway. OTP tokens are cryptographically hashed using SHA-256 in the database.
</div>
""", unsafe_allow_html=True)

# Fetch Customers and their Accounts
try:
    df_customers = DatabaseManager.execute_query("""
        SELECT c.customer_id, c.customer_name, c.phone, c.email, a.account_id, a.account_type, a.balance
        FROM CUSTOMER c
        JOIN ACCOUNT a ON c.customer_id = a.customer_id
        WHERE a.account_status = 'Active'
        ORDER BY c.customer_id ASC
    """)
except Exception as e:
    st.error(f"Error loading customers from database: {e}")
    st.stop()

# Initialize OTP Service from Session State settings
if "screening_system" in st.session_state:
    otp_threshold = st.session_state.screening_system.large_withdrawal_threshold
else:
    otp_threshold = 50000.0

otp_service = OTPService(large_withdrawal_threshold=otp_threshold)

# Session state tracking for current OTP verification workflow
if "active_otp_obj" not in st.session_state:
    st.session_state.active_otp_obj = None
if "plain_demo_otp" not in st.session_state:
    st.session_state.plain_demo_otp = None
if "withdrawal_analysis" not in st.session_state:
    st.session_state.withdrawal_analysis = None
if "otp_verification_status" not in st.session_state:
    st.session_state.otp_verification_status = None

# Step-by-Step Flow Guide
st.markdown("""
<div style='display: flex; justify-content: space-between; background: #F8FAFC; padding: 0.8rem 1.2rem; border-radius: 8px; border: 1px solid #E2E8F0; margin-bottom: 1.5rem; font-size: 0.82rem; font-weight: 600; color: #475569;'>
    <span>1️⃣ Request Withdrawal</span> ➔ 
    <span>2️⃣ Pattern Analysis</span> ➔ 
    <span>3️⃣ Large Amount Detection</span> ➔ 
    <span>4️⃣ OTP Simulation</span> ➔ 
    <span>5️⃣ Screening Verdict</span>
</div>
""", unsafe_allow_html=True)

col_input, col_sim = st.columns([1.1, 1.0])

with col_input:
    st.markdown("### 🏦 Step 1: Cash Withdrawal Request")
    
    # Customer Selector
    cust_options = {
        f"Cust #{row['customer_id']} - {row['customer_name']} (Acc #{row['account_id']} {row['account_type']}, Bal: ₹{row['balance']:,.2f})": (row['customer_id'], row['account_id'], row['customer_name'], row['phone'], row['balance'])
        for _, row in df_customers.iterrows()
    }
    selected_cust_label = st.selectbox("Select Customer / Account", options=list(cust_options.keys()))
    cust_id, acc_id, cust_name, cust_phone, cust_bal = cust_options[selected_cust_label]

    # Pre-display Customer's Historical Withdrawal Record
    hist_withdrawals = otp_service.get_customer_withdrawal_history(cust_id)
    with st.expander("📜 View Customer's Past Cash Withdrawal History", expanded=True):
        if hist_withdrawals:
            st.write(f"**Recorded Historical Cash Withdrawals:** {', '.join([f'₹{w:,.0f}' for w in hist_withdrawals])}")
            avg_hist = sum(hist_withdrawals) / len(hist_withdrawals)
            st.write(f"**Historical Average Withdrawal (μ):** ₹{avg_hist:,.2f} (from {len(hist_withdrawals)} transactions)")
        else:
            st.info("No prior cash withdrawals recorded for this customer. Standard baseline will be applied.")

    # Withdrawal Amount Input
    withdrawal_amt = st.number_input(
        "Enter Requested Cash Withdrawal Amount (INR ₹)",
        min_value=500.0,
        max_value=1000000.0,
        value=100000.0,
        step=5000.0,
        help="Try ₹1,00,000 for Ramesh (normal is ₹5,000-₹10,000) to trigger large withdrawal + OTP verification."
    )

    location_choice = st.selectbox("Withdrawal Location / Channel", ["Taluka Branch Counter", "Main Branch Counter", "ATM Counter"])

    if st.button("🔎 ANALYZE & PROCESS WITHDRAWAL", type="primary", use_container_width=True):
        # Run withdrawal analysis
        analysis = otp_service.analyze_withdrawal_request(cust_id, withdrawal_amt)
        st.session_state.withdrawal_analysis = analysis
        st.session_state.otp_verification_status = None

        if analysis["is_otp_required"]:
            # Generate simulated OTP
            otp_obj, plain_code = otp_service.generate_and_save_otp(cust_id, cust_phone)
            st.session_state.active_otp_obj = otp_obj
            st.session_state.plain_demo_otp = plain_code
        else:
            st.session_state.active_otp_obj = None
            st.session_state.plain_demo_otp = None

with col_sim:
    st.markdown("### 📱 Step 2: Pattern Analysis & OTP Flow")

    if st.session_state.withdrawal_analysis is not None:
        ana = st.session_state.withdrawal_analysis
        is_large = ana["is_large_withdrawal"]
        is_unusual = ana["is_unusual_pattern"]
        otp_req = ana["is_otp_required"]
        z_val = ana["customer_z_score"]

        # Status Alert Card
        if is_large and is_unusual:
            st.error("🚨 **UNUSUAL LARGE CASH WITHDRAWAL DETECTED!**")
        elif is_large:
            st.warning("⚠️ **LARGE CASH WITHDRAWAL DETECTED** (Exceeds ₹50,000 threshold)")
        elif is_unusual:
            st.warning("⚠️ **UNUSUAL WITHDRAWAL PATTERN DETECTED** (High statistical Z-score)")
        else:
            st.success("✅ **NORMAL CASH WITHDRAWAL** (Within routine member limits)")

        # Metrics Card
        m_c1, m_c2, m_c3 = st.columns(3)
        with m_c1:
            st.metric("Requested Amount", f"₹{ana['current_amount']:,.0f}")
        with m_c2:
            st.metric("Historical Average", f"₹{ana['historical_mean']:,.0f}")
        with m_c3:
            st.metric("Personal Z-Score", f"{z_val:.2f}", delta="High Anomaly" if is_unusual else "Normal")

        st.markdown(f"""
        - **Large Withdrawal ($\\ge$ ₹{ana['large_withdrawal_threshold']:,.0f}):** `{'TRUE' if is_large else 'FALSE'}`
        - **Unusual Personal Pattern (|z| $\\ge$ {ana['customer_z_threshold']:.1f}):** `{'TRUE' if is_unusual else 'FALSE'}`
        - **OTP Verification Required:** `{'TRUE' if otp_req else 'FALSE'}`
        - **Classification:** **{ana['classification']}**
        """)

        # OTP Virtual Mobile Phone Simulation Box
        if otp_req and st.session_state.active_otp_obj is not None:
            st.markdown("---")
            st.markdown("#### 📲 Simulated Mobile Phone SMS Notification")
            
            # Mask phone
            masked_p = cust_phone[:2] + "******" + cust_phone[-2:] if len(cust_phone) >= 4 else cust_phone
            plain_token = st.session_state.plain_demo_otp

            st.markdown(f"""
            <div style='background: #1E293B; border-radius: 14px; padding: 1.2rem; color: white; border: 2px solid #3B82F6; box-shadow: 0 4px 15px rgba(0,0,0,0.2);'>
                <div style='font-size: 0.75rem; color: #94A3B8; text-align: center; margin-bottom: 0.5rem;'>📱 SIMULATED SMS • REGISTERED NUMBER {masked_p}</div>
                <div style='background: #334155; padding: 0.9rem; border-radius: 8px; border-left: 4px solid #10B981;'>
                    <div style='font-weight: 700; color: #F8FAFC; font-size: 0.9rem;'>Cooperative Bank Alert:</div>
                    <div style='font-size: 0.85rem; color: #CBD5E1; margin: 0.3rem 0;'>
                        Your OTP for high-value cash withdrawal of <b>₹{ana['current_amount']:,.2f}</b> is:
                    </div>
                    <div style='font-size: 1.6rem; font-weight: 900; letter-spacing: 4px; color: #38BDF8; text-align: center; margin: 0.4rem 0;'>
                        {plain_token}
                    </div>
                    <div style='font-size: 0.72rem; color: #94A3B8; text-align: center;'>Valid for 5 minutes. Do not share this OTP with anyone.</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # OTP Verification Input Box
            st.markdown("##### 🔐 Enter OTP to Authorize:")
            c_otp_in, c_otp_btn = st.columns([1.2, 1])
            with c_otp_in:
                user_entered_otp = st.text_input("Enter 6-digit OTP", max_chars=6, placeholder="e.g. 123456", key="otp_input_field")
            with c_otp_btn:
                st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
                verify_btn = st.button("✅ VERIFY OTP", type="primary", use_container_width=True)

            if verify_btn:
                otp_obj = st.session_state.active_otp_obj
                is_valid, v_msg = otp_service.verify_otp_token(otp_obj, user_entered_otp)
                st.session_state.otp_verification_status = (is_valid, v_msg)

            # Display OTP Verification Result
            if st.session_state.otp_verification_status is not None:
                is_valid, v_msg = st.session_state.otp_verification_status
                if is_valid:
                    st.success(f"✓ {v_msg}")
                    st.markdown("""
                    <div style='background: #ECFDF5; border: 1px solid #10B981; padding: 0.8rem; border-radius: 8px; color: #065F46; font-size: 0.85rem;'>
                        <b>✓ Identity Authenticated:</b> Customer passed simulated two-factor verification.
                    </div>
                    """, unsafe_allow_html=True)

                    # Screening Decision Verdict Note
                    st.markdown("---")
                    st.markdown("#### 📋 Final Screening & Audit Verdict")
                    rec_dec = ana["recommended_decision"]
                    if rec_dec == "Review Required":
                        st.warning("""
                        **Screening Classification:** 🟡 **REVIEW REQUIRED**  
                        **Reason:** Large withdrawal with abnormal deviation from customer's personal history ($z = {:.2f}$).  
                        *Note: While OTP verifies identity, the transaction remains marked for routine supervisory review due to historical divergence.*
                        """.format(z_val))
                    else:
                        st.success("""
                        **Screening Classification:** 🟢 **NORMAL**  
                        **Reason:** Customer withdrawal is within acceptable tolerance and authenticated successfully.
                        """)

                else:
                    st.error(f"❌ {v_msg}")
    else:
        st.info("👈 Select a customer, enter a withdrawal amount, and click **ANALYZE & PROCESS WITHDRAWAL**.", icon="💡")
