import streamlit as st
import os
import base64
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

# ==============================
# 🎨 Page Style (Premium UI)
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
        background-image: linear-gradient(rgba(255,255,255,0.8), rgba(255,255,255,0.8)), {bg_img};
        background-size: cover;
    }}

    .hero {{
        background: linear-gradient(135deg, #1e3a8a, #3b82f6);
        padding: 25px;
        border-radius: 20px;
        text-align: center;
        color: white;
        font-size: 32px;
        font-weight: bold;
        box-shadow: 0 10px 25px rgba(0,0,0,0.2);
    }}

    .section {{
        background: rgba(255,255,255,0.9);
        padding: 20px;
        border-radius: 15px;
        margin-top: 15px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }}

    .stButton>button {{
        background: linear-gradient(45deg, #1e3a8a, #3b82f6);
        color: white;
        border-radius: 30px;
        height: 3em;
        width: 100%;
        font-weight: bold;
    }}
    </style>
    ''', unsafe_allow_html=True)

# ==============================
# ⚙️ Config
# ==============================
st.set_page_config(page_title="AED PK Pro", layout="wide")
set_page_style('bg.jpg' if os.path.exists("bg.jpg") else "")

# ==============================
# 🏷️ Header
# ==============================
st.markdown('<div class="hero">💊Dose wise</div>', unsafe_allow_html=True)

# ==============================
# 📄 PDF Generation Function
# ==============================
def generate_pdf(age, weight, drug, crcl, ld, md, interval):
    doc = SimpleDocTemplate("PK_Report.pdf")
    styles = getSampleStyleSheet()
    content = []

    content.append(Paragraph("AED PK Clinical Report", styles['Title']))
    content.append(Spacer(1, 12))
    content.append(Paragraph(f"Patient Age: {age}", styles['Normal']))
    content.append(Paragraph(f"Weight: {weight} kg", styles['Normal']))
    content.append(Paragraph(f"Drug: {drug}", styles['Normal']))
    content.append(Spacer(1, 12))
    content.append(Paragraph(f"Creatinine Clearance: {crcl:.2f} mL/min", styles['Normal']))
    content.append(Paragraph(f"Loading Dose: {round(ld)} mg", styles['Normal']))
    content.append(Paragraph(f"Maintenance Dose: {round(md)} mg every {interval} hr", styles['Normal']))
    content.append(Spacer(1, 12))
    content.append(Paragraph("Clinical Note:", styles['Heading2']))
    content.append(Paragraph("Dose adjusted based on renal function and PK parameters.", styles['Normal']))
    doc.build(content)

# ==============================
# 📑 Tabs (Website Style)
# ==============================
tab1, tab2, tab3, tab4 = st.tabs([
    "💊 PK Calculator",
    "🧠 Drug Knowledge",
    "🛡️ Clinical Decision",
    "📊 Case Presentation"
])

# ==============================
# 💊 TAB 1: PK CALCULATOR
# ==============================
with tab1:
    st.markdown('<div class="section">', unsafe_allow_html=True)

    selected_drug = st.selectbox("Select Drug", [
        "Phenytoin", "Valproic acid", "Carbamazepine", "Levetiracetam"
    ])

    col1, col2 = st.columns(2)

    with col1:
        age = st.number_input("Age", 1, 100, 30)
        weight = st.number_input("Weight (kg)", 10.0, 150.0, 70.0)
        height = st.number_input("Height (cm)", 50, 250, 170)

    with col2:
        gender = st.selectbox("Gender", ["Male", "Female"])
        scr = st.number_input("Serum Creatinine", 0.1, 5.0, 1.0)
        target = st.slider("Target Concentration", 5, 100, 15)

    interval = st.selectbox("Dosing Interval", [4, 6, 8, 12, 24], index=3)

    # ==============================
    # 🧮 Calculations (Corrected Scientific Logic)
    # ==============================
    if gender == "Male":
        crcl = ((140 - age) * weight) / (72 * scr)
    else:
        crcl = ((140 - age) * weight) / (72 * scr) * 0.85

    if selected_drug == "Phenytoin":
        vd = 0.7 * weight
        vmax = 7 * weight  # mg/kg/day
        km = 4             # mg/L
        ld = target * vd
        daily_md = (vmax * target) / (km + target)
        md = daily_md / (24 / interval)
        k = 0.03 # Approx for t1/2 display

    elif selected_drug == "Valproic acid":
        vd = 0.15 * weight
        cl = 0.008 * weight # L/hr
        k = cl / vd
        ld = target * vd
        md = target * cl * interval

    elif selected_drug == "Carbamazepine":
        vd = 1.4 * weight
        cl = 0.06 * weight # L/hr
        k = cl / vd
        ld = target * vd
        md = target * cl * interval

    else: # Levetiracetam
        vd = 0.6 * weight
        cl = (crcl * 0.6) / 1000 * 60 # Cl in L/hr
        k = cl / vd
        ld = target * vd
        md = target * cl * interval

    t_half = 0.693 / k if k > 0 else 0

    # Renal Adjustment (Except for Phenytoin/Non-renally cleared)
    if selected_drug != "Phenytoin" and crcl < 50:
        md = md * (crcl / 100)

    # ==============================
    # 📊 Results
    # ==============================
    if st.button("🚀 Generate Plan"):
        col_res1, col_res2, col_res3, col_res4 = st.columns(4)

        col_res1.metric("CrCl", f"{crcl:.1f}")
        col_res2.metric("Vd (L)", f"{vd:.2f}")
        col_res3.metric("Cl (L/h)", f"{cl:.2f}" if selected_drug != "Phenytoin" else "N/A")
        col_res4.metric("t½ (h)", f"{t_half:.2f}" if selected_drug != "Phenytoin" else "N/A")

        st.success(f"""
        ✅ **Final Regimen**
        - Loading Dose: {round(ld)} mg
        - Maintenance Dose: {round(md)} mg every {interval} hr
        """)

        if crcl < 50:
            st.warning("⚠️ Dose adjusted due to renal impairment")

        # ==============================
        # PDF Button
        # ==============================
        if st.button("📄 Generate PDF Report"):
            generate_pdf(age, weight, selected_drug, crcl, ld, md, interval)
            with open("PK_Report.pdf", "rb") as file:
                st.download_button(
                    label="⬇️ Download Report",
                    data=file,
                    file_name="PK_Report.pdf",
                    mime="application/pdf"
                )

    st.markdown('</div>', unsafe_allow_html=True)

# ==============================
# 🧠 TAB 2: DRUG KNOWLEDGE
# ==============================
with tab2:
    st.markdown('<div class="section">', unsafe_allow_html=True)

    drug_data = {
        "Phenytoin": ("Na channel blocker", "10-20 mg/L", "Non-linear kinetics"),
        "Valproic acid": ("GABA enhancer", "50-100 mg/L", "Hepatotoxic"),
        "Carbamazepine": ("Na channel blocker", "4-12 mg/L", "Autoinduction"),
        "Levetiracetam": ("SV2A modulator", "12-46 mg/L", "Behavioral effects")
    }

    mech, tdm, note = drug_data[selected_drug]

    st.subheader(selected_drug)
    st.write(f"**Mechanism:** {mech}")
    st.write(f"**TDM Range:** {tdm}")
    st.write(f"**Key Note:** {note}")

    st.markdown('</div>', unsafe_allow_html=True)

# ==============================
# 🛡️ TAB 3: CLINICAL DECISION
# ==============================
with tab3:
    st.markdown('<div class="section">', unsafe_allow_html=True)

    st.subheader("Clinical Reasoning")

    st.write("### 📌 Mathematical Output")
    st.write(f"- Maintenance Dose: {round(md)} mg every {interval} hr")

    st.write("### 🧠 Clinical Recommendation")
    if selected_drug == "Phenytoin":
        st.warning("Avoid rapid dose increase (Non-linear toxicity risk)")

    if crcl < 50:
        st.warning("Renal impairment detected → dose reduction applied")

    st.write("### 🔬 TDM Link")
    st.write("Measure drug levels after 4–5 half-lives to ensure steady state.")

    st.markdown('</div>', unsafe_allow_html=True)

# ==============================
# 📊 TAB 4: CASE PRESENTATION
# ==============================
with tab4:
    st.markdown('<div class="section">', unsafe_allow_html=True)

    st.subheader("Clinical Case Summary")

    st.write(f"""
    **Patient Profile:**
    - Age: {age} Years
    - Weight: {weight} kg
    - Selected Drug: {selected_drug}

    **Pharmacokinetic Analysis:**
    - Estimated CrCl: {crcl:.1f} mL/min
    - Volume of Distribution (Vd): {vd:.2f} L
    
    **Final Regimen:**
    - Recommended LD: {round(ld)} mg
    - Recommended MD: {round(md)} mg every {interval} hr

    **Clinical Rationale:**
    Dose calculation is individualized based on population PK parameters and renal clearance.
    """)

    st.markdown('</div>', unsafe_allow_html=True)

# ==============================
# Footer
# ==============================
st.markdown("<center>💙 Clinical PK Project | MNU</center>", unsafe_allow_html=True)
