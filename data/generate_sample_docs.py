"""
Script to generate high-fidelity test sample certificates and documents with QR codes for demonstration.
"""

import os
import io
import qrcode
from PIL import Image, ImageDraw, ImageFont

def generate_sample_documents():
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sample_documents")
    os.makedirs(out_dir, exist_ok=True)

    # 1. Generate Aadhaar Card with QR Code (Ramesh Kumar Sharma)
    img_w, img_h = 750, 480
    aadhaar_img = Image.new("RGB", (img_w, img_h), color="#FFFFFF")
    draw = ImageDraw.Draw(aadhaar_img)

    # Decorative header bar
    draw.rectangle([(0, 0), (img_w, 75)], fill="#1E3A8A")
    draw.text((30, 20), "GOVERNMENT OF INDIA - UNIQUE IDENTIFICATION AUTHORITY OF INDIA", fill="#FFFFFF")
    draw.text((30, 45), "आधार - विशिष्ट पहचान प्राधिकरण (Mera Aadhaar, Meri Pehchan)", fill="#93C5FD")

    # Body details
    draw.rectangle([(20, 90), (730, 460)], outline="#E2E8F0", width=2)
    
    # Left Photo placeholder
    draw.rectangle([(40, 115), (200, 310)], fill="#F1F5F9", outline="#94A3B8", width=2)
    draw.text((85, 200), "[ PHOTO ]", fill="#64748B")

    # Personal Information
    draw.text((230, 120), "Name / नाम :", fill="#64748B")
    draw.text((360, 120), "Ramesh Kumar Sharma", fill="#0F172A")

    draw.text((230, 160), "DOB / जन्म तिथि :", fill="#64748B")
    draw.text((360, 160), "14/05/1982", fill="#0F172A")

    draw.text((230, 200), "Gender / लिंग :", fill="#64748B")
    draw.text((360, 200), "Male / पुरुष", fill="#0F172A")

    draw.text((230, 240), "Address / पता :", fill="#64748B")
    draw.text((360, 240), "Village Pipariya, Tehsil Hoshangabad, MP - 461001", fill="#0F172A")

    # Big Aadhaar Number at bottom
    draw.rectangle([(40, 395), (710, 445)], fill="#EFF6FF")
    draw.text((220, 410), "9821  4820  1928", fill="#1E3A8A")

    # Generate QR Code
    qr = qrcode.QRCode(version=1, box_size=4, border=2)
    qr_payload = "<?xml version='1.0'?><AadhaarData uid='982148201928' name='Ramesh Kumar Sharma' dob='14/05/1982' gender='M' co='S/O Sharma' vtc='Pipariya' dist='Hoshangabad' state='Madhya Pradesh' pc='461001' sig='VALID_DIGITAL_SIG_UIDAI_PKI'/>"
    qr.add_data(qr_payload)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="#0F172A", back_color="#FFFFFF").resize((130, 130))
    aadhaar_img.paste(qr_img, (580, 115))

    aadhaar_path = os.path.join(out_dir, "sample_aadhaar_ramesh.png")
    aadhaar_img.save(aadhaar_path, "PNG")

    # 2. Generate PDF Income Certificate
    try:
        import pypdf
        # Create a simple PDF via raw PDF stream
        pdf_content = (
            "%PDF-1.4\n"
            "1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj\n"
            "2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj\n"
            "3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >> endobj\n"
            "4 0 obj << /Length 520 >> stream\n"
            "BT\n"
            "/F1 18 Tf\n"
            "50 720 Td (GOVERNMENT OF MADHYA PRADESH - REVENUE DEPARTMENT) Tj\n"
            "/F1 14 Tf\n"
            "0 -30 Td (CERTIFICATE OF ANNUAL INCOME) Tj\n"
            "/F1 11 Tf\n"
            "0 -40 Td (Certificate Reference No: REV-2026-89102) Tj\n"
            "0 -25 Td (Date of Issue: 10/02/2026) Tj\n"
            "0 -30 Td (This is to certify that Shri Ramesh Kumar Sharma, resident of Village Pipariya,) Tj\n"
            "0 -20 Td (Tehsil Hoshangabad, District Hoshangabad, has an assessed Gross Annual Income of:) Tj\n"
            "/F1 13 Tf\n"
            "0 -30 Td (Rs. 5,40,000 /- [Rupees Five Lakh Forty Thousand Only] from Agriculture & Allied Sources.) Tj\n"
            "/F1 11 Tf\n"
            "0 -40 Td (Issuing Authority: Tahsildar / Sub-Divisional Magistrate) Tj\n"
            "0 -20 Td (Digitally signed by Tahsildar, Revenue Department) Tj\n"
            "0 -20 Td (Signature Valid - Authorized Public Key Cryptography Seal) Tj\n"
            "ET\n"
            "endstream\n"
            "endobj\n"
            "5 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj\n"
            "xref\n"
            "0 6\n"
            "0000000000 65535 f \n"
            "0000000010 00000 n \n"
            "0000000060 00000 n \n"
            "0000000117 00000 n \n"
            "0000000248 00000 n \n"
            "0000000820 00000 n \n"
            "trailer << /Size 6 /Root 1 0 R >>\n"
            "startxref\n"
            "895\n"
            "%%EOF\n"
        )
        pdf_path = os.path.join(out_dir, "sample_income_certificate_ramesh.pdf")
        with open(pdf_path, "wb") as f:
            f.write(pdf_content.encode("latin1"))
    except Exception as e:
        print("PDF Gen Error:", e)

    # 3. Generate Salary Slip PDF
    pdf_sal_content = (
        "%PDF-1.4\n"
        "1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj\n"
        "2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj\n"
        "3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >> endobj\n"
        "4 0 obj << /Length 580 >> stream\n"
        "BT\n"
        "/F1 16 Tf\n"
        "50 720 Td (APEX COTTON MILLS LTD - PAYSLIP FOR FEBRUARY 2026) Tj\n"
        "/F1 11 Tf\n"
        "0 -30 Td (Employee Name: Anjali Deshmukh) Tj\n"
        "0 -20 Td (Employee ID: EMP-9821 | Designation: Senior Textile Engineer) Tj\n"
        "0 -20 Td (Bank Account: 4091823901 | IFSC: COOP0001001) Tj\n"
        "0 -30 Td (----------------------------------------------------------------------------------) Tj\n"
        "0 -25 Td (Basic Pay: Rs 65,000.00        | Provident Fund (PF): Rs 4,800.00) Tj\n"
        "0 -20 Td (HRA Allowance: Rs 20,000.00    | Professional Tax:    Rs 200.00) Tj\n"
        "0 -20 Td (Special Allowance: Rs 10,000.00| Income Tax (TDS):    Rs 5,800.00) Tj\n"
        "0 -25 Td (----------------------------------------------------------------------------------) Tj\n"
        "/F1 13 Tf\n"
        "0 -25 Td (Gross Earnings: Rs 95,000.00   | Total Deductions: Rs 10,800.00) Tj\n"
        "0 -25 Td (NET TAKE-HOME SALARY: Rs 84,200.00) Tj\n"
        "/F1 10 Tf\n"
        "0 -40 Td (Digitally signed by Human Resources & Finance Controller) Tj\n"
        "ET\n"
        "endstream\n"
        "endobj\n"
        "5 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj\n"
        "xref\n"
        "0 6\n"
        "0000000000 65535 f \n"
        "0000000010 00000 n \n"
        "0000000060 00000 n \n"
        "0000000117 00000 n \n"
        "0000000248 00000 n \n"
        "0000000880 00000 n \n"
        "trailer << /Size 6 /Root 1 0 R >>\n"
        "startxref\n"
        "955\n"
        "%%EOF\n"
    )
    sal_path = os.path.join(out_dir, "sample_salary_slip_anjali.pdf")
    with open(sal_path, "wb") as f:
        f.write(pdf_sal_content.encode("latin1"))

    # 4. Generate Mismatched Name Test Image (for testing Review Required / Unable to Verify)
    mismatch_img = Image.new("RGB", (600, 300), color="#FFFBEB")
    d_mis = ImageDraw.Draw(mismatch_img)
    d_mis.rectangle([(0, 0), (600, 40)], fill="#B45309")
    d_mis.text((20, 12), "IDENTITY DOCUMENT - SAMPLE MISMATCH TEST", fill="#FFFFFF")
    d_mis.text((30, 70), "Applicant Name: Vikramaditya Chauhan", fill="#991B1B")
    d_mis.text((30, 110), "Document Number: MISMATCH-998877", fill="#1E293B")
    d_mis.text((30, 150), "Issuing Authority: Unknown Private Issuer", fill="#475569")
    d_mis.text((30, 190), "Date: 01/01/2020", fill="#475569")
    d_mis.rectangle([(30, 230), (570, 270)], outline="#DC2626")
    d_mis.text((50, 245), "Note: Uploading this against Ramesh Sharma triggers Name Mismatch Alert", fill="#DC2626")
    mismatch_path = os.path.join(out_dir, "sample_name_mismatch_test.png")
    mismatch_img.save(mismatch_path, "PNG")

    print(f"Sample documents successfully generated in {out_dir}")

if __name__ == "__main__":
    generate_sample_documents()
