import streamlit as st
import os
import base64

# --- 1. وظيفة الخلفية ---
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def set_page_bg_from_local(bin_file):
    try:
        bin_str = get_base64_of_bin_file(bin_file)
        page_bg_img = f'''
        <style>
        .stApp {{
            background-image: linear-gradient(rgba(255, 255, 255, 0.88), rgba(255, 255, 255, 0.88)), 
            url("data:image/png;base64,{bin_str}");
            background-size: cover;
            background-attachment: fixed;
        }}
        .main-container {{
            background-color: rgba(255, 255, 255, 0.98);
            padding: 25px;
            border-radius: 20px;
            border-top: 10px solid #1e3a8a;
            box-shadow: 0 12px 30px rgba(0,0,0,0.2);
            margin-top: 10px;
        }}
        .custom-title {{ color: #1e3a8a; font-size: 22px; font-weight: bold; border-bottom: 2px solid #f0f2f6; padding-bottom: 10px; margin-bottom: 20px; }}
        h1 {{ color: #1e3a8a; text-align: center; font-weight: bold; font-size: 26px; }}
        h4 {{ color: #b8860b; text-align: center; margin-top: -10px; font-size: 16px; }}
        .stButton>button {{ background-color: #1e3a8a; color: white; font-weight: bold; border-radius: 12px; width: 100%; height: 3.5em; }}
        </style>
        '''
        st.markdown(page_bg_img, unsafe_allow_html=True)
    except Exception:
        st.markdown("<style>.stApp {background-color: #f0f2f6;}</style>", unsafe_allow_html=True)

# --- 2. إعداد الصفحة واللوجوهات ---
st.set_page_config(page_title="MNU Clinical PK Tool", layout="centered")
if os.path.exists("bg.jpg"):
    set_page_bg_from_local('bg.jpg')

# تقسيم اللوجوهات بشكل صحيح
col_l, col_m, col_r = st.columns([1, 2, 1])
with col_l:
    if os.path.exists("college_logo.png"):
        st.image("college_logo.png", width=100)
with col_r:
    if os.path.exists("uni_logo.png"):
        st.image("uni_logo.png", width=100)

st.markdown("<h1>Clinical PK Dose Calculator</h1>", unsafe_allow_html=True)
st.markdown("<h4>Faculty of Pharmacy - Mansoura National University</h4>", unsafe_allow_html=True)

# --- 3. المربع الرئيسي (GUI) ---
st.markdown('<div class="main-container">', unsafe_allow_html=True)
st.markdown('<div class="custom-title">📋 Patient Clinical Profile</div>', unsafe_allow_html=True)

# مدخلات المشروع بالكامل
selected_drug = st.selectbox("💊 Selected Drug Category", [
    "Vancomycin (Antibiotics - Renal Adjusted)", 
    "Gentamicin (Antibiotics - Renal Adjusted)", 
    "Digoxin (Cardiovascular - Renal Adjusted)",
    "General Renal Dose Adjustment"
])
calc_type = st.radio("Type of Calculation", ["Initial Regimen", "Dose Adjustment"], horizontal=True)
diagnosis = st.text_input("Diagnosis / Clinical Condition (e.g., Sepsis, Heart Failure)")

st.markdown("---")

c1, c2 = st.columns(2)
with c1:
    age = st.number_input("Age (Years)", min_value=1, value=60)
    weight = st.number_input("Weight (kg)", min_value=10.0, value=80.0)
    height = st.number_input("Height (cm)", min_value=50, value=170)
    gender = st.selectbox("Gender", ["Male", "Female"])
with c2:
    scr = st.number_input("Serum Creatinine (mg/dL)", min_value=0.1, value=1.20, format="%.2f")
    
    if "Vancomycin" in selected_drug:
        target = st.slider("Target Trough (mg/L)", 10, 20, 15)
        intervals = [8, 12, 24, 48]
    elif "Gentamicin" in selected_drug:
        target = st.slider("Target Trough (mg/L)", 0.5, 2.0, 1.0)
        intervals = [8, 12, 24]
    elif "Digoxin" in selected_drug:
        target = st.slider("Target CSS (ng/mL)", 0.5, 2.0, 0.8)
        intervals = [24, 48]
    else:
        target = st.slider("Target Dose %", 25, 100, 100)
        intervals = [12, 24, 48]
        
    interval = st.selectbox("Dosing Interval (Hours)", intervals)

# --- الحسابات العلمية ---
# 1. CrCl (Cockcroft-Gault)
if gender == "Male":
    crcl = ((140 - age) * weight) / (72 * scr)
else:
    crcl = (((140 - age) * weight) / (72 * scr)) * 0.85

# 2. IBW (Ideal Body Weight)
if gender == "Male":
    ibw = 50 + 2.3 * ((height/2.54) - 60)
else:
    ibw = 45.5 + 2.3 * ((height/2.54) - 60)

# 3. Drug Parameters
unit, step = ("mg", 250) if "Vancomycin" in selected_drug else ("mg", 20) if "Gentamicin" in selected_drug else ("mcg", 62.5) if "Digoxin" in selected_drug else ("%", 5)

if "Vancomycin" in selected_drug:
    k, vd, ld_val = (0.00083 * crcl + 0.0044), (0.7 * weight), (25 * weight)
elif "Gentamicin" in selected_drug:
    k, vd, ld_val = (0.00293 * crcl + 0.014), (0.25 * weight), (2 * weight)
elif "Digoxin" in selected_drug:
    k, vd, ld_val = ((0.0138 * crcl + 0.02) / 24), (7 * weight + (3 * crcl)), (10 * weight)
else:
    k, vd, ld_val = 0, 0, 0

# حساب الجرعة و CSS المتوقع
if "General" not in selected_drug:
    md = (target * k * vd * interval) / (1 - (2.71828 ** (-k * interval)))
    css_est = (md / (k * vd * interval))
    f_ld, f_md = round(ld_val/step)*step, round(md/step)*step
    rec_text = f"Give {f_ld} {unit} Loading Dose, then {f_md} {unit} every {interval}h."
else:
    css_est = 0
    rec_text = f"Adjust dose to {target}% of standard regimen every {interval}h."

# --- المخرجات النهائية ---
if st.button("Generate Final Recommendation"):
    st.markdown("---")
    st.markdown(f'<div class="custom-title">📊 Individualized Recommendation</div>', unsafe_allow_html=True)
    m1, m2, m3 = st.columns(3)
    m1.metric("CrCl (mL/min)", f"{crcl:.1f}")
    m2.metric("IBW (kg)", f"{ibw:.1f}")
    m3.metric("t½ (hr)", f"{0.693/k:.1f}" if k > 0 else "N/A")
    
    st.success(f"**Clinical Recommendation:** {rec_text}")
    if css_est > 0:
        st.info(f"**Estimated Steady State Concentration:** {css_est:.2f}")

    with st.expander("🛡️ Monitoring Plan & Safety"):
        st.write(f"**Diagnosis:** {diagnosis if diagnosis else 'General Management'}")
        st.write(f"**Regimen Type:** {calc_type}")
        st.write(f"- CrCl calculated as {crcl:.1f} mL/min. Patient status: {'Renal Impairment' if crcl < 60 else 'Normal Renal Function'}.")
        if "Vancomycin" in selected_drug:
            st.write("- Monitor Trough before 4th dose. Monitor SCr daily.")
        elif "Gentamicin" in selected_drug:
            st.write("- Target Peak: 5-10 mg/L. Watch for Ototoxicity.")
        elif "Digoxin" in selected_drug:
            st.write("- Monitor levels 6-8h post-dose. Watch for Hypokalemia.")

st.markdown('</div>', unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray; font-size: 0.8em; margin-top: 20px;'>Clinical PK Project | MNU</p>", unsafe_allow_html=True)
