import streamlit as st
import os
import base64

# --- 1. وظيفة الخلفية والستايل ---
def set_page_style(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            bin_str = base64.b64encode(f.read()).decode()
        bg_code = f'url("data:image/png;base64,{bin_str}")'
    except:
        bg_code = "none"

    st.markdown(f'''
    <style>
    .stApp {{
        background-image: linear-gradient(rgba(255, 255, 255, 0.85), rgba(255, 255, 255, 0.85)), {bg_code};
        background-size: cover;
        background-attachment: fixed;
    }}
    
    /* المربع الأبيض: رجعناه "صندوق" بس بمسافات خارجية ذكية */
    .block-container {{
        background-color: rgba(255, 255, 255, 0.98);
        padding: 25px 30px !important;
        border-radius: 25px;
        border-top: 10px solid #1e3a8a;
        box-shadow: 0 15px 35px rgba(0,0,0,0.2);
        
        /* تقليل الهامش العلوي والسفلي عشان ما يبقاش ضايع في الشاشة */
        margin-top: 20px !important;
        margin-bottom: 20px !important;
        
        /* العرض المتوازن: لا هو مالي الشاشة ولا هو ضيق */
        max-width: 650px !important; 
    }}
    
    .custom-title {{ 
        color: white; 
        font-size: 20px; 
        font-weight: bold; 
        background: linear-gradient(90deg, #1e3a8a, #3b82f6);
        padding: 12px;
        border-radius: 12px;
        margin-bottom: 20px;
        text-align: center;
    }}
    
    h1 {{ color: #1e3a8a; text-align: center; font-weight: 800; font-size: 24px; margin-bottom: 5px; }}
    h4 {{ color: #b8860b; text-align: center; font-size: 14px; margin-bottom: 15px; }}
    
    .stButton>button {{ 
        background: linear-gradient(45deg, #1e3a8a, #1e40af);
        color: white; 
        font-weight: bold; 
        border-radius: 12px; 
        border: none;
        height: 3.5em;
    }}
    </style>
    ''', unsafe_allow_html=True)

# --- 2. الإعدادات واللوجوهات ---
st.set_page_config(page_title="MNU PK Tool", layout="centered")
set_page_style('bg.jpg' if os.path.exists("bg.jpg") else "")

col_l, col_m, col_r = st.columns([1, 2, 1])
with col_l:
    if os.path.exists("college_logo.png"): st.image("college_logo.png", width=80)
with col_r:
    if os.path.exists("uni_logo.png"): st.image("uni_logo.png", width=80)

st.markdown("<h1>Clinical PK Dose Calculator</h1>", unsafe_allow_html=True)
st.markdown("<h4>Faculty of Pharmacy - MNU</h4>", unsafe_allow_html=True)

# --- 3. المحتوى ---
st.markdown('<div class="custom-title">📋 Patient Clinical Profile</div>', unsafe_allow_html=True)

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
    scr = st.number_input("Serum Creatinine (mg/dL)", min_value=0.1, value=1.20, format="%.2f")
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

unit, step = ("mg", 250) if "Vancomycin" in selected_drug else ("mg", 20) if "Gentamicin" in selected_drug else ("mcg", 62.5) if "Digoxin" in selected_drug else ("%", 5)
if "Vancomycin" in selected_drug: k, vd, ld_val = (0.00083 * crcl + 0.0044), (0.7 * weight), (25 * weight)
elif "Gentamicin" in selected_drug: k, vd, ld_val = (0.00293 * crcl + 0.014), (0.25 * weight), (2 * weight)
elif "Digoxin" in selected_drug: k, vd, ld_val = ((0.0138 * crcl + 0.02) / 24), (7 * weight + (3 * crcl)), (10 * weight)
else: k, vd, ld_val = 0, 0, 0

if st.button("Generate Final Recommendation"):
    st.markdown("<br><div class='custom-title' style='background: #10b981;'>📊 Results</div>", unsafe_allow_html=True)
    m1, m2, m3 = st.columns(3)
    m1.metric("CrCl", f"{crcl:.1f}")
    m2.metric("IBW", f"{ibw:.1f}")
    m3.metric("t½", f"{0.693/k:.1f}h" if k > 0 else "N/A")
    
    if k > 0:
        md = (target * k * vd * interval) / (1 - (2.71828 ** (-k * interval)))
        st.success(f"**Recommendation:** {round(ld_val/step)*step} {unit} LD, then {round(md/step)*step} {unit} every {interval}h.")
    else:
        st.info(f"**Adjustment:** Maintain {target}% of normal dose.")

st.markdown("<br><p style='text-align: center; color: #64748b; font-size: 0.75em;'>Clinical PK Project | MNU</p>", unsafe_allow_html=True)
