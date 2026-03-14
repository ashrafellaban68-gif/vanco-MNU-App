import streamlit as st
import os
import base64

# --- 1. التنسيق والخلفية ---
def set_page_bg_from_local(bin_file):
    try:
        with open(bin_file, 'rb') as f: bin_str = base64.b64encode(f.read()).decode()
        st.markdown(f'''<style>.stApp {{ background-image: linear-gradient(rgba(255, 255, 255, 0.88), rgba(255, 255, 255, 0.88)), url("data:image/png;base64,{bin_str}"); background-size: cover; background-attachment: fixed; }} .main-container {{ background-color: rgba(255, 255, 255, 0.98); padding: 25px; border-radius: 20px; border-top: 10px solid #1e3a8a; box-shadow: 0 12px 30px rgba(0,0,0,0.2); margin-top: 10px; }} .custom-title {{ color: #1e3a8a; font-size: 24px; font-weight: bold; border-bottom: 2px solid #f0f2f6; padding-bottom: 10px; margin-bottom: 20px; }} h1 {{ color: #1e3a8a; text-align: center; font-weight: bold; }} h4 {{ color: #b8860b; text-align: center; margin-top: -10px; }} .stButton>button {{ background-color: #1e3a8a; color: white; font-weight: bold; border-radius: 12px; width: 100%; height: 3.5em; }}</style>''', unsafe_allow_html=True)
    except: st.markdown("<style>.stApp {background-color: #f0f2f6;}</style>", unsafe_allow_html=True)

st.set_page_config(page_title="MNU Clinical PK Tool", layout="centered")
if os.path.exists("bg.jpg"): set_page_bg_from_local('bg.jpg')

# اللوجوهات
col_l, col_m, col_r = st.columns([1, 2, 1])
with col_l: (st.image("college_logo.png", width=110) if os.path.exists("college_logo.png") else None)
with col_r: (st.image("uni_logo.png", width=110) if os.path.exists("uni_logo.png") else None)

st.markdown("<h1>Clinical PK Dose Calculator</h1>", unsafe_allow_html=True)
st.markdown("<h4>Faculty of Pharmacy - Mansoura National University</h4>", unsafe_allow_html=True)

# --- 3. المربع الرئيسي (GUI) ---
st.markdown('<div class="main-container"><div class="custom-title">📋 Patient Clinical Profile</div>', unsafe_allow_html=True)

# قائمة أدوية مقسمة حسب الورقة (Antibiotics, Cardiovascular, Renal Adjustment)
selected_drug = st.selectbox("💊 Selected Drug Category", [
    "Vancomycin (Antibiotics - Renal Adjusted)", 
    "Gentamicin (Antibiotics - Renal Adjusted)", 
    "Digoxin (Cardiovascular - Renal Adjusted)",
    "General Renal Dose Adjustment (Other Drugs)"
])

calc_type = st.radio("Type of Calculation", ["Initial Regimen", "Dose Adjustment"])
diagnosis = st.text_input("Diagnosis / Clinical Condition")

c1, c2 = st.columns(2)
with c1:
    age = st.number_input("Age (Years)", min_value=1, value=60)
    weight = st.number_input("Weight (kg)", min_value=10.0, value=80.0)
    height = st.number_input("Height (cm)", min_value=50, value=170)
    gender = st.selectbox("Gender", ["Male", "Female"])
with c2:
    scr = st.number_input("Serum Creatinine (mg/dL)", min_value=0.1, value=1.20)
    
    # تحديد الأهداف بناءً على الاختيار
    if "Vancomycin" in selected_drug: 
        target = st.slider("Target Trough (mg/L)", 10, 20, 15); intervals = [8, 12, 24, 48]
    elif "Gentamicin" in selected_drug: 
        target = st.slider("Target Trough (mg/L)", 0.5, 2.0, 1.0); intervals = [8, 12, 24]
    elif "Digoxin" in selected_drug:
        target = st.slider("Target CSS (ng/mL)", 0.5, 2.0, 0.8); intervals = [24, 48]
    else: # General Renal Adjustment
        target = st.slider("Target Percentage of Normal Dose (%)", 25, 100, 100)
        intervals = [12, 24, 48]
    
    interval = st.selectbox("Selected Dosing Interval (Hours)", intervals)

# الحسابات العلمية
# 1. IBW
if gender == "Male": ibw = 50 + 2.3 * ((height/2.54) - 60)
else: ibw = 45.5 + 2.3 * ((height/2.54) - 60)

# 2. CrCl (Cockcroft-Gault)
if gender == "Male": crcl = ((140 - age) * weight) / (72 * scr)
else: crcl = (((140 - age) * weight) / (72 * scr)) * 0.85

# 3. Drug Specific Parameters
unit, step = ("mg", 250) if "Vancomycin" in selected_drug else ("mg", 20) if "Gentamicin" in selected_drug else ("mcg", 62.5) if "Digoxin" in selected_drug else ("%", 5)

if "Vancomycin" in selected_drug: 
    k, vd, ld_val = (0.00083 * crcl + 0.0044), (0.7 * weight), (25 * weight)
elif "Gentamicin" in selected_drug: 
    k, vd, ld_val = (0.00293 * crcl + 0.014), (0.25 * weight), (2 * weight)
elif "Digoxin" in selected_drug:
    k, vd, ld_val = ((0.0138 * crcl + 0.02) / 24), (7 * weight + (3 * crcl)), (10 * weight)
else: # General Adjustment
    k, vd, ld_val = 0, 0, 0 # لتبسيط الحسبة العامة بناء على النسبة

# حساب الجرعة
if "General" not in selected_drug:
    md = (target * k * vd * interval) / (1 - (2.71828 ** (-k * interval)))
    f_ld, f_md = round(ld_val/step)*step, round(md/step)*step
    rec_text = f"Give {f_ld} {unit} Loading Dose, then {f_md} {unit} Q{interval}H."
else:
    rec_text = f"Adjust dose to {target}% of the standard dose every {interval} hours based on CrCl of {crcl:.1f} mL/min."

if st.button("Generate Final Recommendation"):
    st.markdown("---")
    st.markdown(f'<div class="custom-title">📊 Individualized Recommendation</div>', unsafe_allow_html=True)
    m1, m2, m3 = st.columns(3)
    m1.metric("CrCl (mL/min)", f"{crcl:.1f}")
    m2.metric("IBW (kg)", f"{ibw:.1f}")
    m3.metric("Status", "Renal Impaired" if crcl < 60 else "Normal")
    
    st.success(f"**Clinical Recommendation:** {rec_text}")
    
    with st.expander("🛡️ Safety & Monitoring (Renal Considerations)"):
        st.write(f"**Diagnosis:** {diagnosis if diagnosis else 'Not Specified'}")
        st.write(f"- Dose adjusted for Kidney Function (CrCl: {crcl:.1f} mL/min).")
        if "Vancomycin" in selected_drug or "Gentamicin" in selected_drug:
            st.write("- Avoid other nephrotoxic drugs (e.g. NSAIDs).")
            st.write("- Monitor SCr daily.")

st.markdown('</div>', unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray; font-size: 0.8em;'>Clinical PK Project | MNU</p>", unsafe_allow_html=True)
