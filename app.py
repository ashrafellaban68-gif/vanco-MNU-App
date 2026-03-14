import streamlit as st
import os
import base64

# --- 1. وظيفة الخلفية والستايل الجمالي ---
def set_page_bg_from_local(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            bin_str = base64.b64encode(f.read()).decode()
        st.markdown(f'''
        <style>
        .stApp {{
            background-image: linear-gradient(rgba(255, 255, 255, 0.85), rgba(255, 255, 255, 0.85)), 
            url("data:image/png;base64,{bin_str}");
            background-size: cover;
            background-attachment: fixed;
        }}
        .aesthetic-box {{
            width: 100%;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 25px;
            border-collapse: separate;
            overflow: hidden;
            box-shadow: 0 15px 35px rgba(30, 58, 138, 0.15);
            border: 1px solid rgba(30, 58, 138, 0.1);
        }}
        .main-cell {{ padding: 30px; }}
        .custom-title {{ 
            color: white; 
            font-size: 20px; 
            font-weight: bold; 
            background: linear-gradient(90deg, #1e3a8a, #3b82f6);
            padding: 12px 20px;
            border-radius: 12px;
            margin-bottom: 25px;
            text-align: center;
        }}
        .stButton>button {{ 
            background: linear-gradient(45deg, #1e3a8a, #1e40af);
            color: white; 
            font-weight: bold; 
            border-radius: 15px; 
            height: 3.5em;
        }}
        </style>
        ''', unsafe_allow_html=True)
    except:
        st.markdown("<style>.stApp {background-color: #f8fafc;}</style>", unsafe_allow_html=True)

# --- 2. الإعدادات ---
st.set_page_config(page_title="MNU PK Calculator", layout="centered")
if os.path.exists("bg.jpg"):
    set_page_bg_from_local('bg.jpg')

col_l, col_m, col_r = st.columns([1, 2, 1])
with col_l:
    if os.path.exists("college_logo.png"): st.image("college_logo.png", width=85)
with col_r:
    if os.path.exists("uni_logo.png"): st.image("uni_logo.png", width=85)

st.markdown("<h1>Clinical PK Dose Calculator</h1>", unsafe_allow_html=True)
st.markdown("<h4>Faculty of Pharmacy - Mansoura National University</h4>", unsafe_allow_html=True)

# --- 3. المربع الجمالي ---
st.markdown('''
<table class="aesthetic-box">
    <tr>
        <td class="main-cell">
            <div class="custom-title">📋 Patient Clinical Profile</div>
''', unsafe_allow_html=True)

selected_drug = st.selectbox("💊 Selected Drug Category", [
    "Vancomycin (Antibiotics - Renal Adjusted)", 
    "Gentamicin (Antibiotics - Renal Adjusted)", 
    "Digoxin (Cardiovascular - Renal Adjusted)",
    "General Renal Dose Adjustment"
])
calc_type = st.radio("Type of Calculation", ["Initial Regimen", "Dose Adjustment"], horizontal=True)
diagnosis = st.text_input("Diagnosis / Clinical Condition")

st.markdown("<hr style='opacity: 0.1; margin: 20px 0;'>", unsafe_allow_html=True)

c1, c2 = st.columns(2)
with c1:
    age = st.number_input("Age (Years)", min_value=1, value=60)
    weight = st.number_input("Weight (kg)", min_value=10.0, value=80.0)
    height = st.number_input("Height (cm)", min_value=50, value=170)
    gender = st.selectbox("Gender", ["Male", "Female"])
with c2:
    scr = st.number_input("Serum Creatinine (mg/dL)", min_value=0.1, value=1.20, format="%.2f")
    if "Vancomycin" in selected_drug:
        target = st.slider("Target Trough (mg/L)", 10.0, 20.0, 15.0); intervals = [8, 12, 24, 48]
    elif "Gentamicin" in selected_drug:
        target = st.slider("Target Trough (mg/L)", 0.5, 2.0, 1.0); intervals = [8, 12, 24]
    elif "Digoxin" in selected_drug:
        target = st.slider("Target CSS (ng/mL)", 0.5, 2.0, 0.8); intervals = [24, 48]
    else:
        target = st.slider("Target Dose %", 25, 100, 100); intervals = [12, 24, 48]
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
    
    # --- جزء المنشورنج (Safety & Monitoring) ---
    with st.expander("🛡️ Safety & Monitoring Plan"):
        st.write(f"**Diagnosis:** {diagnosis if diagnosis else 'Not Specified'}")
        if "Vancomycin" in selected_drug:
            st.write("- Monitor Trough level before the 4th dose.\n- Monitor SCr daily for Nephrotoxicity.")
        elif "Gentamicin" in selected_drug:
            st.write("- Monitor Peak (efficacy) and Trough (safety).\n- Watch for Ototoxicity and Nephrotoxicity.")
        elif "Digoxin" in selected_drug:
            st.write("- Monitor levels 6-8h post-dose.\n- Watch for toxicity signs (Nausea, Yellow vision).")
        else:
            st.write("- General Renal Adjustment: Monitor renal function and clinical response.")

# قفل الجدول
st.markdown('</td></tr></table>', unsafe_allow_html=True)
st.markdown("<br><p style='text-align: center; color: #64748b; font-size: 0.8em;'>Clinical PK Project | MNU</p>", unsafe_allow_html=True)
