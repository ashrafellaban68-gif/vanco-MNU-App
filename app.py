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
# 📄 2. PDF Report Generator
# ==============================
def create_pdf_report(age, weight, drug, crcl, ld, md, interval, soap_text="", peak=None, trough=None):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    content = []
    content.append(Paragraph("DoseWise - Clinical PK Report", styles['Title']))
    content.append(Spacer(1, 20))
    
    data = [
        ["Patient Age", f"{age} Y", "Medication", drug],
        ["Total Weight", f"{weight} kg", "Est. CrCl", f"{crcl:.1f} mL/min"]
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
# ⚙️ 3. App Setup & Logic
# ==============================
st.set_page_config(page_title="DoseWise | Clinical PK Platform", layout="wide")
set_page_style('bg.jpg' if os.path.exists("bg.jpg") else "")

st.markdown('<div class="hero">💊 DoseWise Platform</div>', unsafe_allow_html=True)

# --- 📚 Full Knowledge Database (تم إصلاح الـ Keys) ---
drug_db = {
    "Phenytoin": {
        "Max": "1000 mg/day", 
        "Range": "10-20 mg/L", 
        "SE": "Gingival hyperplasia, Ataxia, Nystagmus.", 
        "Note": "Non-linear Michaelis-Menten kinetics. Monitor levels closely.",
        "Decision": "⚠️ Non-linear kinetics detected. Check Albumin correction if low."
    },
    "Valproic acid": {
        "Max": "60 mg/kg/day", 
        "Range": "50-100 mg/L", 
        "SE": "Hepatotoxicity, Hair loss, Weight gain.", 
        "Note": "Highly protein bound. Monitor Liver function.",
        "Decision": "⚠️ Highly protein-bound. Monitor LFTs and platelet count."
    },
    "Carbamazepine": {
        "Max": "1600 mg/day", 
        "Range": "4-12 mg/L", 
        "SE": "Hyponatremia, Stevens-Johnson Syndrome.", 
        "Note": "Auto-induction risk within 2-4 weeks.",
        "Decision": "⚠️ Potent Enzyme Inducer. Risk of Auto-induction. Monitor Sodium."
    },
    "Levetiracetam": {
        "Max": "3000 mg/day", 
        "Range": "12-46 mg/L", 
        "SE": "Irritability, Behavioral changes.", 
        "Note": "Primarily renally cleared drug.",
        "Decision": "✅ Primarily renally cleared. High safety profile."
    }
}

tab1, tab2, tab3, tab4, tab5 = st.tabs(["🎯 Calculator", "📚 Drug Knowledge", "⚖️ Clinical Decision", "📋 Case Summary", "📝 SOAP Note"])

with tab1:
    st.markdown('<div class="section">', unsafe_allow_html=True)
    selected_drug = st.selectbox("Select Medication", list(drug_db.keys()))
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

        ht_in = height / 2.54; ibw = (50 + 2.3*(ht_in-60)) if gender=="Male" else (45.5 + 2.3*(ht_in-60))
        is_obese = weight > (1.2 * ibw); dosing_weight = weight
        s_factor, albumin, vmax, km = 0.92, 4.4, 7.0, 4.0

        if selected_drug == "Phenytoin":
            st.markdown("<h2 style='color:#1e3a8a;'>🧬 Phenytoin Advanced Parameters</h2>", unsafe_allow_html=True)
            if is_obese: dosing_weight = ibw + 0.4 * (weight - ibw)
            cp1, cp2 = st.columns(2)
            with cp1:
                vmax = st.number_input("Vmax (mg/kg/day)", 1.0, 15.0, 7.0)
                albumin = st.number_input("Serum Albumin (g/dL)", 0.5, 6.0, 4.4)
            with cp2:
                km = st.number_input("Km (mg/L)", 1.0, 10.0, 4.0)
                salt = st.selectbox("Dosage Form (S)", ["Sodium (0.92) - Cap/Inj", "Acid (1.0) - Susp/Tab"])
            s_factor = 0.92 if "Sodium" in salt else 1.0

        crcl_wt = ibw if is_obese else weight
        crcl = ((140-age)*crcl_wt)/(72*scr) if gender=="Male" else ((140-age)*crcl_wt)/(72*scr)*0.85

        if selected_drug == "Phenytoin":
            vd = 0.7 * dosing_weight; vmax_t = vmax * dosing_weight
            md = ((vmax_t * target) / (km + target)) / (24/interval); ld = target * vd
            k_el = (vmax_t / (km + target)) / vd; t_half = 0.693 / k_el
            css_max = (target / s_factor) + ((md * s_factor) / vd); css_min = css_max * math.exp(-k_el * interval)
        else:
            vd, cl = 0.6 * weight, (crcl * 0.6) / 1000 * 60; k = cl/vd; ld, md = target*vd, target*cl*interval; t_half = 0.693/k
        if selected_drug != "Phenytoin" and crcl < 50: md *= (crcl/100)
    
    with col_res:
        st.markdown("<h2 style='color:#1e293b;'>📊 Analysis Results</h2>", unsafe_allow_html=True)
        if st.button("🚀 Calculate Plan"):
            st.write(f"CrCl")
            st.markdown(f"<h1 style='font-size: 50px;'>{crcl:.1f} mL/min</h1>", unsafe_allow_html=True)
            if selected_drug == "Phenytoin":
                st.info(f"Steady State: Peak {css_max:.2f} | Trough {css_min:.2f}")
            st.success(f"Regimen: LD {round(ld)}mg | MD {round(md)}mg q{interval}h")
        
        soap_content = f"S: {age}Y patient. O: CrCl {crcl:.1f}mL/min. A: Optimized for {selected_drug}. P: LD {round(ld)}mg, MD {round(md)}mg q{interval}h."
        pdf_data = create_pdf_report(age, weight, selected_drug, crcl, ld, md, interval, soap_content, (css_max if selected_drug=="Phenytoin" else None), (css_min if selected_drug=="Phenytoin" else None))
        st.download_button("📥 Download Report", pdf_data, f"Report_{selected_drug}.pdf", key="dl1")
    st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    st.markdown('<div class="section">', unsafe_allow_html=True)
    db = drug_db[selected_drug]
    st.subheader(f"📚 {selected_drug} Monograph")
    k1, k2 = st.columns(2)
    with k1: 
        st.write(f"**Target Range:** {db['Range']}")
        st.write(f"**Max Dose:** {db['Max']}")
        st.write(f"**Clinical Note:** {db['Note']}")
    with k2: st.error(f"**Major Side Effects:** {db['SE']}")
    st.download_button("📥 Download Report", pdf_data, f"Report_{selected_drug}.pdf", key="dl2")
    st.markdown('</div>', unsafe_allow_html=True)

with tab3:
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.subheader("⚖️ Clinical Decision Support")
    st.info(f"**Expert Clinical Opinion:** {drug_db[selected_drug]['Decision']}")
    if is_obese: st.error(f"❗ **Obesity:** ABW adjustment logic applied ({dosing_weight:.1f}kg).")
    if crcl < 50: st.warning(f"⚠️ **Renal Status:** Caution. CrCl is {crcl:.1f} mL/min; Maintenance dose reduced.")
    if selected_drug == "Phenytoin" and albumin < 4.4:
        adj_c = target / ((0.2 * albumin) + 0.1)
        st.info(f"💡 **Albumin correction:** Corrected Target Css is {adj_c:.1f} mg/L.")
    st.download_button("📥 Download Report", pdf_data, f"Report_{selected_drug}.pdf", key="dl3")
    st.markdown('</div>', unsafe_allow_html=True)

with tab4:
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center; color:#1e3a8a;'>📋 Case Summary Table</h2>", unsafe_allow_html=True)
    st.table({"Parameter": ["Age", "Actual Weight", "IBW", "Est. CrCl", "Vd", "Drug Choice"], 
              "Value": [f"{age} Y", f"{weight} kg", f"{ibw:.1f} kg", f"{crcl:.1f} mL/min", f"{vd:.1f} L", selected_drug]})
    st.download_button("📥 Download Report", pdf_data, f"Report_{selected_drug}.pdf", key="dl4")
    st.markdown('</div>', unsafe_allow_html=True)

with tab5:
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center; color:#1e3a8a;'>📝 Professional SOAP Note</h2>", unsafe_allow_html=True)
    st.markdown(f'''
    <div style="background-color: #f0f4f8; padding: 25px; border-radius: 12px; border-left: 10px solid #1e3a8a;">
        <p><b>Subjective:</b> Patient presents for {selected_drug} management.</p>
        <p><b>Objective:</b> Weight {weight}kg | CrCl {crcl:.1f}mL/min | SCr {scr}mg/dL.</p>
        <p><b>Assessment:</b> Regimen optimized for body status and {selected_drug} kinetics.</p>
        <p><b>Plan:</b> Start LD <b>{round(ld)}mg</b> then MD <b>{round(md)}mg q{interval}h</b>. Monitor for {drug_db[selected_drug]['SE']}.</p>
    </div>
    ''', unsafe_allow_html=True)
    st.download_button("📥 Download SOAP Report", pdf_data, f"SOAP_{selected_drug}.pdf", key="dl5")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<center>💙 Clinical PK Project | MNU Faculty of Pharmacy</center>", unsafe_allow_html=True)
