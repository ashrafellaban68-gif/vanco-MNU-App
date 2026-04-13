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
# 🎨 1. Premium Medical UI & Advanced Animations
# ==============================
def set_page_style():
    st.markdown('''
    <style>
    /* دخول العناصر بنعومة Slide-up */
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(30px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* نبض خفيف للأزرار */
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.02); }
        100% { transform: scale(1); }
    }

    .stApp {
        background-color: #f8fafc;
    }

    /* Hero Section - التصميم الفخم */
    .hero {
        background: linear-gradient(135deg, #0f172a, #1e3a8a);
        padding: 45px;
        border-radius: 0 0 50px 50px;
        text-align: center;
        color: white;
        margin: -60px -20px 30px -20px;
        box-shadow: 0 15px 35px rgba(0,0,0,0.2);
        animation: fadeInUp 0.8s ease-out;
    }

    /* Section Styling & Hover Effects */
    .section {
        background: white;
        padding: 30px;
        border-radius: 20px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.05);
        border: 1px solid #e2e8f0;
        margin-bottom: 25px;
        animation: fadeInUp 1s ease-out;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }
    .section:hover {
        transform: translateY(-8px);
        box-shadow: 0 15px 30px rgba(0,0,0,0.1);
        border-color: #3b82f6;
    }

    /* Medical Buttons */
    .stButton>button {
        background: linear-gradient(45deg, #1e3a8a, #3b82f6);
        color: white;
        border-radius: 50px;
        height: 3.8em;
        width: 100%;
        font-weight: bold;
        font-size: 18px;
        border: none;
        transition: 0.3s;
        animation: pulse 2s infinite;
    }
    .stButton>button:hover {
        background: linear-gradient(45deg, #3b82f6, #1e3a8a);
        box-shadow: 0 10px 20px rgba(59, 130, 246, 0.4);
    }
    </style>
    ''', unsafe_allow_html=True)

# ==============================
# 📄 2. Advanced PDF Report Generator
# ==============================
def create_pdf_report(age, weight, drug, crcl, ld, md, interval, soap_text, analysis):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('TitleStyle', parent=styles['Title'], textColor=colors.hexColor("#1e3a8a"), fontSize=22)
    
    content = []
    content.append(Paragraph("DoseWise: Clinical Pharmacokinetics Report", title_style))
    content.append(Spacer(1, 20))
    
    # Table Data for PDF
    data = [
        ["Patient Age", f"{age} Y", "Drug Selected", drug],
        ["Actual Weight", f"{weight} kg", "Est. CrCl", f"{crcl:.1f} mL/min"]
    ]
    t = Table(data, colWidths=[100, 150, 100, 150])
    t.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), colors.whitesmoke), ('GRID', (0,0), (-1,-1), 0.5, colors.grey)]))
    content.append(t)
    
    content.append(Spacer(1, 25))
    content.append(Paragraph("<b>Calculated Regimen:</b>", styles['Heading2']))
    content.append(Paragraph(f"- Loading Dose: {round(ld)} mg", styles['Normal']))
    content.append(Paragraph(f"- Maintenance Dose: {round(md)} mg every {interval} hours", styles['Normal']))
    
    content.append(Spacer(1, 25))
    content.append(Paragraph("<b>Clinical SOAP Note:</b>", styles['Heading3']))
    content.append(Paragraph(soap_text.replace('\n', '<br/>'), styles['Normal']))
    
    doc.build(content)
    return buffer.getvalue()

# ==============================
# ⚙️ 3. Main Application Framework
# ==============================
st.set_page_config(page_title="DoseWise Clinical Pro", layout="wide")
set_page_style()

st.markdown('<div class="hero"><h1>💊 DoseWise Clinical Pro</h1><p>The Comprehensive Pharmacokinetics Decision Support System</p></div>', unsafe_allow_html=True)

# --- GLOBAL VARIABLES SETUP ---
if 'calculated' not in st.session_state: st.session_state.calculated = False

# تجميع التبويبات الخمسة
tab1, tab2, tab3, tab4, tab5 = st.tabs(["🎯 Calculator", "📚 Drug Monograph", "⚖️ Clinical Decision", "📋 Case Summary", "📝 SOAP Note"])

# --- TAB 1: CALCULATOR ---
with tab1:
    st.markdown('<div class="section">', unsafe_allow_html=True)
    selected_drug = st.selectbox("💊 Select Medication", ["Phenytoin", "Valproic acid", "Carbamazepine", "Levetiracetam"])
    
    c_in_1, c_in_2 = st.columns(2)
    with c_in_1:
        age = st.number_input("Age (Years)", 1, 100, 30)
        weight = st.number_input("Total Weight (kg)", 10.0, 250.0, 70.0)
        height = st.number_input("Height (cm)", 50, 250, 170)
    with c_in_2:
        gender = st.selectbox("Gender", ["Male", "Female"])
        scr = st.number_input("Serum Creatinine (mg/dL)", 0.1, 5.0, 1.0)
        target = st.slider("Target Concentration (Css)", 5, 100, 15 if selected_drug != "Valproic acid" else 75)
    
    interval = st.selectbox("Interval (hr)", [4, 6, 8, 12, 24], index=3)

    # --- SCIENTIFIC LOGIC ---
    ht_in = height / 2.54; ibw = (50 + 2.3*(ht_in-60)) if gender=="Male" else (45.5 + 2.3*(ht_in-60))
    is_obese = weight > (1.2 * ibw)
    d_wt = weight; s_f, alb, vmax, km = 0.92, 4.4, 7.0, 4.0

    if selected_drug == "Phenytoin":
        st.markdown("---")
        st.subheader("🧬 Phenytoin Advanced Settings")
        if is_obese:
            d_wt = ibw + 0.4 * (weight - ibw)
            st.warning(f"Obesity: Adjusted Body Weight used: {d_wt:.1f} kg")
        cp1, cp2 = st.columns(2)
        with cp1:
            vmax = st.number_input("Vmax (mg/kg/day)", 1.0, 15.0, 7.0)
            alb = st.number_input("Serum Albumin (g/dL)", 0.5, 6.0, 4.4)
        with cp2:
            km = st.number_input("Km (mg/L)", 1.0, 10.0, 4.0)
            salt_form = st.selectbox("Formulation", ["Sodium (S=0.92)", "Acid (S=1.0)"])
        s_f = 0.92 if "Sodium" in salt_form else 1.0

    crcl_wt = ibw if is_obese else weight
    crcl = ((140-age)*crcl_wt)/(72*scr) if gender=="Male" else ((140-age)*crcl_wt)/(72*scr)*0.85

    # Drug Specific Equations
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
        st.session_state.calculated = True
        st.balloons()
        st.markdown("---")
        res1, res2, res3 = st.columns(3)
        res1.metric("Creatinine Clearance", f"{crcl:.1f} mL/min")
        res2.metric("Volume of Dist. (Vd)", f"{vd:.1f} L")
        res3.metric("t½ (Elimination)", f"{t_half:.1f} h" if selected_drug != "Phenytoin" else "N/A")
        if selected_drug == "Phenytoin":
            st.info(f"Steady State Profile: Peak {peak:.2f} mg/L | Trough {trough:.2f} mg/L")
        st.success(f"Recommended Regimen: LD {round(ld)} mg | MD {round(md)} mg every {interval} hours")
    st.markdown('</div>', unsafe_allow_html=True)

# --- TAB 2: DRUG MONOGRAPH ---
with tab2:
    st.markdown('<div class="section">', unsafe_allow_html=True)
    drug_data = {
        "Phenytoin": ["10-20 mg/L", "1000 mg/day", "Gingival hyperplasia, Ataxia, Nystagmus."],
        "Valproic acid": ["50-100 mg/L", "60 mg/kg/day", "Hepatotoxicity, Hair loss, Weight gain."],
        "Carbamazepine": ["4-12 mg/L", "1600 mg/day", "Auto-induction, Hyponatremia, SJS."],
        "Levetiracetam": ["12-46 mg/L", "3000 mg/day", "Behavioral changes, Irritability."]
    }
    st.subheader(f"📚 {selected_drug} Monograph")
    st.write(f"**Therapeutic Window:** {drug_data[selected_drug][0]}")
    st.write(f"**Maximum Daily Dose:** {drug_data[selected_drug][1]}")
    st.error(f"**Major Side Effects:** {drug_data[selected_drug][2]}")
    st.markdown('</div>', unsafe_allow_html=True)

# --- TAB 3: CLINICAL DECISION ---
with tab3:
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.subheader("⚖️ Clinical Decision Support")
    if is_obese: st.error(f"❗ **Dosing Weight:** Patient is obese. ABW used ({d_wt:.1f} kg) for Vd adjustment.")
    if crcl < 50: st.warning(f"⚠️ **Renal Status:** CrCl {crcl:.1f} mL/min. Maintenance dose reduction applied.")
    if selected_drug == "Phenytoin" and alb < 4.4:
        st.info(f"💡 **Albumin correction:** Low albumin ({alb} g/dL). Adjusted target Css is {target/((0.2*alb)+0.1):.1f} mg/L.")
    st.write("**Recommendation:** Initiate therapy and monitor serum levels after 5 half-lives.")
    st.markdown('</div>', unsafe_allow_html=True)

# --- TAB 4: CASE SUMMARY ---
with tab4:
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.subheader("📋 Final Case Summary Presentation")
    st.table({
        "Clinical Parameter": ["Patient Age", "Weight Status", "Estimated CrCl", "Drug Choice", "Vd", "Loading Dose", "Maintenance Dose"],
        "Value": [f"{age} Years", "Obese" if is_obese else "Normal", f"{crcl:.1f} mL/min", selected_drug, f"{vd:.1f} L", f"{round(ld)} mg", f"{round(md)} mg q{interval}h"]
    })
    st.markdown('</div>', unsafe_allow_html=True)

# --- TAB 5: SOAP NOTE & PRINTING ---
with tab5:
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.subheader("📝 Professional SOAP Documentation")
    soap_note = f"S: {age}Y patient on {selected_drug}. No known allergies.\nO: Weight {weight}kg, SCr {scr}mg/dL, CrCl {crcl:.1f}mL/min.\nA: PK regimen optimized for patient's {'obese' if is_obese else 'normal'} weight and renal status.\nP: Administer LD {round(ld)}mg. Start MD {round(md)}mg every {interval}h. Monitor for {drug_data[selected_drug][2].split(',')[0]}."
    
    st.markdown(f'''<div style="background:#f0f9ff; padding:25px; border-radius:15px; border-left:10px solid #0f172a; font-family:serif;">{soap_note.replace("\n", "<br><br>")}</div>''', unsafe_allow_html=True)
    
    st.markdown("---")
    pdf_file = create_pdf_report(age, weight, selected_drug, crcl, ld, md, interval, soap_note, "")
    st.download_button("📥 Download Final Clinical Report (PDF)", pdf_file, f"DoseWise_{selected_drug}.pdf", "application/pdf")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<center style='color:#64748b;'>DoseWise Clinical v9.0 | MNU Faculty of Pharmacy | Project by Eslam Ahmed</center>", unsafe_allow_html=True)
