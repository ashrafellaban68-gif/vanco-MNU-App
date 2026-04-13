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
# 🎨 1. Premium Animated UI
# ==============================
def set_page_style():
    st.markdown('''
    <style>
    @keyframes fadeInUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
    .stApp { background-color: #f4f7f9; }
    .hero {
        background: linear-gradient(135deg, #0f172a, #1e3a8a);
        padding: 40px; border-radius: 0 0 40px 40px; text-align: center; color: white;
        margin: -60px -20px 30px -20px; box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        animation: fadeInUp 0.6s ease-out;
    }
    .section {
        background: white; padding: 25px; border-radius: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        border: 1px solid #e2e8f0; margin-bottom: 25px; animation: fadeInUp 0.8s ease-out;
        transition: 0.3s;
    }
    .section:hover { transform: translateY(-5px); box-shadow: 0 12px 25px rgba(0,0,0,0.1); border-color: #3b82f6; }
    .stButton>button {
        background: linear-gradient(45deg, #1e3a8a, #3b82f6); color: white;
        border-radius: 12px; font-weight: 700; border: none; padding: 12px 30px;
    }
    </style>
    ''', unsafe_allow_html=True)

# ==============================
# 📄 2. Professional PDF Generator
# ==============================
def create_pdf_report(age, weight, drug, crcl, ld, md, interval, soap_text):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('TitleStyle', parent=styles['Title'], textColor=colors.hexColor("#1e3a8a"), fontSize=22)
    content = [
        Paragraph("DoseWise: Clinical Pharmacokinetics Report", title_style),
        Spacer(1, 20),
        Paragraph(f"<b>Patient Age:</b> {age}Y | <b>Weight:</b> {weight}kg | <b>Drug:</b> {drug}", styles['Normal']),
        Paragraph(f"<b>Creatinine Clearance:</b> {crcl:.1f} mL/min", styles['Normal']),
        Spacer(1, 20),
        Paragraph(f"<b>Clinical Plan:</b> LD {round(ld)}mg then MD {round(md)}mg every {interval}h", styles['Heading2']),
        Spacer(1, 20),
        Paragraph("<b>Professional SOAP Note:</b>", styles['Heading3']),
        Paragraph(soap_text.replace('\n', '<br/>'), styles['Normal'])
    ]
    doc.build(content)
    return buffer.getvalue()

# ==============================
# ⚙️ 3. App Execution & Advanced Logic
# ==============================
st.set_page_config(page_title="DoseWise Clinical Master", layout="wide")
set_page_style()

st.markdown('<div class="hero"><h1>💊 DoseWise Clinical Master</h1><p>Comprehensive PK Decision Support System</p></div>', unsafe_allow_html=True)

# --- GLOBAL INPUTS (Shared across all tabs) ---
with st.container():
    st.markdown('<div class="section">', unsafe_allow_html=True)
    selected_drug = st.selectbox("💊 Select Medication", ["Phenytoin", "Valproic acid", "Carbamazepine", "Levetiracetam"])
    
    col_pat1, col_pat2 = st.columns(2)
    with col_pat1:
        age = st.number_input("Age (Years)", 1, 100, 30)
        weight = st.number_input("Total Weight (kg)", 10.0, 250.0, 70.0)
        height = st.number_input("Height (cm)", 50, 250, 170)
    with col_pat2:
        gender = st.selectbox("Gender", ["Male", "Female"])
        scr = st.number_input("Serum Creatinine (mg/dL)", 0.1, 5.0, 1.0)
        target = st.slider("Target Steady-State (mg/L)", 5, 100, 15 if selected_drug != "Valproic acid" else 75)
    
    interval = st.selectbox("Interval (hr)", [4, 6, 8, 12, 24], index=3)
    st.markdown('</div>', unsafe_allow_html=True)

# --- SHARED CALCULATIONS ---
ht_in = height / 2.54
ibw = (50 + 2.3*(ht_in-60)) if gender=="Male" else (45.5 + 2.3*(ht_in-60))
is_obese = weight > (1.2 * ibw)
dosing_weight = weight
alb, vmax, km, s_factor = 4.4, 7.0, 4.0, 0.92 # Default values

# Advanced Phenytoin Calculation
if selected_drug == "Phenytoin":
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.subheader("🧬 Phenytoin Specific Parameters")
    if is_obese:
        dosing_weight = ibw + 0.4 * (weight - ibw)
        st.warning(f"Obesity: Using Adjusted Body Weight ({dosing_weight:.1f} kg)")
    cp1, cp2 = st.columns(2)
    with cp1:
        vmax = st.number_input("Vmax (mg/kg/day)", 1.0, 15.0, 7.0)
        alb = st.number_input("Albumin (g/dL)", 0.5, 6.0, 4.4)
    with cp2:
        km = st.number_input("Km (mg/L)", 1.0, 10.0, 4.0)
        salt_form = st.selectbox("Salt Type", ["Sodium (S=0.92)", "Acid (S=1.0)"])
    s_factor = 0.92 if "Sodium" in salt_form else 1.0
    st.markdown('</div>', unsafe_allow_html=True)

# Renal Function
crcl_wt = ibw if is_obese else weight
crcl = ((140-age)*crcl_wt)/(72*scr) if gender=="Male" else ((140-age)*crcl_wt)/(72*scr)*0.85

# Drug-Specific Logic
if selected_drug == "Phenytoin":
    vd = 0.7 * dosing_weight; vmax_t = vmax * dosing_weight
    md = ((vmax_t * target) / (km + target)) / (24/interval); ld = target * vd
    k_el = (vmax_t / (km + target)) / vd; t_half = 0.693 / k_el
    peak = (target/s_factor)+((md*s_factor)/vd); trough = peak * math.exp(-k_el * interval)
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

# ==============================
# 📋 TABS INTERFACE
# ==============================
tab1, tab2, tab3, tab4, tab5 = st.tabs(["🎯 Results", "📚 Drug Monograph", "⚖️ Clinical Decision", "📋 Case Summary", "📝 SOAP Note"])

with tab1:
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.subheader("📊 Primary Outcomes")
    res1, res2, res3 = st.columns(3)
    res1.metric("CrCl (mL/min)", f"{crcl:.1f}")
    res2.metric("Vd (L)", f"{vd:.1f}")
    res3.metric("t½ (h)", f"{t_half:.1f}" if selected_drug != "Phenytoin" else "N/A")
    if selected_drug == "Phenytoin":
        st.info(f"Steady State: Peak {peak:.2f} | Trough {trough:.2f} mg/L")
    st.success(f"**Final Regimen:** LD {round(ld)} mg | MD {round(md)} mg every {interval}h")
    st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.subheader(f"📚 {selected_drug} Monograph")
    db = {"Phenytoin": ["10-20 mg/L", "1000mg/d", "Gingival Hyperplasia, Ataxia"],
          "Valproic acid": ["50-100 mg/L", "60mg/kg/d", "Hepatotoxicity, Hair loss"],
          "Carbamazepine": ["4-12 mg/L", "1600mg/d", "Auto-induction, SJS"],
          "Levetiracetam": ["12-46 mg/L", "3000mg/d", "Behavioral changes"]}
    st.write(f"**Therapeutic Range:** {db[selected_drug][0]}")
    st.write(f"**Maximum Daily Dose:** {db[selected_drug][1]}")
    st.error(f"**Major Side Effects:** {db[selected_drug][2]}")
    st.markdown('</div>', unsafe_allow_html=True)

with tab3:
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.subheader("⚖️ Clinical Decision Support")
    if is_obese: st.error("⚠️ Obesity Detected: Dosing adjusted using ABW.")
    if crcl < 50: st.warning("⚠️ Renal Impairment: Maintenance dose adjusted.")
    if selected_drug == "Phenytoin" and alb < 4.4:
        st.info(f"💡 Low Albumin: Adjusted target Css for phenytoin is {target/((0.2*alb)+0.1):.1f} mg/L.")
    st.write("**Clinical Note:** Ensure serum monitoring after 5 half-lives.")
    st.markdown('</div>', unsafe_allow_html=True)

with tab4:
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.subheader("📋 Case Summary Table")
    st.table({"Parameter": ["Age", "Weight", "IBW", "CrCl", "Regimen"], 
              "Value": [f"{age}Y", f"{weight}kg", f"{ibw:.1f}kg", f"{crcl:.1f}mL/min", f"{round(md)}mg q{interval}h"]})
    st.markdown('</div>', unsafe_allow_html=True)

with tab5:
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.subheader("📝 Clinical SOAP Note")
    soap_txt = f"S: {age}Y {gender} patient. Weight {weight}kg.\nO: SCr {scr}mg/dL, CrCl {crcl:.1f}mL/min. IBW {ibw:.1f}kg.\nA: Patient requires individualized {selected_drug} dose due to {'obesity' if is_obese else 'body weight'}.\nP: Administer LD {round(ld)}mg, then MD {round(md)}mg q{interval}h. Monitor for {db[selected_drug][2].split(',')[0]}."
    
    st.markdown(f'<div style="background:#f0f4f8; padding:20px; border-radius:10px; border-left:10px solid #0f172a;">{soap_txt.replace("\n", "<br><br>")}</div>', unsafe_allow_html=True)
    
    pdf_btn = create_pdf_report(age, weight, selected_drug, crcl, ld, md, interval, soap_txt)
    st.download_button("📥 Download Official Clinical Report", pdf_btn, f"DoseWise_Report_{selected_drug}.pdf", "application/pdf")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<center style='color:#64748b;'>DoseWise Clinical Pro v5.0 | MNU Faculty of Pharmacy</center>", unsafe_allow_html=True)
