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
        margin-top: 15px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.05);
    }}
    .stButton>button {{
        background: linear-gradient(45deg, #1e3a8a, #3b82f6);
        color: white;
        border-radius: 30px;
        height: 3.5em;
        width: 100%;
        font-weight: bold;
        border: none;
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
    if extra_notes:
        content.append(Spacer(1, 10))
        content.append(Paragraph(f"<b>Clinical Notes:</b> {extra_notes}", styles['Normal']))
    content.append(Spacer(20, 20))
    content.append(Paragraph("<i>Note: Generated via AED PK Pro Platform.</i>", styles['Italic']))
    doc.build(content)
    return buffer.getvalue()

# ==============================
# ⚙️ 3. Execution
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
    
    # تمت إزالة الأعمدة الفاضية هنا لرفع القائمة المنسدلة للأعلى مباشرة
    selected_drug = st.selectbox("Select Drug", ["Phenytoin", "Valproic acid", "Carbamazepine", "Levetiracetam"])
    
    c_in, c_res = st.columns([1.2, 1])
    
    with c_in:
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

        # --- Calculations Logic ---
        ht_in = height / 2.54
        ibw = (50 + 2.3*(ht_in-60)) if gender=="Male" else (45.5 + 2.3*(ht_in-60))
        dosing_weight = weight
        is_obese = weight > (1.2 * ibw)
        
        # --- Phenytoin Advanced ---
        s_factor = 0.92
        albumin = 4.4
        vmax, km = 7.0, 4.0
        extra_info = ""

        if selected_drug == "Phenytoin":
            st.markdown("---")
            st.subheader("🧬 Phenytoin Parameters")
            if is_obese:
                dosing_weight = ibw + 0.4 * (weight - ibw)
                st.warning(f"Obesity: Using Adjusted Weight ({dosing_weight:.1f} kg)")
            
            cp1, cp2 = st.columns(2)
            with cp1:
                vmax = st.number_input("Vmax (mg/kg/day)", 1.0, 15.0, 7.0)
                albumin = st.number_input("Albumin (g/dL)", 0.5, 6.0, 4.4)
            with cp2:
                km = st.number_input("Km (mg/L)", 1.0, 10.0, 4.0)
                salt_type = st.selectbox("Form (S)", ["Sodium (0.92)", "Acid (1.0)"])
            
            s_factor = 0.92 if "Sodium" in salt_type else 1.0
            
            if albumin < 4.4:
                adj_target = target / ((0.2 * albumin) + 0.1)
                extra_info = f"Albumin correction: Adjusted target is {adj_target:.1f} mg/L."

        crcl_wt = ibw if is_obese else weight
        crcl = ((140-age)*crcl_wt)/(72*scr) if gender=="Male" else ((140-age)*crcl_wt)/(72*scr)*0.85

        # --- Specific Drug Equations ---
        css_max, css_min = None, None
        if selected_drug == "Phenytoin":
            vd = 0.7 * dosing_weight
            vmax_total = vmax * dosing_weight
            md = ((vmax_total * target) / (km + target)) / (24/interval)
            ld = target * vd
            k_el = (vmax_total / (km + target)) / vd
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

    with c_res:
        st.subheader("Results")
        if st.button("🚀 Calculate"):
            m1, m2, m3 = st.columns(3)
            m1.metric("CrCl", f"{crcl:.1f}")
            m2.metric("Vd (L)", f"{vd:.1f}")
            m3.metric("t½ (h)", f"{t_half:.1f}" if selected_drug != "Phenytoin" else "N/A")
            
            if css_max:
                st.info(f"Steady State: Peak {css_max:.2f} | Trough {css_min:.2f}")
            
            st.success(f"**Plan:** LD {round(ld)} mg | MD {round(md)} mg q{interval}h")
            
            pdf_data = create_pdf_report(age, weight, height, selected_drug, crcl, ld, md, interval, css_max, css_min, extra_info)
            st.download_button("📥 Download Report", pdf_data, "Report.pdf", "application/pdf")
    st.markdown('</div>', unsafe_allow_html=True)

# Tabs 2, 3, 4 تظل كما هي
with tab2:
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.subheader(f"Drug Profile: {selected_drug}")
    st.info("Pharmacological details and TDM ranges.")
    st.markdown('</div>', unsafe_allow_html=True)

with tab3:
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.subheader("Clinical Reasoning")
    if is_obese: st.warning("Obesity adjustment applied.")
    if crcl < 50: st.error("Renal adjustment applied.")
    st.markdown('</div>', unsafe_allow_html=True)

with tab4:
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.subheader("Case Summary")
    st.code(f"Patient: {age}Y, {weight}kg | Drug: {selected_drug} | Plan: {round(md)}mg q{interval}h")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<center>💙 Clinical PK Project | MNU</center>", unsafe_allow_html=True)
