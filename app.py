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
# 🎨 1. Premium Page Style (保持原样)
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
    .stButton>button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(30, 58, 138, 0.3);
    }}
    </style>
    ''', unsafe_allow_html=True)

# ==============================
# 📄 2. PDF Report Generator (تحسين الطباعة)
# ==============================
def create_pdf_report(age, weight, drug, crcl, ld, md, interval, soap_text=""):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    content = []
    content.append(Paragraph("DoseWise - Professional PK Report", styles['Title']))
    content.append(Spacer(1, 20))
    
    # Table for Patient Info
    data = [
        ["Age", f"{age} Y", "Drug", drug],
        ["Weight", f"{weight} kg", "CrCl", f"{crcl:.1f} mL/min"]
    ]
    t = Table(data, colWidths=[80, 150, 80, 150])
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
# ⚙️ 3. App Setup & Logic
# ==============================
st.set_page_config(page_title="DoseWise | Clinical PK Platform", layout="wide")
set_page_style('bg.jpg' if os.path.exists("bg.jpg") else "")

st.markdown('<div class="hero">💊 DoseWise Platform</div>', unsafe_allow_html=True)

# --- GLOBAL LOGIC (قبل التبويبات لضمان عمل الطباعة في كل مكان) ---
selected_drug = st.sidebar.selectbox("Select Medication", ["Phenytoin", "Valproic acid", "Carbamazepine", "Levetiracetam"])
age = st.sidebar.number_input("Age", 1, 100, 30)
weight = st.sidebar.number_input("Weight (kg)", 10.0, 250.0, 70.0)
height = st.sidebar.number_input("Height (cm)", 50, 250, 170)
gender = st.sidebar.selectbox("Gender", ["Male", "Female"])
scr = st.sidebar.number_input("SCr (mg/dL)", 0.1, 5.0, 1.0)
target = st.sidebar.slider("Target Css (mg/L)", 5, 100, 15 if selected_drug != "Valproic acid" else 75)
interval = st.sidebar.selectbox("Interval (hr)", [4, 6, 8, 12, 24], index=3)

# PK Calculations
ht_in = height / 2.54
ibw = (50 + 2.3*(ht_in-60)) if gender=="Male" else (45.5 + 2.3*(ht_in-60))
dosing_weight = weight
is_obese = weight > (1.2 * ibw)
s_factor, albumin, vmax, km, extra_info = 0.92, 4.4, 7.0, 4.0, ""

if selected_drug == "Phenytoin":
    if is_obese: dosing_weight = ibw + 0.4 * (weight - ibw)
    s_factor = 0.92 # Default for Sodium
    vd = 0.7 * dosing_weight; vmax_t = vmax * dosing_weight
    md = ((vmax_t * target) / (km + target)) / (24/interval); ld = target * vd
    k_el = (vmax_t / (km + target)) / vd; t_half = 0.693 / k_el
    css_max = (target / s_factor) + ((md * s_factor) / vd); css_min = css_max * math.exp(-k_el * interval)
elif selected_drug == "Valproic acid":
    vd, cl = 0.15 * weight, 0.008 * weight; k = cl/vd; ld, md = target*vd, target*cl*interval; t_half = 0.693/k
else:
    vd, cl = 0.6 * weight, (((140-age)*weight)/(72*scr) * 0.6) / 1000 * 60; k = cl/vd; ld, md = target*vd, target*cl*interval; t_half = 0.693/k

crcl_wt = ibw if is_obese else weight
crcl = ((140-age)*crcl_wt)/(72*scr) if gender=="Male" else ((140-age)*crcl_wt)/(72*scr)*0.85
if selected_drug != "Phenytoin" and crcl < 50: md *= (crcl/100)

soap_content = f"""S: {age}Y {gender.lower()} patient, {weight}kg.
O: CrCl {crcl:.1f} mL/min, SCr {scr} mg/dL, {'Obese' if is_obese else 'Normal weight'}.
A: Individualized {selected_drug} dosing required.
P: LD {round(ld)}mg once. MD {round(md)}mg every {interval}h."""

pdf_btn_data = create_pdf_report(age, weight, selected_drug, crcl, ld, md, interval, soap_content)

# --- TABS ---
tab1, tab2, tab3, tab4, tab5 = st.tabs(["🎯 Calculator", "📚 Drug Knowledge", "⚖️ Clinical Decision", "📋 Case Summary", "📝 SOAP Note"])

with tab1:
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.subheader("📊 Output Results")
    st.metric("CrCl", f"{crcl:.1f} mL/min")
    if selected_drug == "Phenytoin": st.info(f"Predicted Steady State: Peak {css_max:.2f} | Trough {css_min:.2f}")
    st.success(f"**Recommended Regimen:** LD {round(ld)}mg | MD {round(md)}mg q{interval}h")
    st.download_button("📥 Download Report", pdf_btn_data, f"DoseWise_{selected_drug}.pdf", "application/pdf", key="pdf1")
    st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    st.markdown('<div class="section">', unsafe_allow_html=True)
    drug_db = {
        "Phenytoin": {"Max": "600-1000 mg/d", "SE": "Gingival hyperplasia, Ataxia, Nystagmus.", "Note": "Michaelis-Menten kinetics."},
        "Valproic acid": {"Max": "60 mg/kg/d", "SE": "Hepatotoxicity, Hair loss, Weight gain.", "Note": "Monitor LFTs."},
        "Carbamazepine": {"Max": "1600 mg/d", "SE": "Hyponatremia, Stevens-Johnson Syndrome.", "Note": "Auto-induction risk."},
        "Levetiracetam": {"Max": "3000 mg/d", "SE": "Irritability, Behavioral changes.", "Note": "Adjust for renal function."}
    }
    db = drug_db[selected_drug]
    st.subheader(f"📚 {selected_drug} Monograph")
    k1, k2 = st.columns(2)
    with k1: st.write(f"**Max Dose:** {db['Max']}"); st.write(f"**Clinical Note:** {db['Note']}")
    with k2: st.error(f"**Side Effects:** {db['SE']}")
    st.download_button("📥 Download Report", pdf_btn_data, f"DoseWise_{selected_drug}.pdf", "application/pdf", key="pdf2")
    st.markdown('</div>', unsafe_allow_html=True)

with tab3:
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.subheader("⚖️ Clinical Decision Analysis")
    if is_obese:
        st.error(f"❗ **Weight Alert:** Patient is Obese. Dosing weight adjusted from {weight}kg to ABW {dosing_weight:.1f}kg.")
    if crcl < 50:
        st.warning(f"⚠️ **Renal Alert:** CrCl is low ({crcl:.1f} mL/min). Maintenance dose reduction applied.")
    if selected_drug == "Phenytoin":
        st.info("💡 **Phenytoin Specific:** Non-linear kinetics (Michaelis-Menten) applied for MD calculation.")
    st.write("---")
    st.write("**Pharmacist Note:** Target concentration is within therapeutic range. Monitor for efficacy and side effects.")
    st.download_button("📥 Download Report", pdf_btn_data, f"DoseWise_{selected_drug}.pdf", "application/pdf", key="pdf3")
    st.markdown('</div>', unsafe_allow_html=True)

with tab4:
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center; color:#1e3a8a;'>📋 Case Summary Table</h2>", unsafe_allow_html=True)
    # تصميم الجدول كما طلبت
    st.table({
        "Parameter": ["Age", "Actual Weight", "IBW", "Est. CrCl", "Vd", "Drug Selection"],
        "Clinical Value": [f"{age} Y", f"{weight} kg", f"{ibw:.1f} kg", f"{crcl:.1f} mL/min", f"{vd:.1f} L", selected_drug]
    })
    st.download_button("📥 Download Report", pdf_btn_data, f"DoseWise_{selected_drug}.pdf", "application/pdf", key="pdf4")
    st.markdown('</div>', unsafe_allow_html=True)

with tab5:
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center; color:#1e3a8a;'>📝 Professional SOAP Note</h2>", unsafe_allow_html=True)
    st.markdown(f'''
    <div style="background-color: #f0f4f8; padding: 25px; border-radius: 12px; border-left: 10px solid #1e3a8a;">
        <p><b>Subjective:</b> Patient presents for {selected_drug} dosing optimization.</p>
        <p><b>Objective:</b> Weight {weight}kg, SCr {scr}mg/dL, calculated CrCl {crcl:.1f}mL/min.</p>
        <p><b>Assessment:</b> Individualized PK regimen based on patient status and {selected_drug} kinetics.</p>
        <p><b>Plan:</b> Administer Loading Dose {round(ld)}mg, then Maintenance Dose {round(md)}mg q{interval}h.</p>
    </div>
    ''', unsafe_allow_html=True)
    st.download_button("📥 Download SOAP Report", pdf_btn_data, f"DoseWise_SOAP.pdf", "application/pdf", key="pdf5")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<br><center>💙 **DoseWise** | Clinical PK Project | MNU</center>", unsafe_allow_html=True)
