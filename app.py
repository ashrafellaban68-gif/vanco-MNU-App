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
# 🎨 1. Premium Medical UI & Professional Animations
# ==============================
def set_page_style():
    st.markdown('''
    <style>
    /* Professional Fade-in Animation */
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .stApp { background-color: #f8fafc; }

    /* Hero Section */
    .hero {
        background: linear-gradient(135deg, #0f172a, #1e3a8a);
        padding: 40px; border-radius: 0 0 45px 45px;
        text-align: center; color: white;
        margin: -60px -20px 30px -20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        animation: fadeInUp 0.8s ease-out;
    }

    /* Cards with Smooth Transition */
    .section {
        background: white; padding: 25px; border-radius: 20px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.05);
        border: 1px solid #e2e8f0; margin-bottom: 25px;
        animation: fadeInUp 1s ease-out;
        transition: all 0.3s ease;
    }
    .section:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 30px rgba(0,0,0,0.1);
        border-color: #3b82f6;
    }

    /* Professional Medical Buttons */
    .stButton>button {
        background: linear-gradient(45deg, #1e3a8a, #3b82f6);
        color: white; border-radius: 12px;
        font-weight: 700; border: none; padding: 12px 30px;
        transition: 0.3s;
    }
    </style>
    ''', unsafe_allow_html=True)

# ==============================
# 📄 2. Fixed PDF Report Generator (Error Correction)
# ==============================
def create_pdf_report(age, weight, drug, crcl, ld, md, interval, soap_text):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    
    # تصحيح تعريف الـ ParagraphStyle لتجنب الـ AttributeError
    header_style = styles["Heading1"]
    header_style.textColor = colors.hexColor("#1e3a8a")
    
    content = []
    content.append(Paragraph("DoseWise: Clinical PK Report", header_style))
    content.append(Spacer(1, 20))
    
    # Patient Summary Table
    data = [
        ["Age", f"{age} Y", "Drug", drug],
        ["Weight", f"{weight} kg", "CrCl", f"{crcl:.1f} mL/min"]
    ]
    t = Table(data, colWidths=[80, 150, 80, 150])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.whitesmoke),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold')
    ]))
    content.append(t)
    
    content.append(Spacer(1, 25))
    content.append(Paragraph("<b>Calculated Regimen:</b>", styles["Heading2"]))
    content.append(Paragraph(f"Loading Dose: {round(ld)} mg (Once)", styles["Normal"]))
    content.append(Paragraph(f"Maintenance Dose: {round(md)} mg every {interval} hours", styles["Normal"]))
    
    content.append(Spacer(1, 25))
    content.append(Paragraph("<b>Clinical SOAP Note:</b>", styles["Heading3"]))
    content.append(Paragraph(soap_text.replace('\n', '<br/>'), styles["Normal"]))
    
    doc.build(content)
    return buffer.getvalue()

# ==============================
# ⚙️ 3. Main Application Logic
# ==============================
st.set_page_config(page_title="DoseWise Clinical Pro", layout="wide")
set_page_style()

st.markdown('<div class="hero"><h1>💊 DoseWise Clinical Pro</h1><p>Integrated Pharmacokinetics Decision Support</p></div>', unsafe_allow_html=True)

# التبويبات الخمسة
tab1, tab2, tab3, tab4, tab5 = st.tabs(["🎯 Calculator", "📚 Drug Monograph", "⚖️ Clinical Decision", "📋 Case Summary", "📝 SOAP Note"])

with tab1:
    st.markdown('<div class="section">', unsafe_allow_html=True)
    selected_drug = st.selectbox("💊 Choose Medication", ["Phenytoin", "Valproic acid", "Carbamazepine", "Levetiracetam"])
    
    c_i1, c_i2 = st.columns(2)
    with c_i1:
        age = st.number_input("Age (Years)", 1, 100, 30)
        weight = st.number_input("Total Weight (kg)", 10.0, 250.0, 70.0)
        height = st.number_input("Height (cm)", 50, 250, 170)
    with c_i2:
        gender = st.selectbox("Gender", ["Male", "Female"])
        scr = st.number_input("SCr (mg/dL)", 0.1, 5.0, 1.0)
        target = st.slider("Target Css (mg/L)", 5, 100, 15 if selected_drug != "Valproic acid" else 75)
    
    interval = st.selectbox("Interval (hr)", [4, 6, 8, 12, 24], index=3)

    # --- Calculations Logic (Full Data) ---
    ht_in = height / 2.54; ibw = (50 + 2.3*(ht_in-60)) if gender=="Male" else (45.5 + 2.3*(ht_in-60))
    is_obese = weight > (1.2 * ibw)
    d_wt = weight; s_f, alb, vmax, km = 0.92, 4.4, 7.0, 4.0

    if selected_drug == "Phenytoin":
        st.markdown("---")
        st.subheader("🧬 Advanced Phenytoin Parameters")
        if is_obese:
            d_wt = ibw + 0.4 * (weight - ibw)
            st.warning(f"Obesity Detected: Using ABW ({d_wt:.1f} kg)")
        cp1, cp2 = st.columns(2)
        with cp1:
            vmax = st.number_input("Vmax (mg/kg/day)", 1.0, 15.0, 7.0)
            alb = st.number_input("Albumin (g/dL)", 0.5, 6.0, 4.4)
        with cp2:
            km = st.number_input("Km (mg/L)", 1.0, 10.0, 4.0)
            salt_form = st.selectbox("Salt Form", ["Sodium (S=0.92)", "Acid (S=1.0)"])
        s_f = 0.92 if "Sodium" in salt_form else 1.0

    crcl_wt = ibw if is_obese else weight
    crcl = ((140-age)*crcl_wt)/(72*scr) if gender=="Male" else ((140-age)*crcl_wt)/(72*scr)*0.85

    if selected_drug == "Phenytoin":
        vd = 0.7 * d_wt; vmax_total = vmax * d_wt
        md = ((vmax_total * target) / (km + target)) / (24/interval); ld = target * vd
        k_el = (vmax_total / (km + target)) / vd; t_half = 0.693 / k_el
        peak = (target/s_f)+((md*s_f)/vd); trough = peak * math.exp(-k_el * interval)
    elif selected_drug == "Valproic acid":
        vd, cl = 0.15 * weight, 0.008 * weight; k = cl/vd; ld, md = target*vd, target*cl*interval; t_half = 0.693/k
    elif selected_drug == "Carbamazepine":
        vd, cl = 1.4 * weight, 0.06 * weight; k = cl/vd; ld, md = target*vd, target*cl*interval; t_half = 0.693/k
    else: # Levetiracetam
        vd = 0.6 * weight; cl = (crcl * 0.6) / 1000 * 60; k = cl/vd; ld, md = target*vd, target*cl*interval; t_half = 0.693/k

    if selected_drug != "Phenytoin" and crcl < 50: md *= (crcl/100)
    
    if st.button("🚀 Calculate Final Regimen"):
        # تم مسح st.balloons()
        st.markdown("---")
        res1, res2, res3 = st.columns(3)
        res1.metric("CrCl (mL/min)", f"{crcl:.1f}")
        res2.metric("Vd (L)", f"{vd:.1f}")
        res3.metric("t½ (h)", f"{t_half:.1f}" if selected_drug != "Phenytoin" else "N/A")
        if selected_drug == "Phenytoin":
            st.info(f"Steady State Profile: Peak {peak:.2f} mg/L | Trough {trough:.2f} mg/L")
        st.success(f"Recommended Regimen: LD {round(ld)} mg | MD {round(md)} mg every {interval} hours")
    st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    st.markdown('<div class="section">', unsafe_allow_html=True)
    drug_db = {"Phenytoin": ["10-20 mg/L", "1000 mg/day", "Gingival hyperplasia, Ataxia"], "Valproic acid": ["50-100 mg/L", "60 mg/kg/day", "Hepatotoxicity, Weight gain"], "Carbamazepine": ["4-12 mg/L", "1600 mg/day", "Auto-induction, SJS"], "Levetiracetam": ["12-46 mg/L", "3000 mg/day", "Behavioral changes"]}
    st.subheader(f"📚 {selected_drug} Monograph")
    st.write(f"**Therapeutic Window:** {drug_db[selected_drug][0]}")
    st.write(f"**Max Dose:** {drug_db[selected_drug][1]}")
    st.error(f"**Side Effects:** {drug_db[selected_drug][2]}")
    st.markdown('</div>', unsafe_allow_html=True)

with tab3:
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.subheader("⚖️ Clinical Decision Support")
    if is_obese: st.error(f"❗ **Obesity:** ABW used ({d_wt:.1f} kg) for dosing.")
    if crcl < 50: st.warning(f"⚠️ **Renal:** Caution advised; dose reduction applied.")
    if selected_drug == "Phenytoin" and alb < 4.4:
        st.info(f"💡 **Albumin:** Corrected target Css is {target/((0.2*alb)+0.1):.1f} mg/L.")
    st.write("Recommendation: Start therapy and monitor efficacy.")
    st.markdown('</div>', unsafe_allow_html=True)

with tab4:
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.subheader("📋 Case Summary Table")
    st.table({"Parameter": ["Age", "Weight", "IBW", "CrCl", "Regimen"], "Value": [f"{age}Y", f"{weight}kg", f"{ibw:.1f}kg", f"{crcl:.1f}mL/min", f"{round(md)}mg q{interval}h"]})
    st.markdown('</div>', unsafe_allow_html=True)

with tab5:
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.subheader("📝 Professional SOAP Note")
    soap_note = f"S: {age}Y patient on {selected_drug}.\nO: Weight {weight}kg, CrCl {crcl:.1f}mL/min, SCr {scr}mg/dL.\nA: Personalized dosing for {'obese' if is_obese else 'normal weight'} patient.\nP: Administer LD {round(ld)}mg. Start MD {round(md)}mg q{interval}h. Monitor serum levels."
    st.markdown(f'<div style="background:#f0f9ff; padding:20px; border-radius:15px; border-left:10px solid #0f172a;">{soap_note.replace("\n", "<br><br>")}</div>', unsafe_allow_html=True)
    
    # تحسين زرار الطباعة
    pdf_file = create_pdf_report(age, weight, selected_drug, crcl, ld, md, interval, soap_note)
    st.download_button("📥 Download Final Clinical Report", pdf_file, f"DoseWise_{selected_drug}.pdf", "application/pdf")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<center style='color:#64748b;'>DoseWise Clinical v10.0 | MNU Faculty of Pharmacy | Project by Eslam Ahmed</center>", unsafe_allow_html=True)
