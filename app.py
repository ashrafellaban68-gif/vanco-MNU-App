import streamlit as st
import os
import base64
import math
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
from io import BytesIO

# ==============================
# 🎨 1. Advanced CSS: Animations & Transitions
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
    /* دخول العناصر بنعومة */
    @keyframes fadeInUp {{
        from {{ opacity: 0; transform: translateY(30px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    
    /* نبض الأزرار */
    @keyframes pulse {{
        0% {{ transform: scale(1); }}
        50% {{ transform: scale(1.02); }}
        100% {{ transform: scale(1); }}
    }}

    .stApp {{
        background-image: linear-gradient(rgba(255, 255, 255, 0.9), rgba(255, 255, 255, 0.9)), {bg_img};
        background-size: cover;
        background-attachment: fixed;
    }}

    .hero {{
        background: linear-gradient(135deg, #1e3a8a, #3b82f6);
        padding: 35px;
        border-radius: 25px;
        text-align: center;
        color: white;
        font-size: 42px;
        font-weight: 900;
        box-shadow: 0 15px 35px rgba(30, 58, 138, 0.3);
        margin-bottom: 30px;
        animation: fadeInUp 0.8s ease-out;
    }}

    .section {{
        background: white;
        padding: 30px;
        border-radius: 20px;
        margin-top: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.05);
        border: 1px solid #f1f5f9;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        animation: fadeInUp 1s ease-out;
    }}
    
    .section:hover {{
        transform: translateY(-8px);
        box-shadow: 0 20px 40px rgba(0,0,0,0.1);
    }}

    .stButton>button {{
        background: linear-gradient(45deg, #1e3a8a, #3b82f6);
        color: white;
        border-radius: 50px;
        height: 3.8em;
        width: 100%;
        font-weight: bold;
        font-size: 18px;
        border: none;
        transition: all 0.3s ease;
        animation: pulse 2s infinite;
    }}
    
    .stButton>button:hover {{
        background: linear-gradient(45deg, #3b82f6, #1e3a8a);
        box-shadow: 0 10px 20px rgba(30, 58, 138, 0.4);
    }}
    </style>
    ''', unsafe_allow_html=True)

# ==============================
# 📄 2. Logic & Scientific Calculations
# ==============================
def create_pdf_report(age, weight, drug, crcl, ld, md, interval, soap_text):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    content = [
        Paragraph("DoseWise Clinical Report", styles['Title']),
        Spacer(1, 20),
        Paragraph(f"Patient Info: {age}Y | {weight}kg", styles['Normal']),
        Paragraph(f"Pharmacological Regimen for {drug}", styles['Heading2']),
        Paragraph(f"Loading Dose: {round(ld)} mg | Maintenance: {round(md)} mg q{interval}h", styles['Normal']),
        Spacer(1, 15),
        Paragraph("SOAP Note Analysis:", styles['Heading3']),
        Paragraph(soap_text.replace('\n', '<br/>'), styles['Normal'])
    ]
    doc.build(content)
    return buffer.getvalue()

# ==============================
# ⚙️ 3. App Execution
# ==============================
st.set_page_config(page_title="DoseWise | Clinical Excellence", layout="wide")
set_page_style('bg.jpg' if os.path.exists("bg.jpg") else "")

st.markdown('<div class="hero">💊 DoseWise Clinical Platform</div>', unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs(["🎯 Smart Calculator", "📚 Drug Monograph", "⚖️ Clinical Decision", "📋 Case Summary"])

with tab1:
    st.markdown('<div class="section">', unsafe_allow_html=True)
    selected_drug = st.selectbox("Select Medication", ["Phenytoin", "Valproic acid", "Carbamazepine", "Levetiracetam"])
    
    col_in, col_res = st.columns([1.3, 1])
    
    with col_in:
        c1, c2 = st.columns(2)
        with c1:
            age = st.number_input("Age", 1, 100, 30)
            weight = st.number_input("Actual Weight (kg)", 10.0, 250.0, 70.0)
            height = st.number_input("Height (cm)", 50, 250, 170)
        with c2:
            gender = st.selectbox("Gender", ["Male", "Female"])
            scr = st.number_input("SCr (mg/dL)", 0.1, 5.0, 1.0)
            target = st.slider("Target Css (mg/L)", 5, 100, 15 if selected_drug != "Valproic acid" else 75)
        
        interval = st.selectbox("Interval (hr)", [4, 6, 8, 12, 24], index=3)

        # --- High-End Scientific Logic ---
        ht_in = height / 2.54
        ibw = (50 + 2.3*(ht_in-60)) if gender=="Male" else (45.5 + 2.3*(ht_in-60))
        dosing_weight = weight
        is_obese = weight > (1.2 * ibw)
        
        s_factor, albumin, vmax, km, extra_info = 0.92, 4.4, 7.0, 4.0, ""

        if selected_drug == "Phenytoin":
            st.markdown("---")
            if is_obese:
                dosing_weight = ibw + 0.4 * (weight - ibw)
                st.warning(f"Obesity Detected: Using ABW ({dosing_weight:.1f} kg)")
            cp1, cp2 = st.columns(2)
            with cp1:
                vmax = st.number_input("Vmax (mg/kg/d)", 1.0, 15.0, 7.0)
                albumin = st.number_input("Albumin (g/dL)", 0.5, 6.0, 4.4)
            with cp2:
                km = st.number_input("Km (mg/L)", 1.0, 10.0, 4.0)
                salt = st.selectbox("Dosage Form", ["Sodium (0.92)", "Acid (1.0)"])
            s_factor = 0.92 if "Sodium" in salt else 1.0
            if albumin < 4.4: 
                adj_css = target / ((0.2 * albumin) + 0.1)
                extra_info = f"Albumin correction: Adj Css {adj_css:.1f} mg/L."

        crcl_wt = ibw if is_obese else weight
        crcl = ((140-age)*crcl_wt)/(72*scr) if gender=="Male" else ((140-age)*crcl_wt)/(72*scr)*0.85

        if selected_drug == "Phenytoin":
            vd = 0.7 * dosing_weight; vmax_t = vmax * dosing_weight
            md = ((vmax_t * target) / (km + target)) / (24/interval); ld = target * vd
            k_el = (vmax_t / (km + target)) / vd; t_h = 0.693 / k_el
            peak = (target/s_factor)+((md*s_factor)/vd); trough = peak * math.exp(-k_el*interval)
        elif selected_drug == "Valproic acid":
            vd, cl = 0.15 * weight, 0.008 * weight; k = cl/vd; ld, md = target*vd, target*cl*interval; t_h = 0.693/k
        elif selected_drug == "Carbamazepine":
            vd, cl = 1.4 * weight, 0.06 * weight; k = cl/vd; ld, md = target*vd, target*cl*interval; t_h = 0.693/k
        else: # Levetiracetam
            vd = 0.6 * weight; cl = (crcl * 0.6) / 1000 * 60; k = cl/vd; ld, md = target*vd, target*cl*interval; t_h = 0.693/k

        if selected_drug != "Phenytoin" and crcl < 50: md *= (crcl/100)

    with col_res:
        st.subheader("📊 Output Results")
        if st.button("🚀 Run Analysis"):
            st.balloons()
            m1, m2, m3 = st.columns(3)
            m1.metric("CrCl", f"{crcl:.1f}")
            m2.metric("Vd (L)", f"{vd:.1f}")
            m3.metric("t½ (h)", f"{t_h:.1f}" if selected_drug != "Phenytoin" else "N/A")
            if selected_drug == "Phenytoin":
                st.info(f"Steady State: Peak {peak:.2f} | Trough {trough:.2f}")
            st.success(f"**Plan:** LD {round(ld)}mg | MD {round(md)}mg q{interval}h")

with tab2:
    st.markdown('<div class="section">', unsafe_allow_html=True)
    db = {"Phenytoin": {"Max": "600-1000 mg/d", "SE": "Gingival hyperplasia, Ataxia, Nystagmus."},
           "Valproic acid": {"Max": "60 mg/kg/d", "SE": "Hepatotoxicity, Weight gain, Hair loss."},
           "Carbamazepine": {"Max": "1600 mg/d", "SE": "Hyponatremia, Stevens-Johnson Syndrome."},
           "Levetiracetam": {"Max": "3000 mg/d", "SE": "Irritability, Somnolence, Fatigue."}}
    st.subheader(f"💊 {selected_drug} Monograph")
    k1, k2 = st.columns(2)
    with k1: st.write(f"**Max Dose:** {db[selected_drug]['Max']}")
    with k2: st.error(f"**Side Effects:** {db[selected_drug]['SE']}")
    st.markdown('</div>', unsafe_allow_html=True)

with tab4:
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center;'>📝 SOAP & Summary Presentation</h2>", unsafe_allow_html=True)
    soap = f"S: {age}Y patient, {weight}kg.\nO: CrCl {crcl:.1f}, SCr {scr}.\nA: Individually dosed {selected_drug}.\nP: LD {round(ld)}mg, MD {round(md)}mg q{interval}h."
    
    st.markdown(f'''
    <div style="background: #f8fafc; border-left: 5px solid #1e3a8a; padding: 25px; border-radius: 15px;">
        <p><b>S:</b> {age}Y {gender}, {weight}kg patient profile.</p>
        <p><b>O:</b> SCr {scr}mg/dL | CrCl {crcl:.1f}mL/min | {'Obese' if is_obese else 'Normal weight'}.</p>
        <p><b>A:</b> Dose optimization for {selected_drug} based on PK parameters.</p>
        <p><b>P:</b> Loading Dose <b>{round(ld)}mg</b>, MD <b>{round(md)}mg every {interval}h</b>.</p>
    </div>
    ''', unsafe_allow_html=True)
    
    st.download_button("📥 Save Detailed Report", create_pdf_report(age, weight, selected_drug, crcl, ld, md, interval, soap))
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<center>💙 **DoseWise** | MNU Faculty of Pharmacy</center>", unsafe_allow_html=True)
