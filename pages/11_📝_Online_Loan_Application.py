"""
Online Loan Application & Certificate Verification Page.
Allows customers to submit online loan applications with automated 6-parameter preliminary certificate screening,
and provides bank officers with a manual review and decision workspace.
"""

import os
import io
import json
import datetime
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from database.db_connection import DatabaseManager
from database.init_db import init_database
from models.loan_application import LoanApplication
from models.loan_document import LoanDocument
from models.loan_review import LoanReview
from services.document_verification_service import DocumentVerificationService
from services.loan_service import LoanService

# Set page config
st.set_page_config(
    page_title="Online Loan Application | Coop Bank AI",
    page_icon="📝",
    layout="wide"
)

# Custom CSS for modern banking theme and verification styling
st.markdown("""
<style>
    .loan-header {
        background: linear-gradient(135deg, #1E3A8A 0%, #0F172A 100%);
        padding: 1.6rem 2.2rem;
        border-radius: 12px;
        color: #FFFFFF;
        margin-bottom: 1.2rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.12);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    .loan-header h1 {
        color: #FFFFFF !important;
        font-size: 1.85rem;
        font-weight: 800;
        margin-bottom: 0.3rem;
    }
    .loan-header p {
        color: #93C5FD;
        font-size: 0.95rem;
        margin-bottom: 0;
    }
    .academic-disclaimer {
        background-color: #FEF3C7;
        border-left: 5px solid #F59E0B;
        padding: 0.85rem 1.2rem;
        border-radius: 6px;
        color: #92400E;
        font-size: 0.88rem;
        font-weight: 500;
        margin-bottom: 1.4rem;
    }
    .score-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 1.2rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
        margin-bottom: 1rem;
    }
    .doc-pass-badge {
        background-color: #D1FAE5;
        color: #065F46;
        border: 1px solid #34D399;
        padding: 4px 12px;
        border-radius: 9999px;
        font-weight: 700;
        font-size: 0.85rem;
        display: inline-block;
    }
    .doc-review-badge {
        background-color: #FEF3C7;
        color: #92400E;
        border: 1px solid #FBBF24;
        padding: 4px 12px;
        border-radius: 9999px;
        font-weight: 700;
        font-size: 0.85rem;
        display: inline-block;
    }
    .doc-unable-badge {
        background-color: #FEE2E2;
        color: #991B1B;
        border: 1px solid #F87171;
        padding: 4px 12px;
        border-radius: 9999px;
        font-weight: 700;
        font-size: 0.85rem;
        display: inline-block;
    }
    .step-box {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    .summary-card {
        background: linear-gradient(135deg, #F8FAFC 0%, #EFF6FF 100%);
        border: 1px solid #BFDBFE;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1.2rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Services in Session State
if "doc_verifier" not in st.session_state:
    st.session_state.doc_verifier = DocumentVerificationService()

if "loan_service" not in st.session_state:
    st.session_state.loan_service = LoanService()

verifier: DocumentVerificationService = st.session_state.doc_verifier
loan_service: LoanService = st.session_state.loan_service

# Page Header
st.markdown("""
<div class='loan-header'>
    <h1>📝 Online Loan Application & Certificate Verification</h1>
    <p>Automated Document Screening, Multi-Parameter Consistency Analysis & Bank Officer Review Portal</p>
</div>
""", unsafe_allow_html=True)

# Academic Disclaimer Banner
st.markdown("""
<div class='academic-disclaimer'>
    ⚠️ <b>Academic Disclaimer:</b> This system provides preliminary automated screening of uploaded loan certificates and documents using multi-factor textual, QR, signature, and metadata analysis. It does <b>NOT</b> assert legal proof of authenticity. Final authenticity verification and credit decisions remain strictly with authorized bank officers.
</div>
""", unsafe_allow_html=True)

# Main Navigation Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "📝 Apply for Online Loan",
    "🔍 Track Application Status",
    "👨‍💼 Bank Officer Review Portal",
    "🧪 Test Scenarios & Demo Data"
])

# =============================================================================
# TAB 1: APPLY FOR ONLINE LOAN
# =============================================================================
with tab1:
    st.markdown("### 🏦 Digital Loan Application Form")
    st.caption("Complete the applicant details and attach supporting certificates. Our automated engine will conduct preliminary verification.")

    # Initialize form fields in session state if preset via Demo tab
    if "form_name" not in st.session_state:
        st.session_state.form_name = "Ramesh Kumar Sharma"
    if "form_mobile" not in st.session_state:
        st.session_state.form_mobile = "9876543210"
    if "form_email" not in st.session_state:
        st.session_state.form_email = "ramesh.sharma@coopbank.in"
    if "form_address" not in st.session_state:
        st.session_state.form_address = "Village Pipariya, Tehsil Hoshangabad, MP - 461001"
    if "form_dob" not in st.session_state:
        st.session_state.form_dob = datetime.date(1982, 5, 14)
    if "form_occupation" not in st.session_state:
        st.session_state.form_occupation = "Farmer / Agriculturalist"
    if "form_income" not in st.session_state:
        st.session_state.form_income = 45000.0
    if "form_loan_type" not in st.session_state:
        st.session_state.form_loan_type = "Agricultural Credit Loan"
    if "form_amount" not in st.session_state:
        st.session_state.form_amount = 250000.0
    if "form_purpose" not in st.session_state:
        st.session_state.form_purpose = "Purchase of high-yield wheat seeds, drip irrigation equipment, and organic fertilizer for Rabi harvest season."
    if "form_period" not in st.session_state:
        st.session_state.form_period = "36 Months"

    # Step Progress Indicator
    col_p1, col_p2, col_p3, col_p4 = st.columns(4)
    with col_p1:
        st.info("📌 **Step 1:** Applicant Details")
    with col_p2:
        st.info("💵 **Step 2:** Loan Requirements")
    with col_p3:
        st.info("📎 **Step 3:** Document Upload")
    with col_p4:
        st.info("🔍 **Step 4:** Screening & Submit")

    with st.expander("👤 1. Applicant Personal & Financial Profile", expanded=True):
        c1, c2 = st.columns(2)
        with c1:
            app_name = st.text_input("Applicant Full Name *", value=st.session_state.form_name, help="Must match full legal name on identity documents.")
            app_mobile = st.text_input("Mobile Number *", value=st.session_state.form_mobile, max_chars=15, help="10-digit mobile number for SMS OTP and verification.")
            app_email = st.text_input("Email Address *", value=st.session_state.form_email)
            app_dob = st.date_input("Date of Birth *", value=st.session_state.form_dob, min_value=datetime.date(1940, 1, 1), max_value=datetime.date(2010, 1, 1))

        with c2:
            app_address = st.text_area("Full Residential Address *", value=st.session_state.form_address, height=100)
            app_occupation = st.selectbox("Occupation / Primary Source of Income *", [
                "Farmer / Agriculturalist",
                "Dairy / Livestock Owner",
                "Small Business Owner / MSME",
                "Salaried Employee (Private Sector)",
                "Salaried Employee (Government / PSU)",
                "Rural Artisan / Handloom Weaver",
                "Self-Employed Professional",
                "Other"
            ], index=0)
            app_income = st.number_input("Monthly Income (₹) *", min_value=1000.0, max_value=10000000.0, value=float(st.session_state.form_income), step=5000.0)

    with st.expander("💰 2. Loan Requirements & Purpose", expanded=True):
        c_l1, c_l2 = st.columns(2)
        with c_l1:
            loan_type = st.selectbox("Loan Scheme / Type *", LoanApplication.ALLOWED_LOAN_TYPES, index=0)
            req_amount = st.number_input("Requested Loan Amount (₹) *", min_value=5000.0, max_value=10000000.0, value=float(st.session_state.form_amount), step=10000.0)
            repay_period = st.selectbox("Repayment Period *", [
                "12 Months (1 Year)",
                "24 Months (2 Years)",
                "36 Months (3 Years)",
                "48 Months (4 Years)",
                "60 Months (5 Years)",
                "84 Months (7 Years)",
                "120 Months (10 Years)"
            ], index=2)
        with c_l2:
            loan_purpose = st.text_area("Detailed Loan Purpose *", value=st.session_state.form_purpose, height=150)

    # 3. DOCUMENT UPLOADER SECTION
    st.markdown("---")
    st.markdown("### 📎 3. Certificate & Document Upload")
    st.caption("Upload supporting documents (PDF, JPG, JPEG, PNG | Maximum 10MB per file).")

    # Interactive upload slots
    col_u1, col_u2 = st.columns(2)
    
    with col_u1:
        doc_type_selected = st.selectbox("Select Document Category to Attach", LoanDocument.ALLOWED_DOC_TYPES, index=0)
        uploaded_file = st.file_uploader(
            f"Upload file for '{doc_type_selected}'",
            type=["pdf", "jpg", "jpeg", "png"],
            key="primary_file_uploader",
            help="Supported formats: PDF, JPG, JPEG, PNG. Clean legible scans recommended."
        )

    with col_u2:
        st.markdown("**⚡ Quick Pre-loaded Sample Files:**")
        st.caption("Use generated high-fidelity sample certificates for rapid demonstration.")
        sample_doc_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "sample_documents")
        
        c_btn1, c_btn2 = st.columns(2)
        with c_btn1:
            if st.button("🪪 Load Sample Aadhaar (QR Code)", use_container_width=True):
                sample_file = os.path.join(sample_doc_dir, "sample_aadhaar_ramesh.png")
                if os.path.exists(sample_file):
                    with open(sample_file, "rb") as f:
                        st.session_state.temp_uploaded_bytes = f.read()
                        st.session_state.temp_uploaded_name = "sample_aadhaar_ramesh.png"
                        st.session_state.temp_uploaded_type = "Aadhaar/Identity Proof"
                    st.success("Loaded 'sample_aadhaar_ramesh.png' with valid QR code payload!")
        with c_btn2:
            if st.button("🌾 Load Sample Income Cert (PDF)", use_container_width=True):
                sample_file = os.path.join(sample_doc_dir, "sample_income_certificate_ramesh.pdf")
                if os.path.exists(sample_file):
                    with open(sample_file, "rb") as f:
                        st.session_state.temp_uploaded_bytes = f.read()
                        st.session_state.temp_uploaded_name = "sample_income_certificate_ramesh.pdf"
                        st.session_state.temp_uploaded_type = "Income Certificate"
                    st.success("Loaded 'sample_income_certificate_ramesh.pdf' with digital seal!")

    # Store list of verified documents in session state for current application draft
    if "current_application_docs" not in st.session_state:
        st.session_state.current_application_docs = []

    # Handle Upload / Pre-load action
    active_bytes = None
    active_name = None
    active_category = doc_type_selected

    if uploaded_file is not None:
        active_bytes = uploaded_file.read()
        active_name = uploaded_file.name
        active_category = doc_type_selected
    elif "temp_uploaded_bytes" in st.session_state and st.session_state.temp_uploaded_bytes:
        active_bytes = st.session_state.temp_uploaded_bytes
        active_name = st.session_state.temp_uploaded_name
        active_category = st.session_state.temp_uploaded_type

    applicant_dict = {
        "applicant_name": app_name,
        "mobile": app_mobile,
        "email": app_email,
        "address": app_address,
        "dob": str(app_dob),
        "occupation": app_occupation,
        "income": app_income,
        "loan_type": loan_type,
        "requested_amount": req_amount,
        "loan_purpose": loan_purpose,
        "repayment_period": repay_period
    }

    st.markdown("---")
    c_act1, c_act2 = st.columns([1, 1])
    
    with c_act1:
        verify_btn = st.button("🔍 SCREEN & ATTACH THIS DOCUMENT", type="primary", use_container_width=True)

    with c_act2:
        if st.button("🗑️ Clear Attached Documents Draft", use_container_width=True):
            st.session_state.current_application_docs = []
            if "temp_uploaded_bytes" in st.session_state:
                del st.session_state.temp_uploaded_bytes
            st.info("Draft documents cleared.")
            st.rerun()

    if verify_btn:
        if not active_bytes or not active_name:
            st.warning("⚠️ Please choose or load a document file before screening.")
        else:
            with st.spinner(f"Executing automated preliminary screening on '{active_name}'..."):
                screening_res = verifier.verify_document(
                    file_bytes=active_bytes,
                    original_filename=active_name,
                    document_type=active_category,
                    applicant_info=applicant_dict
                )
                # Append to current session docs (replace if same category already exists)
                st.session_state.current_application_docs = [
                    d for d in st.session_state.current_application_docs 
                    if d.get("document_type") != active_category or d.get("file_name") != active_name
                ]
                st.session_state.current_application_docs.append(screening_res)
                st.success(f"✅ Document '{active_name}' screened successfully! Score: {screening_res['verification_score']}% ({screening_res['verification_status']})")

    # Display Current Attached Documents & Detailed Screening Cards
    if st.session_state.current_application_docs:
        st.markdown("### 📊 Automated Document Verification Results")
        st.caption("Detailed 6-factor academic scoring formula and entity match verification.")

        for idx, doc_res in enumerate(st.session_state.current_application_docs, start=1):
            v_status = doc_res.get("verification_status", "UNABLE TO VERIFY")
            v_score = doc_res.get("verification_score", 0.0)
            b_info = doc_res.get("verification_details", {}).get("formula_breakdown", {})
            
            # Status Badge Rendering
            if v_status == "PASS":
                status_html = "<span class='doc-pass-badge'>✅ PASS — Document passed automated screening</span>"
            elif v_status == "REVIEW REQUIRED":
                status_html = "<span class='doc-review-badge'>⚠️ REVIEW REQUIRED — Document requires manual verification</span>"
            else:
                status_html = "<span class='doc-unable-badge'>❓ UNABLE TO VERIFY — Unable to verify automatically</span>"

            with st.container():
                st.markdown(f"""
                <div class='score-card'>
                    <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.8rem;'>
                        <div>
                            <span style='font-size: 1.1rem; font-weight: 800; color: #1E3A8A;'>#{idx}. {doc_res['file_name']}</span>
                            <span style='font-size: 0.85rem; color: #64748B; margin-left: 10px;'>({doc_res['document_type']})</span>
                        </div>
                        <div>
                            {status_html}
                            <span style='font-size: 1.25rem; font-weight: 800; color: #1E3A8A; margin-left: 12px;'>{v_score:.1f}%</span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # 9 Required Fields Detailed Inspection Grid
                c_d1, c_d2, c_d3 = st.columns(3)
                with c_d1:
                    st.markdown(f"**Document Name:** `{doc_res['file_name']}`")
                    st.markdown(f"**Document Type:** `{doc_res['document_type']}`")
                    st.markdown(f"**File Validity:** `{'Valid & Readable (1.0)' if doc_res['file_validity_score'] >= 0.8 else 'Warning/Corrupt'}`")
                with c_d2:
                    st.markdown(f"**Text Extraction:** `{'Readable ASCII' if doc_res['text_consistency_score'] >= 0.7 else 'Scanned / OCR'}`")
                    st.markdown(f"**Name Matching:** `{doc_res['name_match_status']}`")
                    doc_num_display = doc_res['extracted_doc_number'] if doc_res['extracted_doc_number'] else "Not Detected"
                    # Mask Aadhaar for privacy
                    if len(doc_num_display) >= 12 and "-" in doc_num_display:
                        doc_num_display = "XXXX-XXXX-" + doc_num_display.split("-")[-1]
                    st.markdown(f"**Document / Cert No:** `{doc_num_display}`")
                with c_d3:
                    qr_text = doc_res['verification_details'].get('qr_details', {}).get('status', 'None')
                    sig_text = doc_res['verification_details'].get('signature_details', {}).get('status', 'None')
                    integ_text = doc_res['verification_details'].get('integrity_details', {}).get('integrity_status', 'Clean')
                    st.markdown(f"**QR/Barcode:** `{qr_text}`")
                    st.markdown(f"**Digital Signature:** `{sig_text}`")
                    st.markdown(f"**Document Integrity:** `{integ_text}`")

                # Formula Decomposition Expandable Box
                with st.expander("📐 View Mathematical Scoring Formula & Component Breakdown"):
                    st.latex(r"\text{DocumentScore} = 0.20 \cdot \text{FileValidity} + 0.20 \cdot \text{TextConsistency} + 0.20 \cdot \text{IdentityConsistency} + 0.15 \cdot \text{QRVerification} + 0.10 \cdot \text{SignatureCheck} + 0.15 \cdot \text{IntegrityCheck}")
                    
                    if b_info:
                        fc1, fc2, fc3, fc4, fc5, fc6 = st.columns(6)
                        with fc1:
                            st.metric("Validity (20%)", f"{b_info.get('file_validity', {}).get('score', 0):.2f}", f"+{b_info.get('file_validity', {}).get('component_pct', 0)}%")
                        with fc2:
                            st.metric("Text (20%)", f"{b_info.get('text_consistency', {}).get('score', 0):.2f}", f"+{b_info.get('text_consistency', {}).get('component_pct', 0)}%")
                        with fc3:
                            st.metric("Identity (20%)", f"{b_info.get('identity_consistency', {}).get('score', 0):.2f}", f"+{b_info.get('identity_consistency', {}).get('component_pct', 0)}%")
                        with fc4:
                            st.metric("QR Code (15%)", f"{b_info.get('qr_verification', {}).get('score', 0):.2f}", f"+{b_info.get('qr_verification', {}).get('component_pct', 0)}%")
                        with fc5:
                            st.metric("Signature (10%)", f"{b_info.get('signature_check', {}).get('score', 0):.2f}", f"+{b_info.get('signature_check', {}).get('component_pct', 0)}%")
                        with fc6:
                            st.metric("Integrity (15%)", f"{b_info.get('integrity_check', {}).get('score', 0):.2f}", f"+{b_info.get('integrity_check', {}).get('component_pct', 0)}%")

                st.markdown("<hr style='margin: 0.8rem 0; border-top: 1px dashed #E2E8F0;'>", unsafe_allow_html=True)

        # FINAL SUBMIT LOAN APPLICATION BUTTON
        st.markdown("---")
        st.markdown("### 🚀 Final Loan Submission")
        st.caption("Once you have screened and attached your certificates, submit your application for bank officer review.")
        
        if st.button("📥 SUBMIT LOAN APPLICATION TO BANK", type="primary", use_container_width=True):
            if not app_name or not app_mobile or not app_address:
                st.error("❌ Please fill in all required applicant fields (Name, Mobile, Address).")
            elif not st.session_state.current_application_docs:
                st.error("❌ Please screen and attach at least one supporting document before submitting.")
            else:
                with st.spinner("Recording loan application in database and generating official reference ID..."):
                    submission_result = loan_service.submit_loan_application(
                        applicant_data=applicant_dict,
                        verified_documents=st.session_state.current_application_docs
                    )
                    st.session_state.last_submission_result = submission_result
                    st.session_state.current_application_docs = []
                    st.balloons()
                    st.success(f"🎉 Loan Application Successfully Submitted! Your Application Reference ID is: **{submission_result['formatted_id']}**")

    # Display Submitted Application Summary Card
    if "last_submission_result" in st.session_state:
        sub = st.session_state.last_submission_result
        st.markdown(f"""
        <div class='summary-card'>
            <div style='display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #BFDBFE; padding-bottom: 0.8rem; margin-bottom: 1rem;'>
                <div>
                    <h3 style='margin: 0; color: #1E3A8A; font-weight: 800;'>📋 Loan Application Summary</h3>
                    <p style='margin: 0.2rem 0 0 0; color: #64748B;'>Official Digital Receipt - Cooperative Credit Society & Regional Bank</p>
                </div>
                <div style='text-align: right;'>
                    <span style='background: #1E3A8A; color: white; padding: 6px 14px; border-radius: 6px; font-weight: 700; font-size: 1.05rem;'>{sub['formatted_id']}</span>
                </div>
            </div>
            <div style='display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin-bottom: 1rem;'>
                <div><b>Applicant Name:</b> {sub['applicant_name']}</div>
                <div><b>Loan Scheme:</b> {sub['loan_type']}</div>
                <div><b>Requested Amount:</b> ₹{sub['requested_amount']:,.2f}</div>
                <div><b>Documents Submitted:</b> {sub['documents_submitted']}</div>
                <div><b>Documents Passed:</b> {sub['documents_passed']}</div>
                <div><b>Requiring Review:</b> {sub['documents_requiring_review']}</div>
                <div><b>Verification Score:</b> {sub['verification_score']}%</div>
                <div><b>Application Status:</b> <span style='font-weight: 700; color: #0284C7;'>{sub['status']}</span></div>
                <div><b>Submission Date:</b> {sub['application_date']}</div>
            </div>
            <div style='background: #FFFFFF; padding: 0.8rem; border-radius: 6px; border: 1px solid #E2E8F0; font-size: 0.85rem; color: #475569;'>
                ℹ️ <b>Next Steps:</b> Your application has been logged into the bank's core system. An authorized loan officer will review your documents and contact you at <b>{app_mobile}</b>. You may also track progress using your Application ID in the 'Track Application Status' tab.
            </div>
        </div>
        """, unsafe_allow_html=True)


# =============================================================================
# TAB 2: TRACK APPLICATION STATUS
# =============================================================================
with tab2:
    st.markdown("### 🔍 Track Online Loan Application Status")
    st.caption("Enter your Application Reference ID or Registered Mobile Number to check real-time processing status.")

    c_tr1, c_tr2 = st.columns([2, 1])
    with c_tr1:
        track_query = st.text_input("Application Reference ID (e.g. LOAN-2026-0001) or Mobile Number", placeholder="e.g. LOAN-2026-0001 or 9876543210")
    with c_tr2:
        st.write("")
        st.write("")
        track_btn = st.button("🔍 Search Status", type="primary", use_container_width=True)

    if track_btn and track_query.strip():
        # Parse search term (strip 'LOAN-2026-' if entered)
        clean_term = track_query.strip()
        if "LOAN-" in clean_term:
            try:
                numeric_part = str(int(clean_term.split("-")[-1]))
            except Exception:
                numeric_part = clean_term
        else:
            numeric_part = clean_term

        df_matched = loan_service.get_all_loan_applications(search_term=numeric_part)
        
        if df_matched.empty:
            st.warning(f"No loan applications found matching '{track_query}'. Please check your reference code.")
        else:
            for _, row in df_matched.iterrows():
                l_id = int(row["loan_id"])
                dossier = loan_service.get_loan_details(l_id)
                app = dossier.get("application", {})
                docs = dossier.get("documents", [])
                reviews = dossier.get("reviews", [])

                status = app.get("status", "Submitted")
                score = app.get("overall_score", 0.0)

                # Determine Timeline Progress
                timeline_steps = ["Submitted", "Document Verification", "Manual Review", "Final Decision"]
                current_step_idx = 0
                if status == "Document Verification":
                    current_step_idx = 1
                elif status == "Manual Review":
                    current_step_idx = 2
                elif status in ["Approved", "Rejected"]:
                    current_step_idx = 3

                st.markdown(f"""
                <div class='score-card'>
                    <div style='display: flex; justify-content: space-between; align-items: center;'>
                        <div>
                            <h3 style='margin: 0; color: #1E3A8A; font-weight: 800;'>{app.get('formatted_id', f'LOAN-{l_id}')}</h3>
                            <p style='margin: 0; color: #64748B;'>Applicant: <b>{app.get('applicant_name')}</b> | Loan: <b>{app.get('loan_type')}</b> | Amount: <b>₹{app.get('requested_amount', 0):,.2f}</b></p>
                        </div>
                        <div style='text-align: right;'>
                            <span style='background: #E0F2FE; color: #0369A1; padding: 6px 16px; border-radius: 9999px; font-weight: 700;'>Status: {status}</span>
                            <div style='margin-top: 4px; font-size: 0.85rem; color: #64748B;'>Verification Score: <b>{score:.1f}%</b></div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Attached Documents Status Matrix
                if docs:
                    st.markdown("#### 📄 Attached Documents Verification Matrix")
                    doc_rows = []
                    for d in docs:
                        doc_rows.append({
                            "Document": d.get("file_name"),
                            "Category": d.get("document_type"),
                            "Cert Number": d.get("extracted_doc_number") or "N/A",
                            "Name Match": d.get("name_match_status"),
                            "Screening Score": f"{d.get('verification_score', 0):.1f}%",
                            "Status": d.get("verification_status")
                        })
                    st.dataframe(pd.DataFrame(doc_rows), use_container_width=True, hide_index=True)

                # Official Bank Officer Review History
                if reviews:
                    st.markdown("#### 👨‍💼 Bank Officer Review Remarks")
                    for r in reviews:
                        st.info(f"**Reviewed by:** {r.get('officer_name')} | **Status Assigned:** `{r.get('officer_status')}` | **Date:** {r.get('reviewed_at')}\n\n**Officer Comments:** {r.get('officer_comments')}")
                st.markdown("---")


# =============================================================================
# TAB 3: BANK OFFICER REVIEW PORTAL
# =============================================================================
with tab3:
    st.markdown("### 👨‍💼 Bank Officer Loan Underwriting & Review Portal")
    st.caption("Inspect submitted loan dossiers, review automated document screening signals, and record authorized credit decisions.")

    # Fetch All Applications
    all_loans_df = loan_service.get_all_loan_applications()

    if all_loans_df.empty:
        st.info("No loan applications found in the database. Submit an application in Tab 1 or seed demo data in Tab 4.")
    else:
        # KPI Metric Cards
        total_apps = len(all_loans_df)
        approved_cnt = len(all_loans_df[all_loans_df["status"] == "Approved"])
        manual_rev_cnt = len(all_loans_df[all_loans_df["status"] == "Manual Review"])
        doc_ver_cnt = len(all_loans_df[all_loans_df["status"] == "Document Verification"])
        more_info_cnt = len(all_loans_df[all_loans_df["status"] == "More Information Required"])

        m1, m2, m3, m4, m5 = st.columns(5)
        with m1:
            st.metric("Total Applications", f"{total_apps}")
        with m2:
            st.metric("In Verification", f"{doc_ver_cnt}")
        with m3:
            st.metric("Manual Review", f"{manual_rev_cnt}")
        with m4:
            st.metric("Approved", f"{approved_cnt}")
        with m5:
            st.metric("More Info Required", f"{more_info_cnt}")

        st.markdown("---")

        # Filter & Search Controls
        f_col1, f_col2 = st.columns([1, 2])
        with f_col1:
            status_filter = st.selectbox("Filter Applications by Status", ["All Statuses"] + LoanApplication.ALLOWED_STATUSES, index=0)
        with f_col2:
            officer_search = st.text_input("Search Applications by Applicant Name / Mobile / ID", placeholder="Search name or ID...")

        filtered_df = loan_service.get_all_loan_applications(status_filter=status_filter, search_term=officer_search)

        st.markdown(f"**Applications Found:** `{len(filtered_df)}`")
        
        display_officer_df = filtered_df[[
            "loan_id", "applicant_name", "mobile", "loan_type", 
            "requested_amount", "income", "status", "overall_score", "application_date"
        ]].copy()
        
        display_officer_df["formatted_id"] = display_officer_df["loan_id"].apply(lambda x: f"LOAN-2026-{x:04d}")
        display_officer_df["requested_amount"] = display_officer_df["requested_amount"].apply(lambda x: f"₹{x:,.2f}")
        display_officer_df["income"] = display_officer_df["income"].apply(lambda x: f"₹{x:,.2f}/mo")
        display_officer_df["overall_score"] = display_officer_df["overall_score"].apply(lambda x: f"{x:.1f}%")

        # Table Display
        st.dataframe(
            display_officer_df[[
                "formatted_id", "applicant_name", "mobile", "loan_type",
                "requested_amount", "income", "overall_score", "status", "application_date"
            ]],
            column_config={
                "formatted_id": "Application ID",
                "applicant_name": "Applicant Name",
                "mobile": "Mobile",
                "loan_type": "Loan Scheme",
                "requested_amount": "Amount",
                "income": "Income",
                "overall_score": "Screening Score",
                "status": "Current Status",
                "application_date": "Date Submitted"
            },
            use_container_width=True,
            hide_index=True
        )

        st.markdown("---")
        st.markdown("### 🔍 Detailed Loan Inspection & Decision Panel")
        
        # Select Loan to Inspect
        loan_choices = filtered_df["loan_id"].tolist()
        loan_labels = {lid: f"LOAN-2026-{lid:04d} | {filtered_df[filtered_df['loan_id']==lid]['applicant_name'].values[0]} (₹{filtered_df[filtered_df['loan_id']==lid]['requested_amount'].values[0]:,.0f})" for lid in loan_choices}
        
        selected_loan_id = st.selectbox(
            "Select Loan Application to Inspect & Underwrite",
            options=loan_choices,
            format_func=lambda x: loan_labels.get(x, str(x))
        )

        if selected_loan_id:
            dossier = loan_service.get_loan_details(selected_loan_id)
            app_info = dossier.get("application", {})
            doc_records = dossier.get("documents", [])
            review_history = dossier.get("reviews", [])

            c_info1, c_info2 = st.columns([1, 1])
            with c_info1:
                st.markdown(f"""
                <div class='step-box'>
                    <h4 style='margin:0; color:#1E3A8A;'>👤 Applicant Profile</h4>
                    <p style='margin: 4px 0;'><b>Name:</b> {app_info.get('applicant_name')}</p>
                    <p style='margin: 4px 0;'><b>Mobile:</b> {app_info.get('mobile')}</p>
                    <p style='margin: 4px 0;'><b>Email:</b> {app_info.get('email')}</p>
                    <p style='margin: 4px 0;'><b>Address:</b> {app_info.get('address')}</p>
                    <p style='margin: 4px 0;'><b>Date of Birth:</b> {app_info.get('dob')}</p>
                    <p style='margin: 4px 0;'><b>Occupation:</b> {app_info.get('occupation')}</p>
                    <p style='margin: 4px 0;'><b>Monthly Income:</b> ₹{app_info.get('income', 0):,.2f}</p>
                </div>
                """, unsafe_allow_html=True)

            with c_info2:
                st.markdown(f"""
                <div class='step-box'>
                    <h4 style='margin:0; color:#1E3A8A;'>💵 Loan Terms & Details</h4>
                    <p style='margin: 4px 0;'><b>Loan Type:</b> {app_info.get('loan_type')}</p>
                    <p style='margin: 4px 0;'><b>Requested Amount:</b> ₹{app_info.get('requested_amount', 0):,.2f}</p>
                    <p style='margin: 4px 0;'><b>Repayment Period:</b> {app_info.get('repayment_period')}</p>
                    <p style='margin: 4px 0;'><b>Stated Purpose:</b> {app_info.get('loan_purpose')}</p>
                    <p style='margin: 4px 0;'><b>Automated Screening Score:</b> <b style='color:#1E3A8A;'>{app_info.get('overall_score', 0):.1f}%</b></p>
                    <p style='margin: 4px 0;'><b>Current Status:</b> <span style='font-weight:700; color:#0284C7;'>{app_info.get('status')}</span></p>
                </div>
                """, unsafe_allow_html=True)

            # Detailed Document Screening Inspection
            st.markdown("#### 📄 Document Screening Audit Breakdown")
            if not doc_records:
                st.warning("No documents attached to this loan application.")
            else:
                for d in doc_records:
                    v_stat = d.get("verification_status")
                    b_badge = "✅ PASS" if v_stat == "PASS" else "⚠️ REVIEW REQUIRED" if v_stat == "REVIEW REQUIRED" else "❓ UNABLE TO VERIFY"
                    
                    with st.expander(f"📁 {d.get('file_name')} — {d.get('document_type')} ({b_badge} - {d.get('verification_score', 0):.1f}%)"):
                        c_sub1, c_sub2 = st.columns(2)
                        with c_sub1:
                            st.write(f"**Document Type:** {d.get('document_type')}")
                            st.write(f"**File Size:** {d.get('file_size', 0) / 1024:.1f} KB | **MIME:** {d.get('mime_type')}")
                            st.write(f"**SHA-256 Hash:** `{d.get('sha256_hash')[:32]}...`")
                            st.write(f"**Extracted Document Number:** `{d.get('extracted_doc_number') or 'N/A'}`")
                            st.write(f"**Issuing Authority:** `{d.get('issuing_authority') or 'N/A'}`")
                        with c_sub2:
                            st.write(f"**Name Match Status:** `{d.get('name_match_status')}`")
                            st.write(f"**File Validity Score:** `{d.get('file_validity_score', 0):.2f}`")
                            st.write(f"**Text Consistency Score:** `{d.get('text_consistency_score', 0):.2f}`")
                            st.write(f"**Identity Consistency Score:** `{d.get('identity_consistency_score', 0):.2f}`")
                            st.write(f"**QR Verification Score:** `{d.get('qr_verification_score', 0):.2f}`")
                            st.write(f"**Signature Check Score:** `{d.get('signature_check_score', 0):.2f}`")
                            st.write(f"**Integrity Check Score:** `{d.get('integrity_check_score', 0):.2f}`")
                        
                        if d.get("extracted_text"):
                            st.caption("**Extracted Text Snippet:**")
                            st.code(d.get("extracted_text")[:300], language="text")

            # Officer Review & Action Box
            st.markdown("#### ⚖️ Record Official Bank Officer Decision")
            with st.form(f"officer_action_form_{selected_loan_id}"):
                c_act_col1, c_act_col2 = st.columns(2)
                with c_act_col1:
                    new_officer_status = st.selectbox(
                        "Select Decision / Action Status *",
                        ["Approved", "Rejected", "More Information Required", "Manual Review", "Document Verification"],
                        index=0
                    )
                    officer_name_input = st.text_input("Reviewing Officer Name / Designation *", value="A. K. Mukherjee (Chief Credit Manager)")
                with c_act_col2:
                    officer_comments_input = st.text_area(
                        "Officer Inspection Notes & Comments *",
                        placeholder="Enter credit assessment remarks, collateral notes, or reasons for approval/rejection...",
                        height=100
                    )

                submit_officer_decision = st.form_submit_button("💾 SUBMIT OFFICIAL OFFICER DECISION", type="primary", use_container_width=True)

            if submit_officer_decision:
                if not officer_comments_input.strip():
                    st.error("❌ Please provide officer inspection notes or reasoning before submitting.")
                else:
                    loan_service.add_officer_review(
                        loan_id=selected_loan_id,
                        officer_status=new_officer_status,
                        officer_comments=officer_comments_input.strip(),
                        officer_name=officer_name_input.strip()
                    )
                    st.success(f"✅ Officer review recorded! Status for LOAN-2026-{selected_loan_id:04d} updated to '{new_officer_status}'.")
                    st.rerun()


# =============================================================================
# TAB 4: TEST SCENARIOS & DEMO DATA
# =============================================================================
with tab4:
    st.markdown("### 🧪 One-Click Demonstration Scenarios")
    st.caption("Load representative academic test cases to test automated verification formulas and edge cases.")

    col_t1, col_t2, col_t3 = st.columns(3)

    with col_t1:
        st.markdown("#### 🌾 Case 1: Agricultural Credit Loan")
        st.caption("**Applicant:** Ramesh Kumar Sharma (Farmer)\n- Valid Aadhaar with QR code payload\n- Verified Tahsildar Income Certificate\n- **Expected:** Score >85%, Status: PASS")
        if st.button("🚀 Load Scenario 1 (All Clear)", key="demo_case_1", use_container_width=True):
            st.session_state.form_name = "Ramesh Kumar Sharma"
            st.session_state.form_mobile = "9876543210"
            st.session_state.form_email = "ramesh.sharma@coopbank.in"
            st.session_state.form_address = "Village Pipariya, Tehsil Hoshangabad, MP - 461001"
            st.session_state.form_dob = datetime.date(1982, 5, 14)
            st.session_state.form_occupation = "Farmer / Agriculturalist"
            st.session_state.form_income = 45000.0
            st.session_state.form_loan_type = "Agricultural Credit Loan"
            st.session_state.form_amount = 250000.0
            st.session_state.form_purpose = "Purchase of high-yield wheat seeds and drip irrigation pipeline."
            st.session_state.form_period = "36 Months"
            
            sample_doc_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "sample_documents")
            sample_file = os.path.join(sample_doc_dir, "sample_aadhaar_ramesh.png")
            if os.path.exists(sample_file):
                with open(sample_file, "rb") as f:
                    st.session_state.temp_uploaded_bytes = f.read()
                    st.session_state.temp_uploaded_name = "sample_aadhaar_ramesh.png"
                    st.session_state.temp_uploaded_type = "Aadhaar/Identity Proof"
            st.success("Scenario 1 loaded! Switch to Tab 1 to screen and submit.")

    with col_t2:
        st.markdown("#### 💼 Case 2: Housing Loan (Salaried)")
        st.caption("**Applicant:** Anjali Deshmukh (Engineer)\n- Monthly Income: ₹95,000\n- Apex Cotton Mills Pay Slip with Digital Seal\n- **Expected:** Score >85%, Status: PASS")
        if st.button("🚀 Load Scenario 2 (Salaried)", key="demo_case_2", use_container_width=True):
            st.session_state.form_name = "Anjali Deshmukh"
            st.session_state.form_mobile = "9765432109"
            st.session_state.form_email = "anjali.deshmukh@coopbank.in"
            st.session_state.form_address = "Plot 45, Cotton Market Road, Wardha, Maharashtra - 442001"
            st.session_state.form_dob = datetime.date(1990, 8, 19)
            st.session_state.form_occupation = "Salaried Employee (Private Sector)"
            st.session_state.form_income = 95000.0
            st.session_state.form_loan_type = "Home / Rural Housing Loan"
            st.session_state.form_amount = 1200000.0
            st.session_state.form_purpose = "Construction of residential rural housing on ancestral plot."
            st.session_state.form_period = "120 Months"

            sample_doc_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "sample_documents")
            sample_file = os.path.join(sample_doc_dir, "sample_salary_slip_anjali.pdf")
            if os.path.exists(sample_file):
                with open(sample_file, "rb") as f:
                    st.session_state.temp_uploaded_bytes = f.read()
                    st.session_state.temp_uploaded_name = "sample_salary_slip_anjali.pdf"
                    st.session_state.temp_uploaded_type = "Salary Slip"
            st.success("Scenario 2 loaded! Switch to Tab 1 to screen and submit.")

    with col_t3:
        st.markdown("#### ⚠️ Case 3: Tampering / Mismatch Test")
        st.caption("**Applicant:** Suresh Patel (Entered)\n- Uploaded document has mismatched name 'Vikramaditya Chauhan'\n- **Expected:** Score <60%, Status: REVIEW REQUIRED")
        if st.button("🚀 Load Scenario 3 (Mismatch)", key="demo_case_3", use_container_width=True):
            st.session_state.form_name = "Suresh Patel"
            st.session_state.form_mobile = "9823456781"
            st.session_state.form_email = "suresh.patel@coopbank.in"
            st.session_state.form_address = "Shop No 14, Main Market, Anand, Gujarat - 388001"
            st.session_state.form_dob = datetime.date(1978, 11, 22)
            st.session_state.form_occupation = "Small Business Owner / MSME"
            st.session_state.form_income = 75000.0
            st.session_state.form_loan_type = "Small Business / MSME Loan"
            st.session_state.form_amount = 500000.0
            st.session_state.form_purpose = "Expansion of commercial milk chilling unit."
            st.session_state.form_period = "48 Months"

            sample_doc_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "sample_documents")
            sample_file = os.path.join(sample_doc_dir, "sample_name_mismatch_test.png")
            if os.path.exists(sample_file):
                with open(sample_file, "rb") as f:
                    st.session_state.temp_uploaded_bytes = f.read()
                    st.session_state.temp_uploaded_name = "sample_name_mismatch_test.png"
                    st.session_state.temp_uploaded_type = "Aadhaar/Identity Proof"
            st.success("Scenario 3 loaded! Switch to Tab 1 to test mismatch screening.")
