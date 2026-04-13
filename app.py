import streamlit as st
import math
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from io import BytesIO

# ==============================
# 🎨 1. Clean Professional UI (Stable)
# ==============================
def set_page_style():
    st.markdown('''
    <style>
    .stApp { background-color: #f8fafc; }
    .hero {
        background: #0f172a;
        padding: 30px; border-radius: 15px;
        text-align: center; color: white;
        margin-bottom: 25px;
    }
    .section {
        background: white; padding: 25px; border-radius: 12px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        border: 1px solid #e2e8f0; margin-bottom: 20px;
    }
    .stButton>button {
        background: #1e3a8a; color: white;
        border-radius: 8px; font-weight: bold;
        width: 100%; border: none; padding: 12px;
    }
    </style>
    ''', unsafe_allow_html=True)

# ==============================
# 📄 2. Professional PDF Generator
# ==============================
def create_pdf_report(age, weight, drug, crcl, ld, md, interval, soap_text, peak=None, trough=None):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    
    # Custom Title Style
    title_style = styles["Heading1"]
    title_style.textColor = colors.hexColor("#1e3a8a")
    
    content = []
    content.append(Paragraph(f"DoseWise: {drug} Clinical Report", title_style))
    content.append(Spacer(1, 20))
    
    # Patient Table
    data = [
        ["Patient Age", f"{age} Y", "Drug Selected", drug],
        ["Total Weight", f"{weight} kg", "Est. CrCl", f"{crcl:.1f} mL/min"]
    ]
    t = Table(data, colWidths=[100, 150, 100, 150])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.whitesmoke),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey)
    ]))
    content.append(t)
    
    content.append(Spacer(1, 20))
    content.append(Paragraph(f"<b>Final Regimen:</b> LD {round(ld)} mg | MD {round(md)} mg every {interval}h", styles['Heading2']))
    
    if peak and trough:
        content.append(Paragraph(f"<b>Predicted Steady State:</b> Peak {peak:.2f} mg/L | Trough {trough:.2f} mg/L", styles['Normal']))
    
    content.append(Spacer(1, 20))
    content.append(Paragraph("<b>Clinical SOAP Note:</b>", styles['Heading3']))
    content.append(Paragraph(soap_text.replace('\n', '<br/>'), styles['Normal']))
    
    doc.build(content)
    return buffer.getvalue()

# ==============================
# ⚙️ 3. Main Framework & Logic
# ==============================
st.set_page_config(page_title="DoseWise Clinical Master", layout="wide")
set_page_style()

st.markdown('<div class="hero"><h1>💊 DoseWise Clinical Platform</h1><p>Integrated PK Decision Support & SOAP Documentation</p></div>', unsafe_allow_html=True)

# --- Shared Inputs Section ---
st.markdown('<div class="section">', unsafe_allow_html=True)
selected_drug = st.selectbox("💊 Select Medication", ["Phenytoin", "Valproic acid", "Carbamazepine", "Levetiracetam"])
col1, col2 = st.columns(2)
with col1:
    age = st.number_input("Age (Years)", 1, 100, 30)
    weight = st.number_input("Weight (kg)", 10.0, 250.0, 70.0)
    height = st.number_input("Height (cm)", 50, 250, 170)
with col2:
    gender = st.selectbox("Gender", ["Male", "Female"])
    scr = st.number_input("SCr (mg/dL)", 0.1, 5.0, 1.0)
    target = st.slider("Target Css (mg/L)", 5, 100, 15 if selected_drug != "Valproic acid" else 75)
interval = st.selectbox("Interval (hr)", [4, 6, 8, 12, 24], index=3)
st.markdown('</div>', unsafe_allow_html=True)

# --- Phenytoin Advanced Parameters ---
alb, vmax, km, s_factor = 4.4, 7.0, 4.0, 0.92
if selected_drug == "Phenytoin":
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.subheader("🧬 Phenytoin Specific (Non-Linear) Parameters")
    cp1, cp2 = st.columns(2)
    with cp1:
        vmax = st.number_input("Vmax (mg/kg/day)", 1.0, 15.0, 7.0)
        alb = st.number_input("Serum Albumin (g/dL)", 0.5, 6.0, 4.4)
    with cp2:
        km = st.number_input("Km (mg/L)", 1.0, 10.0, 4.0)
        salt_form = st.selectbox("Salt Form Formulation", ["Sodium (S=0.92)", "Acid (S=1.0)"])
    s_factor = 0.92 if "Sodium" in salt_form else 1.0
    st.markdown('</div>', unsafe_allow_html=True)

# --- Calculations Core ---
ht_in = height / 2.54; ibw = (50 + 2.3*(ht_in-60)) if gender=="Male" else (45.5 + 2.3*(ht_in-60))
is_obese = weight > (1.2 * ibw)
d_wt = (ibw + 0.4 * (weight - ibw)) if (is_obese and selected_drug == "Phenytoin") else weight
crcl_wt = ibw if is_obese else weight
crcl = ((140-age)*crcl_wt)/(72*scr) if gender=="Male" else ((140-age)*crcl_wt)/(72*scr)*0.85

peak, trough = None, None
if selected_drug == "Phenytoin":
    vd = 0.7 * d_wt; vmax_t = vmax * d_wt
    md = ((vmax_t * target) / (km + target)) / (24/interval); ld = target * vd
    k_el = (vmax_t / (km + target)) / vd; t_h = 0.693 / k_el
    peak = (target/s_factor)+((md*s_factor)/vd); trough = peak * math.exp(-k_el * interval)
elif selected_drug == "Valproic acid":
    vd, cl = 0.15 * weight, 0.008 * weight; k = cl/vd; ld, md = target*vd, target*cl*interval; t_h = 0.693/k
elif selected_drug == "Carbamazepine":
    vd, cl = 1.4 * weight, 0.06 * weight; k = cl/vd; ld, md = target*vd, target*cl*interval; t_h = 0.693/k
else: # Levetiracetam
    vd = 0.6 * weight; cl = (crcl * 0.6) / 1000 * 60; k = cl/vd; ld, md = target*vd, target*cl*interval; t_h = 0.693/k

if selected_drug != "Phenytoin" and crcl < 50: md *= (crcl/100)

# ==============================
# 📋 TABS INTERFACE
# ==============================
t1, t2, t3, t4, t5 = st.tabs(["🎯 Results", "📚 Drug Monograph", "⚖️ Clinical Decision", "📋 Case Summary", "📝 SOAP Note"])

with t1:
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.subheader("📊 Output Regimen")
    r1, r2, r3 = st.columns(3)
    r1.metric("CrCl (mL/min)", f"{crcl:.1f}")
    r2.metric("Vd (L)", f"{vd:.1f}")
    r3.metric("t½ (h)", f"{t_h:.1f}" if selected_drug != "Phenytoin" else "N/A")
    if selected_drug == "Phenytoin":
        st.info(f"Steady State: Peak {peak:.2f} | Trough {trough:.2f} mg/L")
    st.success(f"Recommended Plan: LD {round(ld)}mg | MD {round(md)}mg q{interval}h")
    st.markdown('</div>', unsafe_allow_html=True)

with t2:
    st.markdown('<div class="section">', unsafe_allow_html=True)
    drug_db = {
        "Phenytoin": ["10-20 mg/L", "1000 mg/day", "Gingival hyperplasia, Osteomalacia, Nystagmus."],
        "Valproic acid": ["50-100 mg/L", "60 mg/kg/day", "Hepatotoxicity, Hair loss, Weight gain."],
        "Carbamazepine": ["4-12 mg/L", "1600 mg/day", "Auto-induction, SJS, Hyponatremia."],
        "Levetiracetam": ["12-46 mg/L", "3000 mg/day", "Behavioral changes, Irritability, Fatigue."]
    }
    st.subheader(f"📚 {selected_drug} Knowledge Base")
    st.write(f"**Therapeutic Window:** {drug_db[selected_drug][0]}")
    st.write(f"**Maximum Daily Dose:** {drug_db[selected_drug][1]}")
    st.error(f"**Common Side Effects:** {drug_db[selected_drug][2]}")
    st.markdown('</div>', unsafe_allow_html=True)

with t3:
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.subheader("⚖️ Clinical Decision Support")
    if is_obese: st.error(f"❗ Obesity: Dose adjusted using ABW ({d_wt:.1f} kg).")
    if crcl < 50: st.warning(f"⚠️ Renal: Maintenance dose reduced due to CrCl {crcl:.1f}.")
    if selected_drug == "Phenytoin" and alb < 4.4:
        adj_c = target / ((0.2 * alb) + 0.1)
        st.info(f"💡 Albumin: Adjusted target Css is {adj_c:.1f} mg/L.")
    st.write("Plan: Initiate therapy and monitor for clinical response.")
    st.markdown('</div>', unsafe_allow_html=True)

with t4:
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.subheader("📋 Case Summary Table")
    st.table({"Clinical Parameter": ["Age", "Weight", "IBW", "CrCl", "Regimen"], 
              "Value": [f"{age}Y", f"{weight}kg", f"{ibw:.1f}kg", f"{crcl:.1f}mL/min", f"{round(md)}mg q{interval}h"]})
    st.markdown('</div>', unsafe_allow_html=True)

with t5:
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.subheader("📝 Professional SOAP Note")
    soap_note = f"S: {age}Y patient on {selected_drug}.\nO: Weight {weight}kg, CrCl {crcl:.1f}mL/min, SCr {scr}mg/dL.\nA: PK dose optimized for patient status.\nP: Administer LD {round(ld)}mg once. Start MD {round(md)}mg q{interval}h. Monitor levels."
    st.markdown(f'<div style="background:#f0f9ff; padding:20px; border-radius:10px; border-left:8px solid #0f172a;">{soap_note.replace("\n", "<br><br>")}</div>', unsafe_allow_html=True)
    
    # PDF Button
    pdf_file = create_pdf_report(age, weight, selected_drug, crcl, ld, md, interval, soap_note, peak, trough)
    st.download_button("📥 Download Official Clinical Report", pdf_file, f"DoseWise_{selected_drug}.pdf", "application/pdf")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<center style='color:#64748b;'>DoseWise Clinical Master v15.0 | MNU Faculty of Pharmacy | Project by Eslam Ahmed</center>", unsafe_allow_html=True)
