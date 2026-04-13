import streamlit as st
import math
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from io import BytesIO

# ==============================
# 🎨 1. Premium Medical UI & Animations
# ==============================
def set_page_style():
    st.markdown('''
    <style>
    @keyframes fadeInUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
    .stApp { background-color: #f8fafc; }
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
    .section:hover { transform: translateY(-5px); border-color: #3b82f6; box-shadow: 0 12px 25px rgba(0,0,0,0.1); }
    .stButton>button {
        background: linear-gradient(45deg, #1e3a8a, #3b82f6); color: white;
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
    title_style = ParagraphStyle('TitleStyle', parent=styles['Title'], textColor=colors.hexColor("#1e3a8a"), fontSize=22)
    content = [
        Paragraph("DoseWise: Clinical Pharmacokinetics Report", title_style),
        Spacer(1, 20),
        Paragraph(f"<b>Patient Age:</b> {age}Y | <b>Weight:</b> {weight}kg | <b>Drug:</b> {drug}", styles['Normal']),
        Paragraph(f"<b>CrCl:</b> {crcl:.1f} mL/min", styles['Normal']),
        Spacer(1, 20),
        Paragraph(f"<b>Final Clinical Plan:</b> LD {round(ld)}mg | MD {round(md)}mg every {interval}h", styles['Heading2']),
        Spacer(1, 20),
        Paragraph("<b>Professional SOAP Note:</b>", styles['Heading3']),
        Paragraph(soap_text.replace('\n', '<br/>'), styles['Normal'])
    ]
    doc.build(content)
    return buffer.getvalue()

# ==============================
# ⚙️ 3. App Construction
# ==============================
st.set_page_config(page_title="DoseWise Clinical Pro", layout="wide")
set_page_style()

st.markdown('<div class="hero"><h1>💊 DoseWise Clinical Master</h1><p>Comprehensive Decision Support System</p></div>', unsafe_allow_html=True)

# التبويبات الخمسة كاملة
tab1, tab2, tab3, tab4, tab5 = st.tabs(["🎯 Calculator", "📚 Drug Monograph", "⚖️ Clinical Decision", "📋 Case Summary", "📝 SOAP Note"])

# --- TAB 1: CALCULATOR ---
with tab1:
    st.markdown('<div class="section">', unsafe_allow_html=True)
    selected_drug = st.selectbox("💊 Select Medication", ["Phenytoin", "Valproic acid", "Carbamazepine", "Levetiracetam"])
    
    col_pat1, col_pat2 = st.columns(2)
    with col_pat1:
        age = st.number_input("Age (Years)", 1, 100, 30)
        weight = st.number_input("Total Weight (kg)", 10.0, 250.0, 70.0)
        height = st.number_input("Height (cm)", 50, 250, 170)
    with col_pat2:
        gender = st.selectbox("Gender", ["Male", "Female"])
        scr = st.number_input("SCr (mg/dL)", 0.1, 5.0, 1.0)
        target = st.slider("Target Css (mg/L)", 5, 100, 15 if selected_drug != "Valproic acid" else 75)
    
    interval = st.selectbox("Interval (hr)", [4, 6, 8, 12, 24], index=3)
    
    # Advanced Parameters
    alb, vmax, km, s_factor = 4.4, 7.0, 4.0, 0.92
    if selected_drug == "Phenytoin":
        st.markdown("---")
        st.subheader("🧬 Phenytoin Specific Parameters")
        cp1, cp2 = st.columns(2)
        with cp1:
            vmax = st.number_input("Vmax (mg/kg/d)", 1.0, 15.0, 7.0)
            alb = st.number_input("Albumin (g/dL)", 0.5, 6.0, 4.4)
        with cp2:
            km = st.number_input("Km (mg/L)", 1.0, 10.0, 4.0)
            salt_form = st.selectbox("Salt Form", ["Sodium (0.92)", "Acid (1.0)"])
        s_factor = 0.92 if "Sodium" in salt_form else 1.0
    st.markdown('</div>', unsafe_allow_html=True)

    # الحسابات (Global Calculation)
    ht_in = height / 2.54; ibw = (50 + 2.3*(ht_in-60)) if gender=="Male" else (45.5 + 2.3*(ht_in-60))
    is_obese = weight > (1.2 * ibw)
    d_wt = (ibw + 0.4 * (weight - ibw)) if (is_obese and selected_drug == "Phenytoin") else weight
    crcl_wt = ibw if is_obese else weight
    crcl = ((140-age)*crcl_wt)/(72*scr) if gender=="Male" else ((140-age)*crcl_wt)/(72*scr)*0.85

    if selected_drug == "Phenytoin":
        vd = 0.7 * d_wt; vmax_t = vmax * d_wt
        md = ((vmax_t * target) / (km + target)) / (24/interval); ld = target * vd
        k_el = (vmax_t / (km + target)) / vd; t_h = 0.693 / k_el
        peak = (target/s_factor)+((md*s_factor)/vd); trough = peak * math.exp(-k_el * interval)
    elif selected_drug == "Valproic acid":
        vd, cl = 0.15 * weight, 0.008 * weight; k = cl/vd; ld, md = target*vd, target*cl*interval; t_h = 0.693/k
    elif selected_drug == "Carbamazepine":
        vd, cl = 1.4 * weight, 0.06 * weight; k = cl/vd; ld, md = target*vd, target*cl*interval; t_h = 0.693/k
    else: # Levetiracetam
        vd = 0.6 * weight; cl = (crcl * 0.6) / 1000 * 60; k = cl/vd; ld, md = target*vd, target*cl*interval; t_h = 0.693/k
    
    if selected_drug != "Phenytoin" and crcl < 50: md *= (crcl/100)

    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.subheader("📊 Output Results")
    if st.button("🚀 Calculate Regimen"):
        st.balloons()
        r1, r2, r3 = st.columns(3)
        r1.metric("CrCl", f"{crcl:.1f}")
        r2.metric("Vd (L)", f"{vd:.1f}")
        r3.metric("t½ (h)", f"{t_h:.1f}" if selected_drug != "Phenytoin" else "N/A")
        if selected_drug == "Phenytoin": st.info(f"Steady State: Peak {peak:.1f} | Trough {trough:.1f}")
        st.success(f"Final Regimen: LD {round(ld)}mg | MD {round(md)}mg q{interval}h")
    st.markdown('</div>', unsafe_allow_html=True)

# --- TAB 2: MONOGRAPH ---
with tab2:
    st.markdown('<div class="section">', unsafe_allow_html=True)
    drug_db = {"Phenytoin": ["10-20 mg/L", "1000mg/d", "Gingival Hyperplasia"], "Valproic acid": ["50-100 mg/L", "60mg/kg/d", "Hepatotoxicity"], "Carbamazepine": ["4-12 mg/L", "1600mg/d", "SJS, Hyponatremia"], "Levetiracetam": ["12-46 mg/L", "3000mg/d", "Behavioral changes"]}
    st.subheader(f"💊 {selected_drug} Profile")
    st.write(f"**Target Range:** {drug_db[selected_drug][0]}")
    st.write(f"**Max Dose:** {drug_db[selected_drug][1]}")
    st.error(f"**Side Effects:** {drug_db[selected_drug][2]}")
    st.markdown('</div>', unsafe_allow_html=True)

# --- TAB 3: CLINICAL DECISION ---
with tab3:
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.subheader("⚖️ Clinical Decision Analysis")
    if is_obese: st.error(f"❗ Obesity: ABW logic applied ({d_wt:.1f} kg).")
    if crcl < 50: st.warning(f"⚠️ Renal Impairment: Dose reduced for CrCl {crcl:.1f}.")
    if selected_drug == "Phenytoin" and alb < 4.4:
        st.info(f"💡 Low Albumin: Corrected target Css: {target/((0.2*alb)+0.1):.1f} mg/L.")
    st.write("Recommendation: Start therapy and monitor clinical response.")
    st.markdown('</div>', unsafe_allow_html=True)

# --- TAB 4: CASE SUMMARY ---
with tab4:
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.subheader("📋 Final Case Summary")
    st.table({"Parameter": ["Age", "Weight", "IBW", "CrCl", "Regimen"], "Value": [f"{age}Y", f"{weight}kg", f"{ibw:.1f}kg", f"{crcl:.1f}mL/min", f"{round(md)}mg q{interval}h"]})
    st.markdown('</div>', unsafe_allow_html=True)

# --- TAB 5: SOAP NOTE & PRINT ---
with tab5:
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.subheader("📝 Professional SOAP Note")
    soap_note = f"S: {age}Y patient on {selected_drug}.\nO: Weight {weight}kg, SCr {scr}mg/dL, CrCl {crcl:.1f}mL/min.\nA: Dose optimized for PK parameters.\nP: LD {round(ld)}mg, MD {round(md)}mg q{interval}h."
    st.markdown(f'<div style="background:#f0f9ff; padding:20px; border-radius:10px; border-left:8px solid #0f172a;">{soap_note.replace("\n", "<br><br>")}</div>', unsafe_allow_html=True)
    
    pdf_file = create_pdf_report(age, weight, selected_drug, crcl, ld, md, interval, soap_note)
    st.download_button("📥 Download Official Clinical Report", pdf_file, f"DoseWise_{selected_drug}.pdf", "application/pdf")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<center style='color:#64748b;'>DoseWise Clinical Master v8.0 | MNU Faculty of Pharmacy</center>", unsafe_allow_html=True)
