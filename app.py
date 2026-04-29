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
        background-size: cover; background-attachment: fixed;
    }}
    .hero {{
        background: linear-gradient(135deg, #1e3a8a, #3b82f6);
        padding: 30px; border-radius: 20px; text-align: center;
        color: white; font-size: 38px; font-weight: 900;
        box-shadow: 0 10px 25px rgba(0,0,0,0.2); margin-bottom: 25px;
    }}
    .section {{
        background: rgba(255,255,255,0.95); padding: 25px;
        border-radius: 15px; margin-top: 20px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.05); border: 1px solid #e2e8f0;
    }}
    .stButton>button {{
        background: linear-gradient(45deg, #1e3a8a, #3b82f6);
        color: white; border-radius: 30px; height: 3.5em;
        width: 100%; font-weight: bold; transition: 0.3s; border: none;
    }}
    </style>
    ''', unsafe_allow_html=True)

# ==============================
# 📄 2. PDF Report Generator
# ==============================
def create_pdf_report(age, weight, drug, crcl, ld, md, interval, soap_text, vd, thalf, c_est=None):
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
    if c_est: data.append(["Est. Css", f"{c_est:.2f} mg/L", "", ""])
    
    t = Table(data, colWidths=[100, 150, 100, 150])
    t.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), colors.whitesmoke), ('GRID', (0,0), (-1,-1), 0.5, colors.grey)]))
    content.append(t)
    content.append(Spacer(1, 25))
    content.append(Paragraph(f"<b>Regimen:</b> LD {round(ld)} mg | MD {round(md)} mg q{interval}h", styles['Heading2']))
    content.append(Spacer(20, 20))
    content.append(Paragraph("<b>Clinical Note:</b>", styles['Heading3']))
    content.append(Paragraph(soap_text.replace('\n', '<br/>'), styles['Normal']))
    doc.build(content)
    return buffer.getvalue()

# ==============================
# ⚙️ 3. App Setup & Logic
# ==============================
st.set_page_config(page_title="DoseWise | Clinical PK Platform", layout="wide")
set_page_style('bg.jpg' if os.path.exists("bg.jpg") else "")
st.markdown('<div class="hero">💊 DoseWise Platform</div>', unsafe_allow_html=True)

drug_db = {
    "Phenytoin": {"Range": "10-20 mg/L", "Max": "1000 mg/day", "Decision": "Non-linear Michaelis-Menten kinetics."},
    "Valproic acid": {"Range": "50-100 mg/L", "Max": "60 mg/kg/day", "Decision": "Highly protein bound."},
    "Carbamazepine": {"Range": "4-12 mg/L", "Max": "1600 mg/day", "Decision": "Auto-induction risk."},
    "Levetiracetam": {"Range": "12-46 mg/L", "Max": "3000 mg/day", "Decision": "Renally cleared."}
}

tab1, tab2, tab3, tab4, tab5 = st.tabs(["🎯 Calculator", "📚 Drug Knowledge", "⚖️ Clinical Decision", "📋 Case Summary", "📝 SOAP Note"])

with tab1:
    st.markdown('<div class="section">', unsafe_allow_html=True)
    selected_drug = st.selectbox("Select Medication", list(drug_db.keys()))
    
    col_in, col_res = st.columns([1.3, 1])
    
    with col_in:
        # --- Input Section ---
        c1, c2 = st.columns(2)
        with c1:
            age = st.number_input("Age", 1, 100, 30)
            weight = st.number_input("Weight (kg)", 10.0, 250.0, 70.0)
            height = st.number_input("Height (cm)", 50, 250, 170)
        with c2:
            gender = st.selectbox("Gender", ["Male", "Female"])
            scr = st.number_input("SCr (mg/dL)", 0.1, 10.0, 1.0)
            target = st.slider("Target Css (mg/L)", 5, 120, 15 if selected_drug != "Valproic acid" else 75)
        interval = st.selectbox("Interval (hr)", [4, 6, 8, 12, 24], index=3)

        # --- Body Metrics Logic ---
        height_m = height / 100; ht_in = height / 2.54; bmi = weight / (height_m ** 2)
        if gender == "Male": ibw = 50 + 2.3 * (ht_in - 60)
        else: ibw = 45.5 + 2.3 * (ht_in - 60)
        ibw = max(ibw, 35); adjbw = ibw + 0.4 * (weight - ibw)

        # Renal Weight Selection
        if bmi < 18.5: renal_weight, weight_note = weight, "⚠️ Underweight → Actual BW used"
        elif bmi >= 30: renal_weight, weight_note = adjbw, "⚠️ Obese → Adjusted BW used"
        else: renal_weight, weight_note = ibw, "✅ Normal/Overweight → IBW used"

        crcl = ((140 - age) * renal_weight) / (72 * max(scr, 0.1))
        if gender == "Female": crcl *= 0.85
        
        bmi_status = "Underweight" if bmi < 18.5 else "Normal" if bmi < 25 else "Overweight" if bmi < 30 else "Obese"

        # --- PK Regimen Logic ---
        dosing_weight = adjbw if bmi >= 30 else weight
        c_estimated = None
        
        if selected_drug == "Phenytoin":
            st.markdown("---")
            st.markdown("### 🧬 Phenytoin Assessment")
            cp1, cp2 = st.columns(2)
            with cp1:
                vmax = st.number_input("Vmax (mg/kg/day)", 1.0, 15.0, 7.0)
                albumin = st.number_input("Serum Albumin (g/dL)", 0.5, 6.0, 4.4)
            with cp2:
                km = st.number_input("Km (mg/L)", 1.0, 10.0, 4.0)
                salt = st.selectbox("Dosage Form (S)", ["Sodium (0.92)", "Acid (1.0)"])
            
            s_factor = 0.92 if "0.92" in salt else 1.0
            vmax_t = vmax * dosing_weight
            daily_dose = (vmax_t * target) / (km + target)
            md = daily_dose / (24/interval)
            ld = target * 0.7 * dosing_weight
            vd = 0.7 * dosing_weight
            k_el = (vmax_t / (km + target)) / vd; t_half = 0.693 / k_el
            
            # 🔥 Calculation of C estimated (Total Css)
            c_estimated = (km * (daily_dose/s_factor)) / (vmax_t - (daily_dose/s_factor))

            # --- Phenytoin Free level Case ---
            st.markdown("### 🧪 Free Phenytoin Assessment")
            total_pheny = st.number_input("Total Phenytoin Level", 0.0, 50.0, 7.5)
            valp_level = st.number_input("Valproic Acid Level", 0.0, 250.0, 100.0)
            f_fraction = 0.1 + (0.001 * valp_level)
            est_free = total_pheny * f_fraction
        else:
            if selected_drug == "Valproic acid":
                vd, cl = 0.15 * weight, 0.008 * weight
            else: # Carbamazepine & Levetiracetam
                vd, cl = 0.6 * weight, (crcl * 0.6) / 1000 * 60
            k_el = cl/vd; ld, md = target*vd, target*cl*interval; t_half = 0.693/k_el
            if crcl < 50: md *= (crcl/100) # Renal adjustment

    with col_res:
        st.markdown("<h2 style='color:#1e293b;'>📊 Assessment Results</h2>", unsafe_allow_html=True)
        calculate_btn = st.button("🚀 Run Calculation")

        if calculate_btn:
            # 1. Body & Renal
            st.markdown("### 🧬 Body & Renal")
            r1, r2, r3 = st.columns(3)
            r1.metric("BMI", f"{bmi:.1f}"); r2.metric("IBW", f"{ibw:.1f}kg"); r3.metric("CrCl", f"{crcl:.1f}")
            st.info(f"**Status:** {bmi_status} | {weight_note}")
            
            if crcl >= 90: st.success("🟢 Normal Renal Function")
            elif crcl >= 15: st.warning("🟠 Moderate/Severe Impairment")
            else: st.error("🔴 Renal Failure")

            st.divider()
            # 2. PK Plan
            st.markdown("### 📋 Clinical Regimen")
            st.success(f"**Plan:** LD {round(ld)}mg | MD {round(md)}mg q{interval}h")
            
            if selected_drug == "Phenytoin":
                st.metric("C estimated (Total Css)", f"{c_estimated:.2f} mg/L")
                st.divider()
                st.metric("Estimated Free Phenytoin", f"{est_free:.2f} mcg/mL")
                if 1 <= est_free <= 2: st.success("✅ Free Level Therapeutic")
                else: st.error("🚨 Free Level Toxic or Subtherapeutic!")

            # 3. TDM Guard
            st.markdown("### 💊 TDM Guard")
            ranges = {"Phenytoin": 20, "Valproic acid": 100, "Carbamazepine": 12, "Levetiracetam": 46}
            if target > ranges[selected_drug]: st.error(f"🚨 Target exceeds limit ({ranges[selected_drug]})")
            else: st.success(f"✅ Target within Therapeutic Range")

            # PDF Download
            soap_txt = f"S: {age}Y patient. O: BMI {bmi:.1f}, CrCl {crcl:.1f}. A: Regimen for {selected_drug}. P: LD {round(ld)}mg, MD {round(md)}mg."
            pdf_bytes = create_pdf_report(age, weight, selected_drug, crcl, ld, md, interval, soap_txt, vd, t_half, c_estimated)
            st.download_button("📥 Download PK Report", pdf_bytes, f"DoseWise_{selected_drug}.pdf")
        else:
            st.info("💡 Fill the patient info and click Calculate to see the clinical analysis.")

# --- Remaining Tabs ---
with tab2:
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.subheader(f"📚 {selected_drug} Monograph")
    st.write(f"**Target Range:** {drug_db[selected_drug]['Range']}")
    st.write(f"**Max Dose:** {drug_db[selected_drug]['Max']}")
    st.markdown('</div>', unsafe_allow_html=True)

with tab3:
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.info(f"**Expert Clinical Note:** {drug_db[selected_drug]['Decision']}")
    st.markdown('</div>', unsafe_allow_html=True)

with tab4:
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.table({"Clinical Parameter": ["Age", "BMI", "CrCl", "IBW"], "Value": [f"{age} Y", f"{bmi:.1f}", f"{crcl:.1f}", f"{ibw:.1f} kg"]})
    st.markdown('</div>', unsafe_allow_html=True)

with tab5:
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.markdown(f"**SOAP Plan:** Administer LD {round(ld)}mg then MD {round(md)}mg q{interval}h.")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<center>💙 **DoseWise** | MNU Pharmacy Team 2</center>", unsafe_allow_html=True)
