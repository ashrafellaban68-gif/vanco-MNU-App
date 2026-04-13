import streamlit as st
import os
import base64
import math
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
from io import BytesIO

# ==============================
# 🎨 1. Premium Page Style (Medical UI)
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
        background-image: linear-gradient(rgba(255, 255, 255, 0.85), rgba(255, 255, 255, 0.85)), {bg_img};
        background-size: cover;
        background-attachment: fixed;
    }}
    .hero {{
        background: linear-gradient(135deg, #1e3a8a, #3b82f6);
        padding: 30px;
        border-radius: 20px;
        text-align: center;
        color: white;
        font-size: 38px;
        font-weight: 900;
        box-shadow: 0 10px 25px rgba(0,0,0,0.2);
        margin-bottom: 25px;
        letter-spacing: 1px;
    }}
    .section {{
        background: rgba(255,255,255,0.95);
        padding: 25px;
        border-radius: 15px;
        margin-top: 20px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.05);
        border: 1px solid #e2e8f0;
    }}
    .stButton>button {{
        background: linear-gradient(45deg, #1e3a8a, #3b82f6);
        color: white;
        border-radius: 30px;
        height: 3.5em;
        width: 100%;
        font-weight: bold;
        font-size: 16px;
        border: none;
        transition: 0.3s;
    }}
    .stButton>button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(30, 58, 138, 0.3);
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
    content.append(Paragraph("DoseWise - Clinical PK Report", styles['Title']))
    content.append(Spacer(1, 20))
    content.append(Paragraph(f"<b>Drug:</b> {drug}", styles['Normal']))
    content.append(Paragraph(f"<b>Patient:</b> {age}Y | {weight}kg | {height}cm", styles['Normal']))
    content.append(Paragraph(f"<b>CrCl:</b> {crcl:.1f} mL/min", styles['Normal']))
    content.append(Spacer(1, 15))
    content.append(Paragraph("<b>Calculated Regimen:</b>", styles['Heading2']))
    content.append(Paragraph(f"- Loading Dose: {round(ld)} mg", styles['Normal']))
    content.append(Paragraph(f"- Maintenance Dose: {round(md)} mg every {interval} hours", styles['Normal']))
    doc.build(content)
    return buffer.getvalue()

# ==============================
# ⚙️ 3. Execution & Logic
# ==============================
st.set_page_config(page_title="DoseWise | Clinical PK Platform", layout="wide")
set_page_style('bg.jpg' if os.path.exists("bg.jpg") else "")

# الاسم الجديد
st.markdown('<div class="hero">💊 Dose Wise </div>', unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs(["🎯 Calculator", "📚 Knowledge", "⚖️ Decision", "📋 Case Summary"])

with tab1:
    st.markdown('<div class="section">', unsafe_allow_html=True)
    c_in, c_res = st.columns([1.3, 1])
    with c_in:
        selected_drug = st.selectbox("Select Medication", ["Phenytoin", "Valproic acid", "Carbamazepine", "Levetiracetam"])
        c_in_1, c_in_2 = st.columns(2)
        with c_in_1:
            age = st.number_input("Age (Years)", 1, 100, 30)
            weight = st.number_input("Weight (kg)", 10.0, 250.0, 70.0)
            height = st.number_input("Height (cm)", 50, 250, 170)
        with c_in_2:
            gender = st.selectbox("Gender", ["Male", "Female"])
            scr = st.number_input("SCr (mg/dL)", 0.1, 5.0, 1.0)
            target = st.slider("Target Css", 5, 100, 15 if selected_drug != "Valproic acid" else 75)
        interval = st.selectbox("Interval (hr)", [4, 6, 8, 12, 24], index=3)

        # Calculations
        ht_in = height / 2.54
        ibw = (50 + 2.3*(ht_in-60)) if gender=="Male" else (45.5 + 2.3*(ht_in-60))
        dosing_weight = weight
        is_obese = weight > (1.2 * ibw)
        s_factor, albumin, vmax, km, extra_info = 0.92, 4.4, 7.0, 4.0, ""

        if selected_drug == "Phenytoin":
            if is_obese: dosing_weight = ibw + 0.4 * (weight - ibw)
            cp1, cp2 = st.columns(2)
            with cp1:
                vmax = st.number_input("Vmax", 1.0, 15.0, 7.0)
                albumin = st.number_input("Albumin", 0.5, 6.0, 4.4)
            with cp2:
                km = st.number_input("Km", 1.0, 10.0, 4.0)
                salt = st.selectbox("Form", ["Sodium (0.92)", "Acid (1.0)"])
            s_factor = 0.92 if "Sodium" in salt else 1.0
            if albumin < 4.4: extra_info = "Albumin correction applied."

        crcl_wt = ibw if is_obese else weight
        crcl = ((140-age)*crcl_wt)/(72*scr) if gender=="Male" else ((140-age)*crcl_wt)/(72*scr)*0.85

        if selected_drug == "Phenytoin":
            vd = 0.7 * dosing_weight; vmax_t = vmax * dosing_weight
            md = ((vmax_t * target) / (km + target)) / (24/interval); ld = target * vd
            k_el = (vmax_t / (km + target)) / vd; css_max = (target / s_factor) + ((md * s_factor) / vd)
            css_min = css_max * math.exp(-k_el * interval); t_half = 0.693 / k_el
        elif selected_drug == "Valproic acid":
            vd, cl = 0.15 * weight, 0.008 * weight
            k = cl/vd; ld, md = target*vd, target*cl*interval; t_half = 0.693/k
        else: # Simplified for other drugs
            vd, cl = 0.6 * weight, (crcl * 0.6) / 1000 * 60
            k = cl/vd; ld, md = target*vd, target*cl*interval; t_half = 0.693/k

    with c_res:
        st.subheader("📊 Analysis Results")
        if st.button("🚀 Run Analysis"):
            st.metric("Estimated CrCl", f"{crcl:.1f} mL/min")
            st.success(f"**Recommended Regimen:** LD {round(ld)} mg then {round(md)} mg q{interval}h")
            pdf_data = create_pdf_report(age, weight, height, selected_drug, crcl, ld, md, interval)
            st.download_button("📥 Save Report", pdf_data, "DoseWise_Report.pdf", "application/pdf")
    st.markdown('</div>', unsafe_allow_html=True)

# ==============================
# 📋 TAB 4: Case Summary (NEW SHIAKA DESIGN)
# ==============================
with tab4:
    st.markdown('<div class="section">', unsafe_allow_html=True)
    
    st.markdown('''
        <div style="text-align:center; padding-bottom:20px;">
            <h2 style="color:#1e3a8a; margin-bottom:5px;">📋 Clinical Case Presentation</h2>
            <p style="color:#64748b;">DoseWise Automated Summary Report</p>
        </div>
    ''', unsafe_allow_html=True)

    # بيانات الحالة في شكل "كروت"
    c1, c2, c3 = st.columns(3)
    c1.info(f"**Patient Profile**\n\n{age}Y / {weight}kg\n\nStatus: {'Obese' if is_obese else 'Normal'}")
    c2.warning(f"**Selected Drug**\n\n{selected_drug}\n\nTarget Css: {target} mg/L")
    c3.success(f"**Final Regimen**\n\nLD: {round(ld)} mg\n\nMD: {round(md)} mg q{interval}h")

    # الجدول الطبي الاحترافي
    table_html = f'''
    <style>
        .res-table {{ width: 100%; border-radius: 12px; overflow: hidden; border: 1px solid #e2e8f0; font-family: sans-serif; margin-top: 20px; }}
        .res-table thead {{ background: #1e3a8a; color: white; text-align: left; }}
        .res-table th, .res-table td {{ padding: 15px; border-bottom: 1px solid #f1f5f9; }}
        .res-table tr:hover {{ background: #f8fafc; }}
        .label {{ font-weight: bold; color: #475569; width: 40%; }}
        .value {{ color: #1e293b; font-weight: 600; }}
    </style>
    <table class="res-table">
        <thead>
            <tr><th colspan="2">📊 Summary Parameters</th></tr>
        </thead>
        <tbody>
            <tr><td class="label">Patient Name</td><td class="value">Case_Ref_{age}Y</td></tr>
            <tr><td class="label">Creatinine Clearance</td><td class="value">{crcl:.1f} mL/min</td></tr>
            <tr><td class="label">Formulation Used</td><td class="value">{'Phenytoin Sodium' if selected_drug=="Phenytoin" and s_factor==0.92 else 'Standard Salt'}</td></tr>
            <tr><td class="label">Calculated LD</td><td class="value" style="color:#10b981;">{round(ld)} mg</td></tr>
            <tr><td class="label">Calculated MD</td><td class="value" style="color:#3b82f6;">{round(md)} mg every {interval}h</td></tr>
        </tbody>
    </table>
    '''
    st.markdown(table_html, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with tab2: st.info(f"Knowledge Base: {selected_drug}")
with tab3: st.warning("Clinical Decision Guidance")

st.markdown("<br><center>💙 **DoseWise** | Clinical PK Project | MNU Faculty of Pharmacy</center>", unsafe_allow_html=True)
