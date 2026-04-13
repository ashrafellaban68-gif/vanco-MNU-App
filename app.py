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
        background-image: linear-gradient(rgba(255, 255, 255, 0.88), rgba(255, 255, 255, 0.88)), {bg_img};
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
def create_pdf_report(age, weight, drug, crcl, ld, md, interval, soap_text=""):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    content = []
    content.append(Paragraph("DoseWise - Clinical PK Report", styles['Title']))
    content.append(Spacer(1, 20))
    content.append(Paragraph(f"<b>Patient Age:</b> {age}Y | <b>Weight:</b> {weight}kg", styles['Normal']))
    content.append(Paragraph(f"<b>Drug:</b> {drug} | <b>CrCl:</b> {crcl:.1f} mL/min", styles['Normal']))
    content.append(Spacer(1, 15))
    content.append(Paragraph(f"<b>Regimen:</b> LD {round(ld)} mg then {round(md)} mg every {interval}h", styles['Heading2']))
    content.append(Spacer(1, 20))
    content.append(Paragraph("<b>Clinical SOAP Summary:</b>", styles['Heading3']))
    content.append(Paragraph(soap_text.replace('\n', '<br/>'), styles['Normal']))
    doc.build(content)
    return buffer.getvalue()

# ==============================
# ⚙️ 3. App Setup & Logic
# ==============================
st.set_page_config(page_title="DoseWise | Clinical PK Platform", layout="wide")
set_page_style('bg.jpg' if os.path.exists("bg.jpg") else "")

st.markdown('<div class="hero">💊 DoseWise Platform</div>', unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs(["🎯 Calculator", "📚 Drug Knowledge", "⚖️ Clinical Decision", "📋 Case Summary"])

with tab1:
    st.markdown('<div class="section">', unsafe_allow_html=True)
    selected_drug = st.selectbox("Select Medication", ["Phenytoin", "Valproic acid", "Carbamazepine", "Levetiracetam"])
    col_in, col_res = st.columns([1.3, 1])
    
    with col_in:
        c1, c2 = st.columns(2)
        with c1:
            age = st.number_input("Age", 1, 100, 30)
            weight = st.number_input("Weight (kg)", 10.0, 250.0, 70.0)
            height = st.number_input("Height (cm)", 50, 250, 170)
        with c2:
            gender = st.selectbox("Gender", ["Male", "Female"])
            scr = st.number_input("SCr (mg/dL)", 0.1, 5.0, 1.0)
            target = st.slider("Target Css (mg/L)", 5, 100, 15 if selected_drug != "Valproic acid" else 75)
        interval = st.selectbox("Interval (hr)", [4, 6, 8, 12, 24], index=3)

        # Basic PK Logic
        ht_in = height / 2.54
        ibw = (50 + 2.3*(ht_in-60)) if gender=="Male" else (45.5 + 2.3*(ht_in-60))
        dosing_weight = weight
        is_obese = weight > (1.2 * ibw)
        s_factor, albumin, vmax, km, extra_info = 0.92, 4.4, 7.0, 4.0, ""

        if selected_drug == "Phenytoin":
            st.markdown("---")
            if is_obese: dosing_weight = ibw + 0.4 * (weight - ibw)
            cp1, cp2 = st.columns(2)
            with cp1:
                vmax = st.number_input("Vmax", 1.0, 15.0, 7.0)
                albumin = st.number_input("Albumin (g/dL)", 0.5, 6.0, 4.4)
            with cp2:
                km = st.number_input("Km (mg/L)", 1.0, 10.0, 4.0)
                salt = st.selectbox("Form", ["Sodium (0.92)", "Acid (1.0)"])
            s_factor = 0.92 if "Sodium" in salt else 1.0
            if albumin < 4.4: 
                adj_css = target / ((0.2 * albumin) + 0.1)
                extra_info = f"Albumin correction: Adjusted target is {adj_css:.1f} mg/L."

        crcl_wt = ibw if is_obese else weight
        crcl = ((140-age)*crcl_wt)/(72*scr) if gender=="Male" else ((140-age)*crcl_wt)/(72*scr)*0.85

        if selected_drug == "Phenytoin":
            vd = 0.7 * dosing_weight; vmax_t = vmax * dosing_weight
            md = ((vmax_t * target) / (km + target)) / (24/interval); ld = target * vd
            k_el = (vmax_t / (km + target)) / vd; t_half = 0.693 / k_el
            css_max = (target / s_factor) + ((md * s_factor) / vd); css_min = css_max * math.exp(-k_el * interval)
        elif selected_drug == "Valproic acid":
            vd, cl = 0.15 * weight, 0.008 * weight
            k = cl/vd; ld, md = target*vd, target*cl*interval; t_half = 0.693/k
        else:
            vd, cl = 0.6 * weight, (crcl * 0.6) / 1000 * 60
            k = cl/vd; ld, md = target*vd, target*cl*interval; t_half = 0.693/k

        if selected_drug != "Phenytoin" and crcl < 50: md *= (crcl/100)

    with col_res:
        st.subheader("📊 Output")
        if st.button("🚀 Analyze Regimen"):
            st.metric("CrCl", f"{crcl:.1f} mL/min")
            if selected_drug == "Phenytoin": st.info(f"Peak: {css_max:.2f} | Trough: {css_min:.2f}")
            st.success(f"**Regimen:** LD {round(ld)}mg | MD {round(md)}mg q{interval}h")
    st.markdown('</div>', unsafe_allow_html=True)

# --- TAB 2: Knowledge ---
with tab2:
    st.markdown('<div class="section">', unsafe_allow_html=True)
    drug_db = {
        "Phenytoin": {"Max": "600-1000 mg/d", "SE": "Gingival hyperplasia, Ataxia, Nystagmus.", "Note": "Michaelis-Menten kinetics."},
        "Valproic acid": {"Max": "60 mg/kg/d", "SE": "Hepatotoxicity, Hair loss, Weight gain.", "Note": "Monitor LFTs."},
        "Carbamazepine": {"Max": "1600 mg/d", "SE": "Hyponatremia, Stevens-Johnson Syndrome.", "Note": "Auto-induction risk."},
        "Levetiracetam": {"Max": "3000 mg/d", "SE": "Irritability, Behavioral changes.", "Note": "Adjust for renal function."}
    }
    db = drug_db[selected_drug]
    st.subheader(f"💊 {selected_drug} Monograph")
    k1, k2 = st.columns(2)
    with k1: st.write(f"**Max Dose:** {db['Max']}"); st.write(f"**Clinical Note:** {db['Note']}")
    with k2: st.error(f"**Side Effects:** {db['SE']}")
    st.markdown('</div>', unsafe_allow_html=True)

# --- TAB 3: Decision ---
with tab3:
    st.markdown('<div class="section">', unsafe_allow_html=True)
    if is_obese: st.warning("Obesity: Dosing weight adjusted (ABW).")
    if crcl < 50: st.error("Renal Impairment: Maintenance dose reduced.")
    if selected_drug == "Phenytoin" and albumin < 4.4: st.info(extra_info)
    st.markdown('</div>', unsafe_allow_html=True)

# --- TAB 4: Case Summary & SOAP ---
with tab4:
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center; color:#1e3a8a;'>📋 SOAP Note & Case Summary</h2>", unsafe_allow_html=True)
    
    soap_content = f"""S: {age}Y {gender.lower()} patient, {weight}kg.
O: CrCl {crcl:.1f} mL/min, SCr {scr} mg/dL, {'Obese' if is_obese else 'Normal weight'}.
A: Individualized {selected_drug} dosing required.
P: LD {round(ld)}mg once. MD {round(md)}mg every {interval}h."""

    st.markdown(f'''
    <div style="background-color: #f8fafc; border-left: 5px solid #1e3a8a; padding: 20px; border-radius: 10px;">
        <p><b><span style="color:#1e3a8a;">S (Subjective):</span></b> Patient is a {age}-year-old {gender.lower()}, {weight}kg.</p>
        <p><b><span style="color:#1e3a8a;">O (Objective):</span></b> SCr {scr}mg/dL | CrCl {crcl:.1f}mL/min | {'Obese' if is_obese else 'Normal Weight'}.</p>
        <p><b><span style="color:#1e3a8a;">A (Assessment):</span></b> Adjusted PK regimen based on {selected_drug} parameters.</p>
        <p><b><span style="color:#1e3a8a;">P (Plan):</span></b> LD <b>{round(ld)}mg</b> then MD <b>{round(md)}mg q{interval}h</b>. Monitor for {db['SE']}.</p>
    </div>
    ''', unsafe_allow_html=True)
    
    pdf_btn = create_pdf_report(age, weight, selected_drug, crcl, ld, md, interval, soap_content)
    st.download_button("📥 Download SOAP Report", pdf_btn, "DoseWise_SOAP.pdf", "application/pdf")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<center>💙 **DoseWise** | Clinical PK Project | MNU</center>", unsafe_allow_html=True)
