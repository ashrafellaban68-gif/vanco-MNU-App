import streamlit as st
import os
import base64
import math
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
from io import BytesIO

# ==============================
# 🎨 1. Page Style & Layout Correction
# ==============================
def set_page_style(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            bin_str = base64.b64encode(f.read()).decode()
        bg_img = f'url("data:image/png;base64,{bin_str}")'
    except:
        bg_img = "none"

    st.markdown(f'''
    <style>
    .stApp {{
        background-image: linear-gradient(rgba(255, 255, 255, 0.75), rgba(255, 255, 255, 0.75)), {bg_img};
        background-size: cover;
        background-attachment: fixed;
    }}
    .hero {{
        background: linear-gradient(135deg, #1e3a8a, #3b82f6);
        padding: 25px;
        border-radius: 20px;
        text-align: center;
        color: white;
        font-size: 32px;
        font-weight: bold;
        box-shadow: 0 10px 25px rgba(0,0,0,0.2);
        margin-bottom: 20px;
    }}
    .section {{
        background: rgba(255,255,255,0.9);
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.05);
    }}
    /* إزالة أي هوامش تلقائية قد تسبب المربع الأبيض */
    .stSelectbox, .stNumberInput {{
        margin-top: -10px;
    }}
    </style>
    ''', unsafe_allow_html=True)

# ==============================
# 📄 2. PDF Report Generator
# ==============================
def create_pdf_report(age, weight, height, drug, crcl, ld, md, interval, css_max=None, css_min=None, extra_notes=""):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    content = []
    content.append(Paragraph("Clinical Pharmacokinetics Report", styles['Title']))
    content.append(Spacer(1, 20))
    content.append(Paragraph(f"<b>Drug:</b> {drug}", styles['Normal']))
    content.append(Paragraph(f"<b>Patient:</b> {age}Y | {weight}kg | {height}cm", styles['Normal']))
    content.append(Paragraph(f"<b>CrCl:</b> {crcl:.1f} mL/min", styles['Normal']))
    content.append(Spacer(1, 15))
    content.append(Paragraph("<b>Dosage Regimen:</b>", styles['Heading2']))
    content.append(Paragraph(f"- Loading Dose: {round(ld)} mg", styles['Normal']))
    content.append(Paragraph(f"- Maintenance Dose: {round(md)} mg every {interval} hours", styles['Normal']))
    if css_max:
        content.append(Paragraph(f"- Predicted Css Max: {css_max:.2f} mg/L", styles['Normal']))
        content.append(Paragraph(f"- Predicted Css Min: {css_min:.2f} mg/L", styles['Normal']))
    doc.build(content)
    return buffer.getvalue()

# ==============================
# ⚙️ 3. App Config
# ==============================
st.set_page_config(page_title="AED PK Pro Platform", layout="wide")
set_page_style('bg.jpg' if os.path.exists("bg.jpg") else "")

st.markdown('<div class="hero">💊 AED PK CLINICAL PLATFORM</div>', unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs(["🎯 Calculator", "📚 Knowledge", "⚖️ Decision", "📋 Case Summary"])

# ==============================
# 🎯 TAB 1: CALCULATOR
# ==============================
with tab1:
    st.markdown('<div class="section">', unsafe_allow_html=True)
    
    # اختيار الدواء في الأعلى مباشرة بدون تقسيم أعمدة قد يسبب فراغ
    selected_drug = st.selectbox("💊 Select Drug", ["Phenytoin", "Valproic acid", "Carbamazepine", "Levetiracetam"])
    
    col_in, col_out = st.columns([1.2, 1])
    
    with col_in:
        c1, c2 = st.columns(2)
        with c1:
            age = st.number_input("Age", 1, 100, 30)
            weight = st.number_input("Actual Weight (kg)", 10.0, 250.0, 70.0)
            height = st.number_input("Height (cm)", 50, 250, 170)
        with c2:
            gender = st.selectbox("Gender", ["Male", "Female"])
            scr = st.number_input("SCr (mg/dL)", 0.1, 5.0, 1.0)
            target = st.slider("Target Css (mg/L)", 5, 100, 15 if selected_drug != "Valproic acid" else 75)
        
        interval = st.selectbox("Interval (hr)", [4, 6, 8, 12, 24], index=3)

        # Calculations
        ht_in = height / 2.54
        ibw = (50 + 2.3*(ht_in-60)) if gender=="Male" else (45.5 + 2.3*(ht
