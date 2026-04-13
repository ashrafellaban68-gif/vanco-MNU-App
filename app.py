import streamlit as st
import os
import base64
import math
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from io import BytesIO

# ==============================
# 🎨 1. Professional Medical UI & Transitions
# ==============================
def set_page_style():
    st.markdown('''
    <style>
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .stApp { background-color: #f8fafc; }
    .hero {
        background: linear-gradient(135deg, #0f172a, #1e293b);
        padding: 40px; border-radius: 0 0 40px 40px; text-align: center; color: white;
        margin: -60px -20px 30px -20px; box-shadow: 0 10px 30px rgba(0,0,0,0.15);
        animation: fadeInUp 0.6s ease-out;
    }
    .section {
        background: white; padding: 25px; border-radius: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        border: 1px solid #e2e8f0; margin-bottom: 25px; animation: fadeInUp 0.8s ease-out;
        transition: all 0.3s ease-in-out;
    }
    .section:hover {
        transform: translateY(-5px); box-shadow: 0 12px 24px rgba(0,0,0,0.1); border-color: #3b82f6;
    }
    .stButton>button {
        background: linear-gradient(45deg, #1e293b, #3b82f6); color: white;
        border-radius: 12px; font-weight: 700; border: none; padding: 12px 30px;
    }
    </style>
    ''', unsafe_allow_html=True)

# ==============================
# 📄 2. Fixed PDF Report Generator
# ==============================
def create_pdf_report(age, weight, drug, crcl, ld, md, interval, soap_text):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('TitleStyle', parent=styles['Title'], textColor=colors.hexColor("#1e293b"), fontSize=22)
    content = [
        Paragraph("DoseWise: Clinical Pharmacokinetics Report", title_style),
        Spacer(1, 20),
        Paragraph(f"<b>Patient:</b> {age}Y | {weight}kg | <b>Drug:</b> {drug}", styles['Normal']),
        Paragraph(f"<b>CrCl:</b> {crcl:.1f} mL/min", styles['Normal']),
        Spacer(1, 25),
        Paragraph("<b>Final Clinical Regimen:</b>", styles['Heading2']),
        Paragraph(f"LD: {round(ld)} mg | MD: {round(md)} mg q{interval}h", styles['Normal']),
        Spacer(1, 25),
        Paragraph("<b>SOAP Clinical Note:</b>", styles['Heading3']),
        Paragraph(soap_text.replace('\n', '<br/>'), styles['Normal'])
    ]
    doc.build(content)
    return buffer.getvalue()

# ==============================
# ⚙️ 3. Execution (Shared Logic)
# ==============================
st.set_page_config(page_title="DoseWise Clinical Master", layout="wide")
set_page_style()

st.markdown('<div class="hero"><h1>💊 DoseWise Clinical Master</h1><p>Integrated PK Decision Support & SOAP Documentation</p></div>', unsafe_allow_html=True)

# --- A. Shared Input UI (Outside Tabs to prevent errors) ---
with st.container():
    st.markdown('<div class="section">', unsafe_allow_html=True)
    selected_drug = st.selectbox("Choose Medication", ["Phenytoin", "Valproic acid", "Carbamazepine", "Levetiracetam"])
    c1, c2 = st.columns(2)
    with c1:
        age = st.number_input("Age (Years)", 1, 100, 30)
        weight = st.number_input("Actual Weight (kg)", 10.0, 250.0, 70.0)
        height = st.number_input("Height (cm)", 50, 250, 170)
    with c2:
        gender = st.selectbox("Gender", ["Male", "Female"])
        scr = st.number_input("Serum Creatinine (mg/dL)", 0.1, 5.0, 1.0)
        target = st.slider("Target Steady-State Css (mg/L)", 5, 100, 15)
    interval = st.selectbox("Dosing Interval (hr)", [4, 6, 8, 12, 24], index=3)
    
    # Advanced Params
    s_factor, alb, vmax, km = 0.92, 4.4, 7.0, 4.0
    if selected_drug == "Phenytoin":
        st.markdown("---")
        cp1, cp2 = st.columns(2)
        with cp1:
            vmax = st.number_input("Vmax (mg/kg/d)", 1.0, 15.0, 7.0)
            alb = st.number_input("Albumin (g/dL)", 0.5, 6.0, 4.4)
        with cp2:
            km = st.number_input("Km (mg/L)", 1.0, 10.0, 4.0)
            salt = st.selectbox("Salt Form", ["Sodium (S=0.92)", "Acid (S=1.0)"])
        s_factor = 0.92 if "Sodium" in salt else 1.0
    st.markdown('</div>', unsafe_allow_html=True)

# --- B. Shared Global Calculations (Crucial for fixing errors) ---
ht_in = height / 2.54
ibw = (50 + 2.3*(ht_in-60)) if gender=="Male" else (45.5 + 2.3*(ht_in-60))
is_obese = weight > (1.2 * ibw)
dosing_weight = (ibw + 0.4 * (weight - ibw)) if (is_obese and selected_drug == "Phenytoin") else weight
crcl_wt = ibw if is_obese else weight
crcl = ((140-age)*crcl_wt)/(72*scr) if gender=="Male" else ((140-age)*crcl_wt)/(72*scr)*0.85

if selected_drug == "Phenytoin":
    vd = 0.7 * dosing_weight; vmax_t = vmax * dosing_weight
    md = ((vmax_t * target) / (km + target)) / (24/interval); ld = target * vd
    k_el = (vmax_t / (km + target)) / vd; t_half = 0.693 / k_el
    peak = (target/s_factor)+((md*s_factor)/vd); trough = peak * math.exp(-k_el * interval)
else:
    vd = 0.6 * weight; cl = (crcl * 0.6) / 1000 * 60; k = cl/vd; ld, md = target*vd, target*cl*interval; t_half = 0.693/k

if selected_drug != "Phenytoin" and crcl < 50: md *= (crcl/100)

# --- C. Tabs Interface (Display only) ---
tab1, tab2, tab3, tab4, tab5 = st.tabs(["🎯 Calculator", "📚 Drug Knowledge", "⚖️ Clinical Decision", "📋 Case Summary", "📝 SOAP Note"])

with tab1:
    st.markdown('<div class="section">', unsafe_allow_html=True)
    col_res1, col_res2 = st.columns([1, 1])
    with col_res1:
        st.subheader("📊 Primary Metrics")
        st.metric("CrCl", f"{crcl:.1f} mL/min")
        st.metric("Vd (L)", f"{vd:.1f}")
    with col_res2:
        st.subheader("⚡ Result Plan")
        if selected_drug == "Phenytoin": st.info(f"Steady State: Peak {peak:.1f} | Trough {trough:.1f}")
        st.success(f"Final Regimen: LD {round(ld)}mg | MD {round(md)}mg q{interval}h")
    st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    st.markdown('<div class="section">', unsafe_allow_html=True)
    drugs_info = {"Phenytoin": "10-20 mg/L. SE: Gingival hyperplasia.", "Valproic acid": "50-100 mg/L. SE: Weight gain.", "Carbamazepine": "4-12 mg/L. SE: Autoinduction.", "Levetiracetam": "12-46 mg/L. SE: Irritability."}
    st.info(drugs_info[selected_drug])
    st.markdown('</div>', unsafe_allow_html=True)

with tab3:
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.subheader("⚖️ Clinical Decision Analysis")
    if is_obese: st.error(f"❗ Obesity: Using ABW ({dosing_weight:.1f} kg).")
    if crcl < 50: st.warning(f"⚠️ Renal: MD adjusted for CrCl {crcl:.1f}.")
    if selected_drug == "Phenytoin" and alb < 4.4: st.info(f"💡 Low Albumin: Adjusted target is {target/((0.2*alb)+0.1):.1f} mg/L.")
    st.markdown('</div>', unsafe_allow_html=True)

with tab4:
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.subheader("📋 Final Case Summary")
    st.table({"Parameter": ["Age", "Weight", "CrCl", "Drug", "Regimen"], "Value": [f"{age}Y", f"{weight}kg", f"{crcl:.1f}mL/min", selected_drug, f"{round(md)}mg q{interval}h"]})
    st.markdown('</div>', unsafe_allow_html=True)

with tab5:
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.subheader("📝 Professional SOAP Note")
    soap_txt = f"S: {age}Y patient on {selected_drug}.\nO: Weight {weight}kg, CrCl {crcl:.1f}mL/min.\nA: Regimen optimized for PK parameters.\nP: LD {round(ld)}mg, MD {round(md)}mg q{interval}h."
    st.markdown(f'<div style="background:#f0f9ff; padding:20px; border-radius:10px; border-left:8px solid #0f172a;">{soap_txt.replace("\n", "<br><br>")}</div>', unsafe_allow_html=True)
    pdf_data = create_pdf_report(age, weight, selected_drug, crcl, ld, md, interval, soap_txt)
    st.download_button("📥 Download Report PDF", pdf_data, f"DoseWise_{selected_drug}.pdf", "application/pdf")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<center style='color:#94a3b8;'>DoseWise Clinical Master v3.1 | 2024</center>", unsafe_allow_html=True)
