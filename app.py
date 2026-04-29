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
        background-image: linear-gradient(rgba(255, 255, 255, 0.92), rgba(255, 255, 255, 0.92)), {bg_img};
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
    .stMetric {{
        background: #f8fafc;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #e2e8f0;
    }}
    </style>
    ''', unsafe_allow_html=True)

# ==============================
# 📄 2. Professional PDF Report Generator
# ==============================
def create_pdf_report(age, weight, drug, crcl, ld, md, interval, soap_text, vd=0, thalf=0):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    content = []
    content.append(Paragraph("DoseWise - Clinical PK Report", styles['Title']))
    content.append(Spacer(1, 20))
    
    data = [
        ["Age", f"{age} Y", "Medication", drug],
        ["Weight", f"{weight} kg", "Est. CrCl", f"{crcl:.1f} mL/min"],
        ["Vd (L)", f"{vd:.1f} L", "t1/2 (h)", f"{thalf:.1f} h"]
    ]
    t = Table(data, colWidths=[100, 150, 100, 150])
    t.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), colors.whitesmoke), ('GRID', (0,0), (-1,-1), 0.5, colors.grey)]))
    content.append(t)
    
    content.append(Spacer(1, 25))
    content.append(Paragraph(f"<b>Final Regimen:</b> LD {round(ld)} mg | MD {round(md)} mg q{interval}h", styles['Heading2']))
    content.append(Spacer(20, 20))
    content.append(Paragraph("<b>Clinical Assessment:</b>", styles['Heading3']))
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
    "Phenytoin": {"Max": "1000 mg/day", "Range": "10-20 mg/L", "SE": "Ataxia, Nystagmus, Gingival hyperplasia.", "Decision": "⚠️ Capacity-limited kinetics. Check albumin and VPA interaction."},
    "Valproic acid": {"Max": "60 mg/kg/day", "Range": "50-100 mg/L", "SE": "Hepatotoxicity, Thrombocytopenia.", "Decision": "⚠️ Highly protein-bound. Monitor LFTs."},
    "Carbamazepine": {"Max": "1600 mg/day", "Range": "4-12 mg/L", "SE": "SIADH, Rash, Leukopenia.", "Decision": "⚠️ Auto-induction risk (2-4 weeks)."},
    "Levetiracetam": {"Max": "3000 mg/day", "Range": "12-46 mg/L", "SE": "Irritability, Somnolence.", "Decision": "✅ Wide safety margin. Renal dose adjustment required."}
}

tab1, tab2, tab3, tab4 = st.tabs(["🎯 Calculator", "📚 Drug Info", "📋 Case Summary", "📝 SOAP Note"])

with tab1:
    col_in, col_res = st.columns([1.3, 1])
    
    with col_in:
        st.markdown('<div class="section">', unsafe_allow_html=True)
        selected_drug = st.selectbox("Select Medication", list(drug_db.keys()))
        
        c1, c2 = st.columns(2)
        with c1:
            age = st.number_input("Age (Years)", 1, 100, 30)
            weight = st.number_input("Weight (kg)", 10.0, 250.0, 70.0)
            height = st.number_input("Height (cm)", 50, 250, 170)
        with c2:
            gender = st.selectbox("Gender", ["Male", "Female"])
            scr = st.number_input("SCr (mg/dL)", 0.1, 8.0, 1.0)
            target = st.slider("Target Css (mg/L)", 5, 100, 15 if selected_drug != "Valproic acid" else 75)
        
        interval = st.selectbox("Dosing Interval (hr)", [4, 6, 8, 12, 24], index=3)
        
        # --- Calculations Core ---
        height_m = height / 100
        ht_in = height / 2.54
        bmi = weight / (height_m ** 2)
        
        if gender == "Male":
            ibw = 50 + 2.3 * (ht_in - 60)
        else:
            ibw = 45.5 + 2.3 * (ht_in - 60)
        ibw = max(ibw, 35) # Safeguard
        adjbw = ibw + 0.4 * (weight - ibw)

        # Weight selection for CrCl
        if bmi < 18.5:
            renal_weight = weight
            weight_note = "⚠️ Underweight → Actual BW used"
        elif bmi >= 30:
            renal_weight = adjbw
            weight_note = "⚠️ Obese → Adjusted BW used"
        else:
            renal_weight = ibw
            weight_note = "✅ Normal/Overweight → IBW used"

        crcl = ((140 - age) * renal_weight) / (72 * scr)
        if gender == "Female": crcl *= 0.85
        
        # Drug Specific PK
        if selected_drug == "Phenytoin":
            vd = 0.7 * (adjbw if bmi >= 30 else weight)
            vmax_t = 7.0 * (adjbw if bmi >= 30 else weight)
            km = 4.0
            s_factor = 0.92
            ld = target * vd
            md = ((vmax_t * target) / (km + target)) / (24/interval)
            k_el = (vmax_t / (km + target)) / vd
            t_half = 0.693 / k_el
        elif selected_drug == "Valproic acid":
            vd, cl = 0.15 * weight, 0.008 * weight
            ld, md = target*vd, target*cl*interval
            t_half = 0.693/(cl/vd)
        else:
            vd, cl = 0.6 * weight, (crcl * 0.6) / 1000 * 60
            ld, md = target*vd, target*cl*interval
            t_half = 0.693/(cl/vd)

        st.markdown('</div>', unsafe_allow_html=True)

        # --- Case 2: Phenytoin + VPA Interaction ---
        if selected_drug == "Phenytoin":
            st.markdown('<div class="section">', unsafe_allow_html=True)
            st.subheader("🧪 Free Concentration (VPA Interaction)")
            cp1, cp2, cp3 = st.columns(3)
            with cp1: total_pht = st.number_input("Total PHT (mg/L)", 0.0, 50.0, 10.0)
            with cp2: vpa_level = st.number_input("VPA Level (mg/L)", 0.0, 200.0, 100.0)
            with cp3: alb = st.number_input("Albumin (g/dL)", 0.5, 6.0, 4.2)
            
            free_fraction = 0.1 + (0.001 * vpa_level)
            estimated_free = total_pht * free_fraction
            st.metric("Estimated Free Phenytoin", f"{estimated_free:.2f} mg/L")
            st.markdown('</div>', unsafe_allow_html=True)

    with col_res:
        st.markdown('<div class="section">', unsafe_allow_html=True)
        st.markdown("### 📊 Body & Renal Assessment")
        m1, m2, m3 = st.columns(3)
        m1.metric("BMI", f"{bmi:.1f}")
        m2.metric("IBW", f"{ibw:.1f} kg")
        m3.metric("CrCl", f"{crcl:.1f}")
        
        st.info(f"**Weight Policy:** {weight_note}")
        
        if crcl >= 60: st.success("🟢 Normal/Mild Impairment")
        elif crcl >= 30: st.warning("🟠 Moderate Impairment")
        else: st.error("🔴 Severe Impairment/Failure")
        
        st.divider()
        st.markdown("### 💊 Final Regimen")
        st.success(f"**Loading Dose:** {round(ld)} mg")
        st.success(f"**Maintenance:** {round(md)} mg q{interval}h")
        
        # Therapeutic range safety check
        t_range = drug_db[selected_drug]["Range"]
        upper_limit = float(t_range.split('-')[1].split()[0])
        if target > upper_limit:
            st.error(f"⚠️ Target ({target}) is ABOVE therapeutic range ({t_range})!")
        else:
            st.info(f"✅ Target within range ({t_range})")
            
        st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    st.markdown('<div class="section">', unsafe_allow_html=True)
    db = drug_db[selected_drug]
    st.subheader(f"📚 {selected_drug} Monograph")
    k1, k2 = st.columns(2)
    with k1: 
        st.write(f"**Target Range:** {db['Range']}")
        st.write(f"**Max Dose:** {db['Max']}")
    with k2: st.error(f"**Side Effects:** {db['SE']}")
    st.markdown('</div>', unsafe_allow_html=True)

with tab3:
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.table({
        "Parameter": ["BMI Status", "IBW", "Adjusted BW", "Creatinine Clearance", "Volume of Distribution (Vd)", "Half-life (t½)"],
        "Value": [f"{bmi:.1f} ({'Obese' if bmi>=30 else 'Normal'})", f"{ibw:.1f} kg", f"{adjbw:.1f} kg", f"{crcl:.1f} mL/min", f"{vd:.1f} L", f"{t_half:.1f} h"]
    })
    st.markdown('</div>', unsafe_allow_html=True)

with tab4:
    st.markdown('<div class="section">', unsafe_allow_html=True)
    soap_txt = f"S: Patient for {selected_drug} dosing.\nO: BMI {bmi:.1f}, CrCl {crcl:.1f}mL/min.\nA: Renal function is {'stable' if crcl>60 else 'impaired'}. Target Css {target}mg/L.\nP: Give LD {round(ld)}mg, then MD {round(md)}mg every {interval}h."
    st.text_area("Edit SOAP Note", soap_txt, height=200)
    
    pdf_data = create_pdf_report(age, weight, selected_drug, crcl, ld, md, interval, soap_txt, vd, t_half)
    st.download_button("📥 Download Official Report", pdf_data, f"DoseWise_{selected_drug}.pdf")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<br><center>💙 **DoseWise** | Project by Team 2</center>", unsafe_allow_html=True)
