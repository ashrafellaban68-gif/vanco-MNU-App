import streamlit as st
import os
import base64

# --- 1. وظيفة الخلفية ---
def set_page_bg_from_local(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            bin_str = base64.b64encode(f.read()).decode()
        st.markdown(f'''
        <style>
        .stApp {{
            background-image: linear-gradient(rgba(255, 255, 255, 0.88), rgba(255, 255, 255, 0.88)), 
            url("data:image/png;base64,{bin_str}");
            background-size: cover;
            background-attachment: fixed;
        }}
        h1 {{ color: #1e3a8a; text-align: center; font-weight: bold; font-size: 26px; }}
        h4 {{ color: #b8860b; text-align: center; margin-top: -10px; font-size: 16px; margin-bottom: 20px; }}
        /* تلوين حواف المربع الداخلي */
        [data-testid="stVerticalBlockBorderWrapper"] {{
            background-color: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 10px;
        }}
        </style>
        ''', unsafe_allow_html=True)
    except:
        st.markdown("<style>.stApp {background-color: #f0f2f6;}</style>", unsafe_allow_html=True)

# --- 2. الإعدادات ---
st.set_page_config(page_title="MNU Clinical PK Tool", layout="centered")
if os.path.exists("bg.jpg"):
    set_page_bg_from_local('bg.jpg')

col_l, col_m, col_r = st.columns([1, 2, 1])
with col_l:
    if os.path.exists("college_logo.png"): st.image("college_logo.png", width=90)
with col_r:
    if os.path.exists("uni_logo.png"): st.image("uni_logo.png", width=90)

st.markdown("<h1>Clinical PK Dose Calculator</h1>", unsafe_allow_html=True)
st.markdown("<h4>Faculty of Pharmacy - Mansoura National University</h4>", unsafe_allow_html=True)

# --- 3. المربع الرئيسي باستخدام خاصية border الأصلية ---
# دي بتعمل مربع أبيض إجباري وبيدخله كل الكلام
with st.container(border=True):
    st.subheader("📋 Patient Clinical Profile")
    
    selected_drug = st.selectbox("💊 Selected Drug Category", [
        "Vancomycin (Antibiotics - Renal Adjusted)", 
        "Gentamicin (Antibiotics - Renal Adjusted)", 
        "Digoxin (Cardiovascular - Renal Adjusted)",
        "General Renal Dose Adjustment"
    ])
    
    calc_type = st.radio("Type of Calculation", ["Initial Regimen", "Dose Adjustment"], horizontal=True)
    diagnosis = st.text_input("Diagnosis / Clinical Condition")
    
    st.divider()
    
    c1, c2 = st.columns(2)
    with c1:
        age = st.number_input("Age (Years)", min_value=1, value=60)
        weight = st.number_input("Weight (kg)", min_value=10.0, value=80.0)
        height = st.number_input("Height (cm)", min_value=50, value=170)
        gender = st.selectbox("Gender", ["Male", "Female"])
    with c2:
        scr = st.number_input("Serum Creatinine (mg/dL)", min_value=0.1, value=1.20)
        
        if "Vancomycin" in selected_drug:
            target = st.slider("Target Trough (mg/L)", 10.0, 20.0, 15.0)
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

    # الحسابات
    if gender == "Male": crcl = ((140 - age) * weight) / (72 * scr)
    else: crcl = (((140 - age) * weight) / (72 * scr)) * 0.85
    
    if gender == "Male": ibw = 50 + 2.3 * ((height/2.54) - 60)
    else: ibw = 45.5 + 2.3 * ((height/2.54) - 60)

    # معادلات الأدوية
    unit, step = ("mg", 250) if "Vancomycin" in selected_drug else ("mg", 20) if "Gentamicin" in selected_drug else ("mcg", 62.5) if "Digoxin" in selected_drug else ("%", 5)
    if "Vancomycin" in selected_drug: k, vd, ld_val = (0.00083 * crcl + 0.0044), (0.7 * weight), (25 * weight)
    elif "Gentamicin" in selected_drug: k, vd, ld_val = (0.00293 * crcl + 0.014), (0.25 * weight), (2 * weight)
    elif "Digoxin" in selected_drug: k, vd, ld_val = ((0.0138 * crcl + 0.02) / 24), (7 * weight + (3 * crcl)), (10 * weight)
    else: k, vd, ld_val = 0, 0, 0

    if st.button("Generate Final Recommendation", use_container_width=True):
        st.divider()
        st.markdown("### 📊 Results")
        m1, m2, m3 = st.columns(3)
        m1.metric("CrCl", f"{crcl:.1f}")
        m2.metric("IBW", f"{ibw:.1f}")
        m3.metric("t½", f"{0.693/k:.1f}h" if k > 0 else "N/A")
        
        if k > 0:
            md = (target * k * vd * interval) / (1 - (2.71828 ** (-k * interval)))
            st.success(f"**Recommendation:** {round(ld_val/step)*step} {unit} LD, then {round(md/step)*step} {unit} Q{interval}H.")
        else:
            st.info(f"**Adjustment:** Maintain {target}% of normal dose.")

st.markdown("<br><p style='text-align: center; color: gray; font-size: 0.8em;'>Clinical PK Project | MNU</p>", unsafe_allow_html=True)
