import streamlit as st
import os
import base64
import math
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
from io import BytesIO

# ==============================
# 🎨 1. Premium Page Style
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
        padding: 20px;
        border-radius: 20px;
        text-align: center;
        color: white;
        font-size: 28px;
        font-weight: bold;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        margin-bottom: 10px;
    }}
    .section {{
        background: rgba(255,255,255,0.9);
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.05);
    }}
    /* تقليل المسافات العلوية تماماً */
    .block-container {{
        padding-top: 1rem !important;
        padding-bottom: 0rem !important;
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
# ⚙️ 3. App Configuration
# ==============================
st.set_page_config(page_title="AED PK Pro", layout="wide")
set_page_style('bg.jpg' if os.path.exists("bg.jpg") else "")

# الهيدر مباشرة بدون أي مسافات قبله
st.markdown('<div class="hero">💊 AED PK CLINICAL PLATFORM</div>', unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs(["🎯 Calculator", "📚 Knowledge", "⚖️ Decision", "📋 Case Summary"])

# ==============================
# 🎯 TAB 1: CALCULATOR
# ==============================
with tab1:
    st.markdown('<div class="section">', unsafe_allow_html=True)
    
    # وضع اختيار الدواء في السطر الأول مباشرة
    selected_drug = st.selectbox("💊 Select Medication", ["Phenytoin", "Valproic acid", "Carbamazepine", "Levetiracetam"])
    
    col_inputs, col_outputs = st.columns([1.2, 1])
    
    with col_inputs:
        c1, c2 = st.columns(2)
        with c1:
            age = st.number_input("Age", 1, 100, 30)
            weight = st.number_input("Weight (kg)", 10.0, 250.0, 70.0)
            height = st.number_input("Height (cm)", 50, 250, 170)
        with c2:
            gender = st.selectbox("Gender", ["Male", "Female"])
            scr = st.number_input("SCr (mg/dL)", 0.1, 5.0, 1.0)
            target = st.slider("Target Css", 5, 100, 15 if selected_drug != "Valproic acid" else 75)
        
        interval = st.selectbox("Dosing Interval", [4, 6, 8, 12, 24], index=3)

        # --- الحسابات ---
        ht_in = height / 2.54
        ibw = (50 + 2.3*(ht_in-60)) if gender=="Male" else (45.5 + 2.3*(ht_in-60))
        dosing_weight = weight
        is_obese = weight > (1.2 * ibw)
        
        s_factor, albumin, vmax, km, extra_info = 0.92, 4.4, 7.0, 4.0, ""

        if selected_drug == "Phenytoin":
            st.markdown("---")
            if is_obese:
                dosing_weight = ibw + 0.4 * (weight - ibw)
                st.warning(f"Adjusted Weight: {dosing_weight:.1f} kg")
            cp1, cp2 = st.columns(2)
            with cp1:
                vmax = st.number_input("Vmax", 1.0, 15.0, 7.0)
                albumin = st.number_input("Albumin", 0.5, 6.0, 4.4)
            with cp2:
                km = st.number_input("Km", 1.0, 10.0, 4.0)
                salt = st.selectbox("Form", ["Sodium (0.92)", "Acid (1.0)"])
            s_factor = 0.92 if "Sodium" in salt else 1.0
            if albumin < 4.4: extra_info = f"Albumin correction applied."

        crcl_wt = ibw if is_obese else weight
        crcl = ((140-age)*crcl_wt)/(72*scr) if gender=="Male" else ((140-age)*crcl_wt)/(72*scr)*0.85

        # --- المعادلات ---
        css_max, css_min = None, None
        if selected_drug == "Phenytoin":
            vd = 0.7 * dosing_weight
            vmax_t = vmax * dosing_weight
            md = ((vmax_t * target) / (km + target)) / (24/interval)
            ld = target * vd
            k_el = (vmax_t / (km + target)) / vd
            css_max = (target / s_factor) + ((md * s_factor) / vd)
            css_min = css_max * math.exp(-k_el * interval)
            t_half = 0.693 / k_el
        elif selected_drug == "Valproic acid":
            vd, cl = 0.15 * weight, 0.008 * weight
            k = cl/vd; ld, md = target*vd, target*cl*interval; t_half = 0.693/k
        elif selected_drug == "Carbamazepine":
            vd, cl = 1.4 * weight, 0.06 * weight
            k = cl/vd; ld, md = target*vd, target*cl*interval; t_half = 0.693/k
        else: # Levetiracetam
            vd = 0.6 * weight; cl = (crcl * 0.6) / 1000 * 60
            k = cl/vd; ld, md = target*vd, target*cl*interval; t_half = 0.693/k

        if selected_drug != "Phenytoin" and crcl < 50: md *= (crcl/100)

    with col_outputs:
        st.subheader("Results")
        if st.button("🚀 Calculate"):
            m1, m2 = st.columns(2)
            m1.metric("CrCl", f"{crcl:.1f}")
            m2.metric("t½ (h)", f"{t_half:.1f}" if selected_drug != "Phenytoin" else "N/A")
            if css_max: st.info(f"Peak: {css_max:.2f} | Trough: {css_min:.2f}")
            st.success(f"**Regimen:** LD {round(ld)} mg | MD {round(md)} mg q{interval}h")
            
            pdf_data = create_pdf_report(age, weight, height, selected_drug, crcl, ld, md, interval, css_max, css_min)
            st.download_button("📥 Report", pdf_data, "Report.pdf", "application/pdf")
    st.markdown('</div>', unsafe_allow_html=True)

# بقية الـ Tabs
with tab2: st.write(f"Knowledge Base for {selected_drug}")
with tab3: st.write("Clinical Decision Support")
with tab4: st.write("Case Summary Presentation")

st.markdown("<center>💙 Clinical PK Project | MNU</center>", unsafe_allow_html=True)
