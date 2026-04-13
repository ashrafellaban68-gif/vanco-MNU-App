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
    /* Professional Fade & Slide Animation */
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .stApp {
        background-color: #f8fafc;
    }

    /* Hero Section */
    .hero {
        background: linear-gradient(135deg, #0f172a, #1e293b);
        padding: 40px;
        border-radius: 0 0 40px 40px;
        text-align: center;
        color: white;
        margin: -60px -20px 30px -20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.15);
        animation: fadeInUp 0.6s ease-out;
    }

    /* Card Styling with Transitions */
    .section {
        background: white;
        padding: 25px;
        border-radius: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        border: 1px solid #e2e8f0;
        margin-bottom: 25px;
        animation: fadeInUp 0.8s ease-out;
        transition: all 0.3s ease-in-out;
    }
    .section:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 24px rgba(0,0,0,0.1);
        border-color: #3b82f6;
    }

    /* Medical Button Styling */
    .stButton>button {
        background: linear-gradient(45deg, #1e293b, #3b82f6);
        color: white;
        border-radius: 12px;
        font-weight: 700;
        border: none;
        padding: 12px 30px;
        transition: all 0.4s ease;
    }
    .stButton>button:hover {
        background: linear-gradient(45deg, #3b82f6, #1e293b);
        box-shadow: 0 8px 20px rgba(59, 130, 246, 0.3);
    }
    
    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #edf2f7;
        border-radius: 10px 10px 0 0;
        padding: 10px 20px;
    }
    </style>
    ''', unsafe_allow_html=True)

# ==============================
# 📄 2. Fixed PDF Report Generator
# ==============================
def create_pdf_report(age, weight, drug, crcl, ld, md, interval, soap_text, analysis):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    
    # Custom Styles
    title_style = ParagraphStyle('TitleStyle', parent=styles['Title'], textColor=colors.hexColor("#1e293b"), fontSize=22)
    
    content = []
    content.append(Paragraph("DoseWise: Clinical Pharmacokinetics Report", title_style))
    content.append(Spacer(1, 20))
    
    # Patient Data Table
    data = [
        ["Patient Age", f"{age} Years", "Current Drug", drug],
        ["Total Weight", f"{weight} kg", "CrCl", f"{crcl:.1f} mL/min"]
    ]
    t = Table(data, colWidths=[100, 150, 100, 150])
    t.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), colors.whitesmoke), ('GRID', (0,0), (-1,-1), 0.5, colors.grey)]))
    content.append(t)
    
    content.append(Spacer(1, 25))
    content.append(Paragraph(f"<b>Final Clinical Regimen:</b>", styles['Heading2']))
    content.append(Paragraph(f"Loading Dose: {round(ld)} mg (Once)", styles['Normal']))
    content.append(Paragraph(f"Maintenance Dose: {round(md)} mg every {interval} hours", styles['Normal']))
    
    content.append(Spacer(1, 25))
    content.append(Paragraph("<b>SOAP Clinical Note:</b>", styles['Heading3']))
    content.append(Paragraph(soap_text.replace('\n', '<br/>'), styles['Normal']))
    
    doc.build(content)
    return buffer.getvalue()

# ==============================
# ⚙️ 3. Main Application Logic
# ==============================
st.set_page_config(page_title="DoseWise Clinical Master", layout="wide")
set_page_style()

st.markdown('<div class="hero"><h1>💊 DoseWise Clinical Master</h1><p>Integrated PK Decision Support & SOAP Documentation</p></div>', unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5 = st.tabs(["🎯 Calculator", "📚 Drug Knowledge", "⚖️ Clinical Decision", "📋 Case Summary", "📝 SOAP Note"])

with tab1:
    st.markdown('<div class="section">', unsafe_allow_html=True)
    selected_drug = st.selectbox("Choose Medication", ["Phenytoin", "Valproic acid", "Carbamazepine", "Levetiracetam"])
    col_in, col_res = st.columns([1.3, 1])
    
    with col_in:
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

        # Advanced PK Calculation Logic
        ht_in = height / 2.54
        ibw = (50 + 2.3*(ht_in-60)) if gender=="Male" else (45.5 + 2.3*(ht_in-60))
        dosing_weight = weight
        is_obese = weight > (1.2 * ibw)
        
        s_factor, alb, vmax, km = 0.92, 4.4, 7.0, 4.0

        if selected_drug == "Phenytoin":
            st.markdown("---")
            if is_obese: dosing_weight = ibw + 0.4 * (weight - ibw)
            cp1, cp2 = st.columns(2)
            with cp1:
                vmax = st.number_input("Vmax (mg/kg/d)", 1.0, 15.0, 7.0)
                alb = st.number_input("Albumin (g/dL)", 0.5, 6.0, 4.4)
            with cp2:
                km = st.number_input("Km (mg/L)", 1.0, 10.0, 4.0)
                salt = st.selectbox("Salt Form", ["Sodium (S=0.92)", "Acid (S=1.0)"])
            s_factor = 0.92 if "Sodium" in salt else 1.0

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
    
    with col_res:
        st.markdown('<div style="background: #f1f5f9; padding: 20px; border-radius: 15px; border: 1px dashed #cbd5e1;">', unsafe_allow_html=True)
        st.subheader("📊 Output Metrics")
        if st.button("🚀 Calculate PK Regimen"):
            st.metric("CrCl (Cockcroft-Gault)", f"{crcl:.1f} mL/min")
            st.metric("Volume of Distribution", f"{vd:.1f} Liters")
            if selected_drug == "Phenytoin": st.info(f"Steady State: Peak {peak:.1f} | Trough {trough:.1f}")
            st.success(f"Recommended Plan:\n\n{round(md)} mg q{interval}h")
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- TAB 3: Clinical Decision (The Content You Wanted) ---
with tab3:
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.subheader("⚖️ Clinical Decision Support Analysis")
    if is_obese:
        st.error(f"❗ **Dosing Weight Alert:** Patient is obese. Dosing weight adjusted from {weight}kg to ABW {dosing_weight:.1f}kg to avoid toxicity.")
    if crcl < 50:
        st.warning(f"⚠️ **Renal Impairment:** CrCl is {crcl:.1f} mL/min. Caution advised; maintenance dose reduced to prevent accumulation.")
    if selected_drug == "Phenytoin" and alb < 4.4:
        adj_target = target / ((0.2 * alb) + 0.1)
        st.info(f"💡 **Albumin Correction:** Low albumin detected ({alb}g/dL). Adjusted target for therapy is {adj_target:.1f} mg/L.")
    st.write("**Pharmacist Note:** Target Css is within therapeutic window. Loading dose recommended for immediate seizure control.")
    st.markdown('</div>', unsafe_allow_html=True)

# --- TAB 5: SOAP Note & PRINTING (Everything Together) ---
with tab5:
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.subheader("📝 Professional SOAP Documentation")
    
    soap_txt = f"S: {age}Y {gender} patient. Target Css: {target}mg/L.\nO: Weight {weight}kg, SCr {scr}mg/dL, CrCl {crcl:.1f}mL/min. IBW: {ibw:.1f}kg.\nA: Regimen optimized for {selected_drug} considering {'obesity' if is_obese else 'normal weight'}.\nP: Start LD {round(ld)}mg once. Follow with MD {round(md)}mg q{interval}h. Monitor levels."
    
    st.markdown(f'''<div style="background: #f0f9ff; padding: 20px; border-radius: 12px; border-left: 8px solid #0f172a; font-family: monospace;">
        {soap_txt.replace('\n', '<br><br>')}</div>''', unsafe_allow_html=True)
    
    # --- PRINT BUTTON (Fixed) ---
    st.markdown("---")
    pdf_data = create_pdf_report(age, weight, selected_drug, crcl, ld, md, interval, soap_txt, "")
    st.download_button(label="📥 Download Clinical PDF Report", data=pdf_data, file_name=f"DoseWise_Report_{selected_drug}.pdf", mime="application/pdf")
    st.markdown('</div>', unsafe_allow_html=True)

with tab4:
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.subheader("📋 Final Case Summary")
    st.table({"Parameter": ["Age", "Weight", "IBW", "CrCl", "Drug", "Vd"], 
              "Value": [f"{age}Y", f"{weight}kg", f"{ibw:.1f}kg", f"{crcl:.1f}mL/min", selected_drug, f"{vd:.1f}L"]})
    st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    st.markdown('<div class="section">', unsafe_allow_html=True)
    drugs_info = {
        "Phenytoin": "Therapeutic Range: 10-20 mg/L. SE: Gingival hyperplasia, Nystagmus.",
        "Valproic acid": "Therapeutic Range: 50-100 mg/L. SE: Weight gain, Hepatotoxicity.",
        "Carbamazepine": "Therapeutic Range: 4-12 mg/L. SE: Autoinduction, Hyponatremia.",
        "Levetiracetam": "Therapeutic Range: 12-46 mg/L. SE: Behavioral changes, Renal clearance."
    }
    st.info(drugs_info[selected_drug])
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<center style='color:#94a3b8;'>DoseWise Clinical Master v3.0 | 2024</center>", unsafe_allow_html=True)
