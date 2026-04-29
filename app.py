import streamlit as st
import os
import base64
import math
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
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
        border: none;
    }}
    </style>
    ''', unsafe_allow_html=True)

# ==============================
# 📄 2. Professional PDF Report Generator
# ==============================
def create_pdf_report(age, weight, drug, crcl, ld, md, interval, soap_text="", peak=None, trough=None, vd=0, thalf=0):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    content = []
    content.append(Paragraph("DoseWise - Clinical PK Report", styles['Title']))
    content.append(Spacer(1, 20))
    
    data = [
        ["Patient Age", f"{age} Y", "Medication", drug],
        ["Total Weight", f"{weight} kg", "Est. CrCl", f"{crcl:.1f} mL/min"],
        ["Vd (L)", f"{vd:.1f} L", "t1/2 (h)", f"{thalf:.1f} h"]
    ]
    t = Table(data, colWidths=[100, 150, 100, 150])
    t.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), colors.whitesmoke), ('GRID', (0,0), (-1,-1), 0.5, colors.grey)]))
    content.append(t)
    
    content.append(Spacer(1, 25))
    content.append(Paragraph(f"<b>Final Regimen:</b> LD {round(ld)} mg | MD {round(md)} mg q{interval}h", styles['Heading2']))
    if peak:
        content.append(Paragraph(f"Steady State: Peak {peak:.2f} | Trough {trough:.2f}", styles['Normal']))
    
    content.append(Spacer(20, 20))
    content.append(Paragraph("<b>Clinical SOAP Note:</b>", styles['Heading3']))
    content.append(Paragraph(soap_text.replace('\n', '<br/>'), styles['Normal']))
    doc.build(content)
    return buffer.getvalue()

# ==============================
# ⚙️ 3. App Setup & Database
# ==============================
st.set_page_config(page_title="DoseWise | Clinical PK Platform", layout="wide")
set_page_style('bg.jpg' if os.path.exists("bg.jpg") else "")

st.markdown('<div class="hero">💊 DoseWise Platform</div>', unsafe_allow_html=True)

drug_db = {
    "Phenytoin": {"Max": "1000 mg/day", "Range": [10, 20], "SE": "Gingival hyperplasia, Ataxia, Nystagmus.", "Note": "Non-linear Michaelis-Menten kinetics.", "Decision": "⚠️ Capacity-limited metabolism. Monitor levels closely and check albumin status."},
    "Valproic acid": {"Max": "60 mg/kg/day", "Range": [50, 100], "SE": "Hepatotoxicity, Hair loss, Tremors.", "Note": "Highly protein bound.", "Decision": "⚠️ Highly protein-bound. Monitor LFTs and platelet count frequently."},
    "Carbamazepine": {"Max": "1600 mg/day", "Range": [4, 12], "SE": "SIADH, Stevens-Johnson Syndrome.", "Note": "Potent auto-induction risk.", "Decision": "⚠️ Risk of Auto-induction within 2-4 weeks. Monitor Na levels closely."},
    "Levetiracetam": {"Max": "3000 mg/day", "Range": [12, 46], "SE": "Irritability, Behavioral changes.", "Note": "Primarily renally cleared.", "Decision": "✅ Low drug-drug interaction risk. Dose adjustment for renal impairment required."}
}

tab1, tab2, tab3, tab4, tab5 = st.tabs(["🎯 Calculator", "📚 Drug Knowledge", "⚖️ Clinical Decision", "📋 Case Summary", "📝 SOAP Note"])

with tab1:
    st.markdown('<div class="section">', unsafe_allow_html=True)
    selected_drug = st.selectbox("Select Medication", list(drug_db.keys()))
    
    col_in, col_res = st.columns([1.3, 1])
    
    with col_in:
        c1, c2 = st.columns(2)
        with c1:
            age = st.number_input("Age (Years)", 1, 100, 30)
            weight = st.number_input("Weight (kg)", 10.0, 250.0, 70.0)
            height = st.number_input("Height (cm)", 50, 250, 170)
        with c2:
            gender = st.selectbox("Gender", ["Male", "Female"])
            scr = st.number_input("SCr (mg/dL)", 0.1, 10.0, 1.0)
            target = st.slider("Target Css (mg/L)", 2, 120, 15 if selected_drug != "Valproic acid" else 75)
        interval = st.selectbox("Interval (hr)", [4, 6, 8, 12, 24], index=3)

        # --- CALCULATIONS (Hidden Logic) ---
        height_m = height / 100
        ht_in = height / 2.54
        bmi = weight / (height_m ** 2)
        
        # IBW & AdjBW
        if gender == "Male":
            ibw = 50 + 2.3 * (ht_in - 60)
        else:
            ibw = 45.5 + 2.3 * (ht_in - 60)
        ibw = max(ibw, 35) 
        adjbw = ibw + 0.4 * (weight - ibw)
        
        # Renal Weight Selection Logic
        if bmi < 18.5:
            renal_weight = weight
            weight_note = "⚠️ Underweight → Actual BW used"
        elif bmi >= 30:
            renal_weight = adjbw
            weight_note = "⚠️ Obese → Adjusted BW used"
        else:
            renal_weight = ibw
            weight_note = "✅ Normal/Overweight → IBW used"

        # Cockcroft-Gault
        crcl = ((140 - age) * renal_weight) / (72 * max(scr, 0.1))
        if gender == "Female": crcl *= 0.85

        # BMI Category
        if bmi < 18.5: bmi_status = "Underweight"
        elif bmi < 25: bmi_status = "Normal"
        elif bmi < 30: bmi_status = "Overweight"
        elif bmi < 35: bmi_status = "Obesity Class I"
        elif bmi < 40: bmi_status = "Obesity Class II"
        else: bmi_status = "Obesity Class III"

        # Drug PK Logic
        dosing_weight = adjbw if bmi >= 30 else weight
        s_factor, albumin, vmax, km = 0.92, 4.4, 7.0, 4.0
        css_max, css_min = 0, 0 # placeholders

        if selected_drug == "Phenytoin":
            st.markdown("<h4 style='color:#1e3a8a;'>🧬 Phenytoin Parameters</h4>", unsafe_allow_html=True)
            cp1, cp2 = st.columns(2)
            with cp1:
                vmax = st.number_input("Vmax (mg/kg/day)", 1.0, 15.0, 7.0)
                albumin = st.number_input("Serum Albumin (g/dL)", 0.5, 6.0, 4.4)
            with cp2:
                km = st.number_input("Km (mg/L)", 1.0, 10.0, 4.0)
                salt = st.selectbox("Dosage Form (S)", ["Sodium (0.92)", "Acid (1.0)"])
            s_factor = 0.92 if "0.92" in salt else 1.0
            vd = 0.7 * dosing_weight; vmax_t = vmax * dosing_weight
            md = ((vmax_t * target) / (km + target)) / (24/interval)
            ld = target * vd
            k_el = (vmax_t / (km + target)) / vd; t_half = 0.693 / k_el
            css_max = (target / s_factor) + ((md * s_factor) / vd); css_min = css_max * math.exp(-k_el * interval)
        elif selected_drug == "Valproic acid":
            vd, cl = 0.15 * weight, 0.008 * weight
            k_el = cl/vd; ld, md = target*vd, target*cl*interval; t_half = 0.693/k_el
        else:
            vd, cl = 0.6 * weight, (crcl * 0.6) / 1000 * 60
            k_el = cl/vd; ld, md = target*vd, target*cl*interval; t_half = 0.693/k_el
        
        if selected_drug != "Phenytoin" and crcl < 50: md *= (crcl/100)
    
    with col_res:
        st.markdown("<h2 style='color:#1e293b;'>📊 Analysis Panel</h2>", unsafe_allow_html=True)
        calc_pressed = st.button("🚀 Calculate Regimen & Assessment")
        
        if calc_pressed:
            st.markdown("### 🧬 Patient Metrics")
            rm1, rm2, rm3 = st.columns(3)
            rm1.metric("BMI", f"{bmi:.1f}")
            rm2.metric("IBW", f"{ibw:.1f}kg")
            rm3.metric("CrCl", f"{crcl:.1f}")
            
            st.info(f"**BMI Status:** {bmi_status}")
            st.info(weight_note)
            
            if crcl >= 90: st.success("🟢 Normal renal function")
            elif crcl >= 60: st.info("🟡 Mild impairment")
            elif crcl >= 30: st.warning("🟠 Moderate impairment")
            elif crcl >= 15: st.warning("🔴 Severe impairment")
            else: st.error("⚫ Kidney failure")

            st.divider()
            st.markdown("### 💊 PK Results")
            col_pk1, col_pk2 = st.columns(2)
            col_pk1.metric("Vd (Volume)", f"{vd:.1f} L")
            col_pk2.metric("t½ (Half-life)", f"{t_half:.1f} h")
            
            st.success(f"**Plan:** LD {round(ld)}mg | MD {round(md)}mg q{interval}h")
            
            # TDM Guard
            low_r, high_r = drug_db[selected_drug]["Range"]
            if target > high_r:
                st.error(f"⚠️ Warning: Target ({target}) is ABOVE therapeutic range ({low_r}-{high_r})")
            elif target < low_r:
                st.warning(f"⚠️ Caution: Target ({target}) is BELOW therapeutic range ({low_r}-{high_r})")
            else:
                st.success(f"✅ Target within Therapeutic Range ({low_r}-{high_r})")
            
            # PDF Download
            soap_text = f"S: {age}Y patient. O: CrCl {crcl:.1f}mL/min, BMI {bmi:.1f}. A: PK optimized for {selected_drug}. P: LD {round(ld)}mg, MD {round(md)}mg q{interval}h."
            pdf_bytes = create_pdf_report(age, weight, selected_drug, crcl, ld, md, interval, soap_text, (css_max if selected_drug=="Phenytoin" else None), (css_min if selected_drug=="Phenytoin" else None), vd, t_half)
            st.download_button("📥 Download PK Report", pdf_bytes, f"Report_{selected_drug}.pdf")
        else:
            st.info("👈 Enter patient details and click Calculate to generate results.")
    st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    st.markdown('<div class="section">', unsafe_allow_html=True)
    db = drug_db[selected_drug]
    st.subheader(f"📚 {selected_drug} Monograph")
    k1, k2 = st.columns(2)
    with k1: 
        st.write(f"**Target Range:** {db['Range'][0]} - {db['Range'][1]} mg/L")
        st.write(f"**Max Recommended:** {db['Max']}")
        st.write(f"**Clinical Note:** {db['Note']}")
    with k2: st.error(f"**Major Side Effects:** {db['SE']}")
    st.markdown('</div>', unsafe_allow_html=True)

with tab3:
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.subheader("⚖️ Clinical Decision Support")
    st.info(f"**Expert Clinical Opinion:** {drug_db[selected_drug]['Decision']}")
    if bmi >= 30: st.error(f"❗ **Obesity Alert:** Calculations adjusted for body mass index.")
    if crcl < 50: st.warning(f"⚠️ **Renal Dose Adjustment:** Dose reduction applied due to CrCl < 50 mL/min.")
    if selected_drug == "Phenytoin" and albumin < 4.4:
        adj_target = target / ((0.2 * albumin) + 0.1)
        st.warning(f"💡 **Albumin Correction:** Corrected Target Css is {adj_target:.1f} mg/L.")
    st.markdown('</div>', unsafe_allow_html=True)

with tab4:
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center; color:#1e3a8a;'>📋 Case Summary</h2>", unsafe_allow_html=True)
    st.table({
        "Clinical Parameter": ["Age", "BMI Category", "IBW", "Est. CrCl", "Vd", "t½ (Half-life)"], 
        "Value": [f"{age} Y", f"{bmi_status}", f"{ibw:.1f} kg", f"{crcl:.1f} mL/min", f"{vd:.1f} L", f"{t_half:.1f} h"]
    })
    st.markdown('</div>', unsafe_allow_html=True)

with tab5:
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center; color:#1e3a8a;'>📝 Professional SOAP Note</h2>", unsafe_allow_html=True)
    st.markdown(f'''
    <div style="background-color: #f0f4f8; padding: 25px; border-radius: 12px; border-left: 10px solid #1e3a8a;">
        <p><b>Subjective:</b> Patient is a {age}-year-old {gender.lower()} presenting for {selected_drug} titration.</p>
        <p><b>Objective:</b> Weight {weight}kg | CrCl {crcl:.1f}mL/min | BMI {bmi:.1f} ({bmi_status}).</p>
        <p><b>Assessment:</b> PK regimen designed for target of {target} mg/L considering current renal and metabolic status.</p>
        <p><b>Plan:</b> Initiate LD <b>{round(ld)}mg</b>, followed by MD <b>{round(md)}mg q{interval}h</b>. Monitor for {db['SE']}.</p>
    </div>
    ''', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<br><center>💙 **DoseWise** | MNU Faculty of Pharmacy | Project by Team 2</center>", unsafe_allow_html=True)
