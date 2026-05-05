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
    
    content.append(Spacer(20, 20))
    content.append(Paragraph("<b>Clinical SOAP Note:</b>", styles['Heading3']))
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
    "Phenytoin": {"Max": "1000 mg/day", "Range": "10-20 mg/L", "SE": "Gingival hyperplasia, Ataxia, Nystagmus.", "Note": "Non-linear Michaelis-Menten kinetics.", "Decision": "⚠️ Capacity-limited metabolism detected. Monitor levels closely and check albumin status."},
    "Valproic acid": {"Max": "60 mg/kg/day", "Range": "50-100 mg/L", "SE": "Hepatotoxicity, Hair loss, Tremors.", "Note": "Highly protein bound.", "Decision": "⚠️ Highly protein-bound drug. Monitor LFTs and platelet count frequently."},
    "Carbamazepine": {"Max": "1600 mg/day", "Range": "4-12 mg/L", "SE": "SIADH, Stevens-Johnson Syndrome.", "Note": "Potent auto-induction risk.", "Decision": "⚠️ Risk of Auto-induction within 2-4 weeks. Monitor Na levels closely."},
    "Levetiracetam": {"Max": "3000 mg/day", "Range": "12-46 mg/L", "SE": "Irritability, Behavioral changes.", "Note": "Primarily renally cleared.", "Decision": "✅ Low drug-drug interaction risk. Mandatory dose adjustment for renal impairment."}
}

tab1, tab2, tab3, tab4, tab5 = st.tabs(["🎯 Calculator", "📚 Drug Knowledge", "⚖️ Clinical Decision", "📋 Case Summary", "📝 SOAP Note"])

with tab1:
    st.markdown('<div class="section">', unsafe_allow_html=True)
    selected_drug = st.selectbox("Select Medication", list(drug_db.keys()))
    col_in, col_res = st.columns([1.3, 1.2])
    
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

        # Body Metrics
        height_m = height / 100
        ht_in = height / 2.54
        bmi = weight / (height_m ** 2)
        if gender == "Male": ibw = 50 + 2.3 * (ht_in - 60)
        else: ibw = 45.5 + 2.3 * (ht_in - 60)
        ibw = max(ibw, 35); adjbw = ibw + 0.4 * (weight - ibw)

        if bmi < 18.5: renal_weight = weight; weight_note = "⚠️ Underweight → Actual BW used"
        elif bmi >= 30: renal_weight = adjbw; weight_note = "⚠️ Obese → Adjusted BW used"
        else: renal_weight = ibw; weight_note = "✅ Normal/Overweight → IBW used"

        crcl = ((140 - age) * renal_weight) / (72 * scr)
        if gender == "Female": crcl *= 0.85
        bmi_status = "Underweight" if bmi < 18.5 else ("Normal" if bmi < 25 else ("Overweight" if bmi < 30 else "Obese"))
        dosing_weight = adjbw if bmi >= 30 else weight

        if selected_drug == "Phenytoin":
            st.markdown("---")
            st.markdown("### 🧪 Free Phenytoin Assessment (Inputs)")
            total_phenytoin = st.number_input("Total Phenytoin Level", value=7.50)
            valproic_level = st.number_input("Valproic Acid Level", value=100.00)
            st.markdown("---")
            st.subheader("🧬 Phenytoin Advanced Parameters")
            cp1, cp2 = st.columns(2)
            with cp1:
                vmax = st.number_input("Vmax (mg/kg/day)", 1.0, 15.0, 7.0)
                km = st.number_input("Km (mg/L)", 1.0, 10.0, 4.0)
            with cp2:
                albumin_val = st.number_input("Serum Albumin (g/dL)", 0.5, 6.0, 4.4)
                salt = st.selectbox("Dosage Form (S)", ["Sodium (0.92)", "Acid (1.0)"])
            s_factor = 0.92 if "Sodium" in salt else 1.0

        # Calculation Logic
        if selected_drug == "Phenytoin":
            vd = 0.7 * dosing_weight
            vmax_t = vmax * dosing_weight
            md = ((vmax_t * target) / (km + target)) / (24/interval)
            ld = target * vd
            t_half = (0.693 * vd * (km + target)) / vmax_t
            k_el = 0.693 / t_half
            css_max = (target / s_factor) + ((md * s_factor) / vd)
            css_min = css_max * math.exp(-k_el * interval)
        elif selected_drug == "Valproic acid":
            vd, cl = 0.15 * weight, 0.008 * weight
            ld, md = target*vd, target*cl*interval
            k_el = cl/vd; t_half = 0.693/k_el
        else: # Carbamazepine & Levetiracetam
            vd, cl = 0.6 * weight, (crcl * 0.6) / 1000 * 60
            ld, md = target*vd, target*cl*interval
            k_el = cl/vd; t_half = 0.693/k_el

        if selected_drug != "Phenytoin" and crcl < 50: md *= (crcl/100)

        calculate_btn = st.button("🚀 Calculate Clinical Plan")

    with col_res:
        if calculate_btn:
            st.markdown("<h2 style='color:#1e293b;'>📊 Analysis Results</h2>", unsafe_allow_html=True)
            if selected_drug == "Phenytoin":
                st.markdown("### 🧪 Free Concentration Assessment")
                f_frac = 0.1 + (0.001 * valproic_level)
                e_free = total_phenytoin * f_frac
                st.metric("Estimated Free Phenytoin", f"{e_free:.2f} mcg/mL")
                if 1 <= e_free <= 2: 
                    st.success("✅ Free level therapeutic. No dose adjustment required.")
                elif e_free < 1: st.warning("⚠️ Subtherapeutic level.")
                else: st.error("🚨 Toxicity risk detected.")
                st.divider()

            st.markdown("### 📊 Body & Renal Assessment")
            r1, r2, r3 = st.columns(3)
            r1.metric("BMI", f"{bmi:.1f}"); r2.metric("IBW", f"{ibw:.1f} kg"); r3.metric("CrCl", f"{crcl:.1f}")
            st.info(f"**Status:** {bmi_status} | {weight_note}")
            st.divider()
            st.success(f"**Final Regimen:** LD {round(ld)}mg | MD {round(md)}mg q{interval}h")
            pk_1, pk_2 = st.columns(2)
            pk_1.metric("Vd (L)", f"{vd:.1f}"); pk_2.metric("t½ (h)", f"{t_half:.1f}")

            full_soap = f"Subjective: Patient is a {age}Y {gender.lower()} for {selected_drug} management.\nObjective: Wt {weight}kg | BMI {bmi:.1f} | CrCl {crcl:.1f}mL/min.\nAssessment: Optimized for {selected_drug} kinetics.\nPlan: LD {round(ld)}mg, MD {round(md)}mg q{interval}h."
            pdf_raw = create_pdf_report(age, weight, selected_drug, crcl, ld, md, interval, full_soap, None, None, vd, t_half)
            st.download_button("📥 Download Report", pdf_raw, f"DoseWise_{selected_drug}.pdf")
        else:
            st.info("👈 Fill data and click Calculate.")
    st.markdown('</div>', unsafe_allow_html=True)

# Tabs
with tab2:
    if calculate_btn:
        st.subheader(f"📚 {selected_drug} Knowledge")
        st.write(f"**Target:** {drug_db[selected_drug]['Range']}")
        st.error(f"**Side Effects:** {drug_db[selected_drug]['SE']}")
    else: st.warning("Calculate first.")

with tab3:
    if calculate_btn:
        st.info(f"**Decision Support:** {drug_db[selected_drug]['Decision']}")
        if selected_drug == "Phenytoin" and 1 <= (total_phenytoin * (0.1 + (0.001 * valproic_level))) <= 2:
            st.success("✅ **Clinical Decision:** No dose adjustment required.")
    else: st.warning("Calculate first.")

with tab4:
    if calculate_btn:
        st.table({"Clinical Parameter": ["Age", "BMI Status", "IBW", "AdjBW", "CrCl", "Vd", "t½"], 
                  "Value": [f"{age}", bmi_status, f"{ibw:.1f} kg", f"{adjbw:.1f} kg", f"{crcl:.1f}", f"{vd:.1f} L", f"{t_half:.1f} h"]})
    else: st.warning("Calculate first.")

with tab5:
    if calculate_btn:
        st.markdown(f'''
        <div style="background-color: #f0f4f8; padding: 25px; border-radius: 12px; border-left: 10px solid #1e3a8a;">
            <p><b>Subjective:</b> Patient is a {age}-year-old {gender.lower()} presenting for {selected_drug} management.</p>
            <p><b>Objective:</b> Weight {weight}kg | BMI {bmi:.1f} | CrCl {crcl:.1f}mL/min | Vd {vd:.1f}L | t½ {t_half:.1f}h.</p>
            <p><b>Assessment:</b> PK regimen optimized for {selected_drug} considering weight and renal status.</p>
            <p><b>Plan:</b> Administer LD <b>{round(ld)}mg</b> then MD <b>{round(md)}mg q{interval}h</b>. Monitor for {drug_db[selected_drug]['SE']}.</p>
        </div>
        ''', unsafe_allow_html=True)
    else: st.warning("Calculate first.")

st.markdown("<br><center>💙 **DoseWise** | MNU Faculty of Pharmacy | Team 2</center>", unsafe_allow_html=True)
