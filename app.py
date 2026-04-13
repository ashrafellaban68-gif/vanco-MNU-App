import streamlit as st
import os
import base64
import math
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
from io import BytesIO

# ==============================
# 🎨 1. Premium Style & Animations
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
    @keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(20px); }} to {{ opacity: 1; transform: translateY(0); }} }}
    .stApp {{
        background-image: linear-gradient(rgba(255, 255, 255, 0.9), rgba(255, 255, 255, 0.9)), {bg_img};
        background-size: cover; background-attachment: fixed;
    }}
    .hero {{
        background: linear-gradient(135deg, #1e3a8a, #3b82f6);
        padding: 30px; border-radius: 20px; text-align: center; color: white;
        font-size: 38px; font-weight: 900; box-shadow: 0 10px 25px rgba(0,0,0,0.2);
        margin-bottom: 25px; animation: fadeIn 0.8s ease-out;
    }}
    .section {{
        background: white; padding: 25px; border-radius: 15px; margin-top: 20px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.05); border: 1px solid #e2e8f0;
        transition: 0.3s; animation: fadeIn 1s ease-out;
    }}
    .section:hover {{ transform: translateY(-5px); box-shadow: 0 12px 24px rgba(0,0,0,0.1); }}
    .stButton>button {{
        background: linear-gradient(45deg, #1e3a8a, #3b82f6); color: white;
        border-radius: 30px; height: 3.5em; width: 100%; font-weight: bold;
        transition: 0.3s;
    }}
    </style>
    ''', unsafe_allow_html=True)

# ==============================
# 📄 2. PDF Report Function
# ==============================
def create_pdf_report(age, weight, drug, crcl, ld, md, interval, soap):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    content = [
        Paragraph("DoseWise Clinical Report", styles['Title']),
        Spacer(1, 15),
        Paragraph(f"Patient: {age}Y | {weight}kg | Drug: {drug}", styles['Normal']),
        Paragraph(f"Final Plan: LD {round(ld)}mg | MD {round(md)}mg q{interval}h", styles['Heading2']),
        Spacer(1, 15),
        Paragraph("Clinical SOAP Note:", styles['Heading3']),
        Paragraph(soap.replace('\n', '<br/>'), styles['Normal'])
    ]
    doc.build(content)
    return buffer.getvalue()

# ==============================
# ⚙️ 3. App Logic
# ==============================
st.set_page_config(page_title="DoseWise PK Platform", layout="wide")
set_page_style('bg.jpg' if os.path.exists("bg.jpg") else "")

st.markdown('<div class="hero">💊 DoseWise Platform</div>', unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs(["🎯 Calculator", "📚 Drug Knowledge", "⚖️ Decision", "📋 Case Summary"])

with tab1:
    st.markdown('<div class="section">', unsafe_allow_html=True)
    selected_drug = st.selectbox("Select Medication", ["Phenytoin", "Valproic acid", "Carbamazepine", "Levetiracetam"])
    c_in, c_res = st.columns([1.3, 1])
    
    with c_in:
        c1, c2 = st.columns(2)
        with c1:
            age = st.number_input("Age", 1, 100, 30)
            weight = st.number_input("Actual Weight (kg)", 10.0, 250.0, 70.0)
            height = st.number_input("Height (cm)", 50, 250, 170)
        with c2:
            gender = st.selectbox("Gender", ["Male", "Female"])
            scr = st.number_input("SCr (mg/dL)", 0.1, 5.0, 1.0)
            target = st.slider("Target Css", 5, 100, 15 if selected_drug != "Valproic acid" else 75)
        interval = st.selectbox("Interval (hr)", [4, 6, 8, 12, 24], index=3)

        # Scientific Logic Setup
        ht_in = height / 2.54; ibw = (50 + 2.3*(ht_in-60)) if gender=="Male" else (45.5 + 2.3*(ht_in-60))
        d_wt = weight; is_obese = weight > (1.2 * ibw)
        s_f, alb, vmax, km, extra = 0.92, 4.4, 7.0, 4.0, ""

        if selected_drug == "Phenytoin":
            st.markdown("---")
            if is_obese: d_wt = ibw + 0.4 * (weight - ibw)
            cp1, cp2 = st.columns(2)
            with cp1:
                vmax = st.number_input("Vmax", 1.0, 15.0, 7.0); alb = st.number_input("Albumin", 0.5, 6.0, 4.4)
            with cp2:
                km = st.number_input("Km", 1.0, 10.0, 4.0); salt = st.selectbox("Form", ["Sodium (0.92)", "Acid (1.0)"])
            s_f = 0.92 if "Sodium" in salt else 1.0
            if alb < 4.4: extra = f"Albumin correction applied. Adj Css: {target/((0.2*alb)+0.1):.1f} mg/L."

        crcl_wt = ibw if is_obese else weight
        crcl = ((140-age)*crcl_wt)/(72*scr) if gender=="Male" else ((140-age)*crcl_wt)/(72*scr)*0.85

        if selected_drug == "Phenytoin":
            vd = 0.7 * d_wt; vmax_t = vmax * d_wt; md = ((vmax_t * target) / (km + target)) / (24/interval); ld = target * vd
            k_el = (vmax_t / (km + target)) / vd; t_h = 0.693 / k_el; peak = (target/s_f)+((md*s_f)/vd); trough = peak * math.exp(-k_el*interval)
        elif selected_drug == "Valproic acid":
            vd, cl = 0.15 * weight, 0.008 * weight; k = cl/vd; ld, md = target*vd, target*cl*interval; t_h = 0.693/k
        elif selected_drug == "Carbamazepine":
            vd, cl = 1.4 * weight, 0.06 * weight; k = cl/vd; ld, md = target*vd, target*cl*interval; t_h = 0.693/k
        else: # Levetiracetam
            vd = 0.6 * weight; cl = (crcl * 0.6) / 1000 * 60; k = cl/vd; ld, md = target*vd, target*cl*interval; t_h = 0.693/k

        if selected_drug != "Phenytoin" and crcl < 50: md *= (crcl/100)

    with c_res:
        st.subheader("📊 Output Results")
        if st.button("🚀 Calculate & Animate"):
            st.balloons()
            st.metric("CrCl", f"{crcl:.1f} mL/min")
            if selected_drug == "Phenytoin": st.info(f"Peak: {peak:.2f} | Trough: {trough:.2f}")
            st.success(f"Final Regimen: LD {round(ld)}mg | MD {round(md)}mg q{interval}h")
    st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    st.markdown('<div class="section">', unsafe_allow_html=True)
    drug_db = {
        "Phenytoin": {"Max": "600-1000 mg/d", "SE": "Gingival hyperplasia, Ataxia, Nystagmus.", "Mech": "Na Channel Blocker"},
        "Valproic acid": {"Max": "60 mg/kg/d", "SE": "Hepatotoxicity, Hair loss, Weight gain.", "Mech": "GABA Enhancer"},
        "Carbamazepine": {"Max": "1600 mg/d", "SE": "Hyponatremia, Diplopia, Stevens-Johnson.", "Mech": "Na Channel Blocker"},
        "Levetiracetam": {"Max": "3000 mg/d", "SE": "Irritability, Behavioral changes.", "Mech": "SV2A Modulator"}
    }
    st.subheader(f"💊 {selected_drug} Information")
    st.write(f"**Mechanism:** {drug_db[selected_drug]['Mech']}")
    st.write(f"**Max Dose:** {drug_db[selected_drug]['Max']}")
    st.error(f"**Side Effects:** {drug_db[selected_drug]['SE']}")
    st.markdown('</div>', unsafe_allow_html=True)

with tab3:
    st.markdown('<div class="section">', unsafe_allow_html=True)
    if is_obese: st.warning("Obesity Adjustment: Using Adjusted Body Weight (ABW).")
    if crcl < 50: st.error("Renal Impairment: Maintenance dose adjusted.")
    if selected_drug == "Phenytoin" and alb < 4.4: st.info(extra)
    st.markdown('</div>', unsafe_allow_html=True)

with tab4:
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center;'>📝 SOAP Note & Summary</h2>", unsafe_allow_html=True)
    
    s_note = f"Patient is a {age}Y {gender}, {weight}kg."
    o_note = f"SCr {scr}mg/dL, CrCl {crcl:.1f}mL/min, {'Obese' if is_obese else 'Normal weight'}."
    a_note = f"Individualized PK dosing for {selected_drug}."
    p_note = f"LD {round(ld)}mg, MD {round(md)}mg every {interval}h. Monitor {drug_db[selected_drug]['SE'].split(',')[0]}."

    st.markdown(f'''
    <div style="background-color: #f8fafc; border-left: 5px solid #1e3a8a; padding: 20px; border-radius: 10px; margin-bottom:20px;">
        <p><b>S:</b> {s_note}</p><p><b>O:</b> {o_note}</p><p><b>A:</b> {a_note}</p><p><b>P:</b> {p_note}</p>
    </div>
    ''', unsafe_allow_html=True)
    
    st.download_button("📥 Save PDF Report", create_pdf_report(age, weight, selected_drug, crcl, ld, md, interval, f"S:{s_note}\nO:{o_note}\nA:{a_note}\nP:{p_note}"))
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<center>💙 **DoseWise** | Clinical Pharmacokinetics | MNU Faculty of Pharmacy</center>", unsafe_allow_html=True)
