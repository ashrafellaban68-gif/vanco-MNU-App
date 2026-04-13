import streamlit as st
import os
import base64
import math
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
from io import BytesIO

# ==============================
# 🎨 1. Professional Medical UI & Animations
# ==============================
def set_page_style():
    st.markdown('''
    <style>
    /* Professional Fade-in Animation */
    @keyframes slideUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .stApp {
        background-color: #f4f7f9;
    }

    /* Hero Section */
    .hero {
        background: linear-gradient(135deg, #102a43, #243b53);
        padding: 40px;
        border-radius: 0 0 30px 30px;
        text-align: center;
        color: white;
        margin: -60px -20px 30px -20px;
        box-shadow: 0 10px 20px rgba(0,0,0,0.1);
        animation: slideUp 0.8s ease-out;
    }

    /* Standardized Medical Cards */
    .section {
        background: white;
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border: 1px solid #d9e2ec;
        margin-bottom: 20px;
        animation: slideUp 1s ease-out;
        transition: transform 0.3s ease;
    }
    .section:hover {
        transform: translateY(-5px);
        border-color: #334e68;
    }

    /* Medical Buttons */
    .stButton>button {
        background: #102a43;
        color: white;
        border-radius: 8px;
        font-weight: 600;
        border: none;
        padding: 10px 24px;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        background: #243b53;
        box-shadow: 0 4px 12px rgba(16, 42, 67, 0.2);
    }

    /* Custom Alert Styles */
    .decision-card {
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 10px;
        border-right: 5px solid;
    }
    </style>
    ''', unsafe_allow_html=True)

# ==============================
# 📄 2. PDF Report Generator
# ==============================
def create_pdf_report(age, weight, drug, crcl, ld, md, interval, soap_text):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    content = [
        Paragraph("DoseWise Medical Report", styles['Title']),
        Spacer(1, 20),
        Paragraph(f"<b>Patient:</b> {age}Y | {weight}kg", styles['Normal']),
        Paragraph(f"<b>Drug:</b> {drug} | <b>CrCl:</b> {crcl:.1f} mL/min", styles['Normal']),
        Spacer(1, 20),
        Paragraph(f"<b>Final Regimen:</b> {round(md)} mg q{interval}h (LD: {round(ld)} mg)", styles['Heading2']),
        Spacer(1, 20),
        Paragraph("<b>Official SOAP Note:</b>", styles['Heading3']),
        Paragraph(soap_text.replace('\n', '<br/>'), styles['Normal'])
    ]
    doc.build(content)
    return buffer.getvalue()

# ==============================
# ⚙️ 3. Main App Execution
# ==============================
st.set_page_config(page_title="DoseWise Clinical", layout="wide")
set_page_style()

st.markdown('<div class="hero"><h1>💊 DoseWise Clinical Pro</h1><p>Professional Pharmacokinetics Decision Support System</p></div>', unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5 = st.tabs(["🎯 Calculator", "📚 Monograph", "⚖️ Clinical Decision", "📋 Case Summary", "📝 SOAP Note"])

# --- Calculation Logic ---
with tab1:
    selected_drug = st.selectbox("Medication Selection", ["Phenytoin", "Valproic acid", "Carbamazepine", "Levetiracetam"])
    c_in, c_res = st.columns([1.2, 1])
    
    with c_in:
        st.markdown('<div class="section">', unsafe_allow_html=True)
        g1, g2 = st.columns(2)
        with g1:
            age = st.number_input("Age", 1, 100, 30)
            weight = st.number_input("Weight (kg)", 10.0, 250.0, 70.0)
            height = st.number_input("Height (cm)", 50, 250, 170)
        with g2:
            gender = st.selectbox("Gender", ["Male", "Female"])
            scr = st.number_input("SCr (mg/dL)", 0.1, 5.0, 1.0)
            target = st.slider("Target Css (mg/L)", 5, 100, 15)
        interval = st.selectbox("Interval (hr)", [4, 6, 8, 12, 24], index=3)
        st.markdown('</div>', unsafe_allow_html=True)

        # Advanced Logic
        ht_in = height / 2.54; ibw = (50 + 2.3*(ht_in-60)) if gender=="Male" else (45.5 + 2.3*(ht_in-60))
        d_wt = weight; is_obese = weight > (1.2 * ibw)
        s_f, alb, vmax, km, extra = 0.92, 4.4, 7.0, 4.0, ""

        if selected_drug == "Phenytoin":
            st.markdown('<div class="section">', unsafe_allow_html=True)
            if is_obese: d_wt = ibw + 0.4 * (weight - ibw)
            p1, p2 = st.columns(2)
            with p1:
                vmax = st.number_input("Vmax (mg/kg/d)", 1.0, 15.0, 7.0); alb = st.number_input("Albumin (g/dL)", 0.5, 6.0, 4.4)
            with p2:
                km = st.number_input("Km (mg/L)", 1.0, 10.0, 4.0); salt = st.selectbox("Form", ["Sodium (0.92)", "Acid (1.0)"])
            s_f = 0.92 if "Sodium" in salt else 1.0
            st.markdown('</div>', unsafe_allow_html=True)

        crcl_wt = ibw if is_obese else weight
        crcl = ((140-age)*crcl_wt)/(72*scr) if gender=="Male" else ((140-age)*crcl_wt)/(72*scr)*0.85

        if selected_drug == "Phenytoin":
            vd = 0.7 * d_wt; vmax_t = vmax * d_wt; md = ((vmax_t * target) / (km + target)) / (24/interval); ld = target * vd
            k_el = (vmax_t / (km + target)) / vd; t_h = 0.693 / k_el; peak = (target/s_f)+((md*s_f)/vd); trough = peak * math.exp(-k_el*interval)
        else: # Standard Linear
            vd = 0.6 * weight; cl = (crcl * 0.6) / 1000 * 60; k = cl/vd; ld, md = target*vd, target*cl*interval; t_h = 0.693/k

    with c_res:
        st.markdown('<div class="section" style="height: 100%;">', unsafe_allow_html=True)
        st.subheader("📊 Clinical Analysis")
        if st.button("🚀 Execute PK Model"):
            st.metric("CrCl", f"{crcl:.1f} mL/min")
            st.metric("Volume of Dist. (Vd)", f"{vd:.1f} L")
            if selected_drug == "Phenytoin": st.info(f"Expected Trough: {trough:.2f} mg/L")
            st.success(f"Recommended Regimen:\n\n{round(md)} mg every {interval}h")
        st.markdown('</div>', unsafe_allow_html=True)

# --- TAB 3: Clinical Decision (The "Brain") ---
with tab3:
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.subheader("⚖️ Pharmacist's Decision Support")
    
    if is_obese:
        st.error(f"⚠️ **Obesity Alert:** Actual weight is >20% over IBW. Dosing adjusted to ABW ({d_wt:.1f} kg).")
    else:
        st.success("✅ **Weight Status:** Patient is within normal weight range for dosing.")
    
    if crcl < 50:
        st.warning(f"⚠️ **Renal Adjustment:** CrCl is {crcl:.1f} mL/min. Maintenance dose reduction considered for non-linear drugs.")
    
    if selected_drug == "Phenytoin" and alb < 4.4:
        adj_c = target / ((0.2 * alb) + 0.1)
        st.info(f"ℹ️ **Albumin Correction:** Low albumin detected. Adjusted Target concentration is {adj_c:.1f} mg/L.")
    
    st.markdown(f"**Final Clinical Recommendation:** Initiate {selected_drug} with a Loading Dose of {round(ld)}mg to achieve rapid steady state.")
    st.markdown('</div>', unsafe_allow_html=True)

# --- TAB 4: Case Summary ---
with tab4:
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.subheader("📋 Case Data Summary")
    st.write(f"- **Patient Profile:** {age}Y {gender}, {weight}kg")
    st.write(f"- **Calculated CrCl:** {crcl:.1f} mL/min")
    st.write(f"- **Pharmacokinetic Profile:** Half-life ~{t_h:.1f} hours")
    st.markdown('</div>', unsafe_allow_html=True)

# --- TAB 5: SOAP Note (Separated) ---
with tab5:
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.subheader("📝 Clinical SOAP Note")
    soap_txt = f"S: {age}Y {gender} patient presents for {selected_drug} dose optimization.\nO: Weight {weight}kg, SCr {scr}mg/dL, CrCl {crcl:.1f}mL/min. Albumin {alb if selected_drug=='Phenytoin' else 'N/A'}.\nA: Patient requires individualized dosing due to {'obesity' if is_obese else 'body weight'} and renal status.\nP: Administer LD {round(ld)}mg once, then MD {round(md)}mg q{interval}h. Monitor serum levels."
    
    st.markdown(f'''
    <div style="background: #f0f4f8; padding: 20px; border-radius: 10px; border-left: 10px solid #102a43;">
        {soap_txt.replace('\n', '<br><br>')}
    </div>
    ''', unsafe_allow_html=True)
    
    st.download_button("📥 Download Official PDF", create_pdf_report(age, weight, selected_drug, crcl, ld, md, interval, soap_txt))
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<center style='color: #627d98;'>DoseWise Clinical Pro v2.0 | MNU Faculty of Pharmacy</center>", unsafe_allow_html=True)
