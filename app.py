import streamlit as st
import os
import base64
import math
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from io import BytesIO

# ==============================
# 🎨 1. Premium Medical UI
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
        background-image: linear-gradient(rgba(255, 255, 255, 0.9), rgba(255, 255, 255, 0.9)), {bg_img};
        background-size: cover;
        background-attachment: fixed;
    }}
    .hero {{
        background: linear-gradient(135deg, #0f172a, #1e3a8a);
        padding: 35px;
        border-radius: 20px;
        text-align: center;
        color: white;
        font-size: 38px;
        font-weight: 900;
        box-shadow: 0 10px 25px rgba(0,0,0,0.2);
        margin-bottom: 20px;
    }}
    .section {{
        background: white;
        padding: 25px;
        border-radius: 15px;
        margin-top: 15px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.05);
        border: 1px solid #e2e8f0;
    }}
    </style>
    ''', unsafe_allow_html=True)

# ==============================
# 📄 2. Fixed PDF Report Generator
# ==============================
def create_pdf_report(age, weight, drug, crcl, ld, md, interval, soap_text=""):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    content = []
    content.append(Paragraph(f"DoseWise: {drug} Clinical Report", styles['Title']))
    content.append(Spacer(1, 20))
    
    data = [["Age", f"{age} Y", "Drug", drug], ["Weight", f"{weight} kg", "CrCl", f"{crcl:.1f} mL/min"]]
    t = Table(data, colWidths=[100, 150, 100, 150])
    t.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), colors.whitesmoke), ('GRID', (0,0), (-1,-1), 0.5, colors.grey)]))
    content.append(t)
    
    content.append(Spacer(1, 20))
    content.append(Paragraph(f"<b>Regimen:</b> LD {round(ld)} mg | MD {round(md)} mg q{interval}h", styles['Heading2']))
    content.append(Spacer(1, 20))
    content.append(Paragraph("<b>Clinical SOAP Note:</b>", styles['Heading3']))
    content.append(Paragraph(soap_text.replace('\n', '<br/>'), styles['Normal']))
    doc.build(content)
    return buffer.getvalue()

# ==============================
# ⚙️ 3. Execution & Logic
# ==============================
st.set_page_config(page_title="DoseWise Clinical Master", layout="wide")
set_page_style('bg.jpg' if os.path.exists("bg.jpg") else "")

st.markdown('<div class="hero">💊 DoseWise Clinical Master</div>', unsafe_allow_html=True)

# --- القاعدة المعرفية للأدوية (Drug Database) ---
drug_db = {
    "Phenytoin": {
        "Range": "10-20 mg/L",
        "Max": "1000 mg/day",
        "SE": "Gingival hyperplasia, Ataxia, Nystagmus, Osteomalacia.",
        "Decision": "⚠️ Non-linear (Michaelis-Menten) kinetics. Monitor for toxicity if Css > 20 mg/L. Check Albumin levels."
    },
    "Valproic acid": {
        "Range": "50-100 mg/L",
        "Max": "60 mg/kg/day",
        "SE": "Hepatotoxicity, Thrombocytopenia, Weight gain, Tremors.",
        "Decision": "⚠️ Highly protein-bound. Monitor Liver Function Tests (LFTs). Dose reduction in hepatic impairment."
    },
    "Carbamazepine": {
        "Range": "4-12 mg/L",
        "Max": "1600 mg/day",
        "SE": "Auto-induction, SIADH (Hyponatremia), SJS (Stevens-Johnson).",
        "Decision": "⚠️ Potent enzyme inducer. Auto-induction occurs in the first 2-4 weeks. Monitor Sodium levels."
    },
    "Levetiracetam": {
        "Range": "12-46 mg/L",
        "Max": "3000 mg/day",
        "SE": "Behavioral changes (Irritability, Aggression), Somnolence.",
        "Decision": "✅ Low drug-drug interactions. Primarily renally cleared. Mandatory dose adjustment for CrCl < 80 mL/min."
    }
}

# --- نقل التبويبات بعد العنوان مباشرة ---
tab1, tab2, tab3, tab4, tab5 = st.tabs(["🎯 Calculator", "📚 Drug Knowledge", "⚖️ Clinical Decision", "📋 Case Summary", "📝 SOAP Note"])

with tab1:
    st.markdown('<div class="section">', unsafe_allow_html=True)
    selected_drug = st.selectbox("💊 Select Medication", list(drug_db.keys()))
    col_in1, col_in2 = st.columns(2)
    with col_in1:
        age = st.number_input("Age (Years)", 1, 100, 30)
        weight = st.number_input("Total Weight (kg)", 10.0, 250.0, 70.0)
        height = st.number_input("Height (cm)", 50, 250, 170)
    with col_in2:
        gender = st.selectbox("Gender", ["Male", "Female"])
        scr = st.number_input("SCr (mg/dL)", 0.1, 5.0, 1.0)
        target = st.slider("Target Css (mg/L)", 5, 100, 15 if selected_drug != "Valproic acid" else 75)
    interval = st.selectbox("Dosing Interval (hr)", [4, 6, 8, 12, 24], index=3)

    # Phenytoin Advanced Params
    alb, vmax, km, s_factor = 4.4, 7.0, 4.0, 0.92
    if selected_drug == "Phenytoin":
        st.markdown("---")
        cp1, cp2 = st.columns(2)
        with cp1:
            vmax = st.number_input("Vmax (mg/kg/d)", 1.0, 15.0, 7.0); alb = st.number_input("Albumin (g/dL)", 0.5, 6.0, 4.4)
        with cp2:
            km = st.number_input("Km (mg/L)", 1.0, 10.0, 4.0); salt = st.selectbox("Salt", ["Sodium (0.92)", "Acid (1.0)"])
        s_factor = 0.92 if "Sodium" in salt else 1.0
    st.markdown('</div>', unsafe_allow_html=True)

    # Global Calculations
    ht_in = height / 2.54; ibw = (50 + 2.3*(ht_in-60)) if gender=="Male" else (45.5 + 2.3*(ht_in-60))
    is_obese = weight > (1.2 * ibw)
    d_wt = (ibw + 0.4 * (weight - ibw)) if (is_obese and selected_drug == "Phenytoin") else weight
    crcl_wt = ibw if is_obese else weight
    crcl = ((140-age)*crcl_wt)/(72*scr) if gender=="Male" else ((140-age)*crcl_wt)/(72*scr)*0.85

    if selected_drug == "Phenytoin":
        vd = 0.7 * d_wt; vmax_t = vmax * d_wt
        md = ((vmax_t * target) / (km + target)) / (24/interval); ld = target * vd
        k_el = (vmax_t / (km + target)) / vd; t_h = 0.693 / k_el
        peak = (target/s_factor)+((md*s_factor)/vd); trough = peak * math.exp(-k_el * interval)
    else:
        vd = 0.6 * weight; cl = (crcl * 0.6) / 1000 * 60; k = cl/vd; ld, md = target*vd, target*cl*interval; t_h = 0.693/k
    if selected_drug != "Phenytoin" and crcl < 50: md *= (crcl/100)

    # Summary in Tab 1
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.subheader("📊 Primary PK Results")
    res1, res2, res3 = st.columns(3)
    res1.metric("CrCl (mL/min)", f"{crcl:.1f}")
    res2.metric("Vd (L)", f"{vd:.1f}")
    res3.metric("t½ (h)", f"{t_h:.1f}" if selected_drug != "Phenytoin" else "N/A")
    st.success(f"Regimen: LD {round(ld)}mg | MD {round(md)}mg q{interval}h")
    st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    st.markdown('<div class="section">', unsafe_allow_html=True)
    info = drug_db[selected_drug]
    st.subheader(f"📚 {selected_drug} Detailed Monograph")
    st.write(f"**Target Window:** {info['Range']}")
    st.write(f"**Max Daily Dose:** {info['Max']}")
    st.error(f"**Side Effects:** {info['SE']}")
    st.markdown('</div>', unsafe_allow_html=True)

with tab3:
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.subheader("⚖️ Professional Clinical Decision")
    st.info(f"**Expert Clinical Note:** {drug_db[selected_drug]['Decision']}")
    if is_obese: st.error(f"❗ **Weight Alert:** Obese patient. Dosing adjusted using ABW ({d_wt:.1f} kg).")
    if crcl < 50: st.warning(f"⚠️ **Renal Alert:** Impaired kidney function. Dose reduction applied for safety.")
    if selected_drug == "Phenytoin" and alb < 4.4:
        adj_c = target / ((0.2 * alb) + 0.1)
        st.info(f"💡 **Albumin Correction:** Low albumin ({alb} g/dL). Adjusted Target Css: {adj_c:.1f} mg/L.")
    st.markdown('</div>', unsafe_allow_html=True)

with tab4:
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.subheader("📋 Case Summary Presentation")
    st.table({"Clinical Parameter": ["Age", "Weight", "IBW", "CrCl", "Regimen"], "Value": [f"{age}Y", f"{weight}kg", f"{ibw:.1f}kg", f"{crcl:.1f}", f"{round(md)}mg q{interval}h"]})
    st.markdown('</div>', unsafe_allow_html=True)

with tab5:
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.subheader("📝 Professional SOAP Note")
    soap_note = f"S: {age}Y patient on {selected_drug}.\nO: Weight {weight}kg, CrCl {crcl:.1f}mL/min, SCr {scr}mg/dL.\nA: Dose optimized for patient's {'obese' if is_obese else 'normal weight'} and renal status.\nP: Administer LD {round(ld)}mg. Start MD {round(md)}mg q{interval}h. Monitor serum levels."
    st.markdown(f'<div style="background:#f0f9ff; padding:20px; border-radius:10px; border-left:8px solid #0f172a;">{soap_note.replace("\n", "<br><br>")}</div>', unsafe_allow_html=True)
    pdf_file = create_pdf_report(age, weight, selected_drug, crcl, ld, md, interval, soap_note)
    st.download_button("📥 Download Official Report", pdf_file, f"DoseWise_{selected_drug}.pdf", "application/pdf")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<center style='color:#64748b;'>DoseWise Clinical v16.0 | MNU Faculty of Pharmacy</center>", unsafe_allow_html=True)
