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
            background-image: linear-gradient(rgba(255, 255, 255, 0.85), rgba(255, 255, 255, 0.85)), url("data:image/png;base64,{bin_str}");
            background-size: cover;
            background-attachment: fixed;
        }}
        .main-container {{
            background-color: rgba(255, 255, 255, 0.98);
            padding: 25px;
            border-radius: 20px;
            border-top: 10px solid #1e3a8a;
            box-shadow: 0 12px 30px rgba(0,0,0,0.25);
            margin-top: 10px;
        }}
        .custom-title {{ color: #1e3a8a; font-size: 24px; font-weight: bold; border-bottom: 2px solid #f0f2f6; padding-bottom: 10px; margin-bottom: 20px; }}
        h1 {{ color: #1e3a8a; text-align: center; font-weight: bold; }}
        h4 {{ color: #b8860b; text-align: center; margin-top: -10px; }}
        .stButton>button {{ background-color: #1e3a8a; color: white; font-weight: bold; border-radius: 12px; width: 100%; height: 3.5em; }}
        </style>
        '''
        st.markdown(page_bg_img, unsafe_allow_html=True)
    except Exception:
        st.markdown("<style>.stApp {background-color: #f0f2f6;}</style>", unsafe_allow_html=True)

# --- 2. الإعدادات واللوجوهات ---
st.set_page_config(page_title="Clinical PK Calculator", layout="centered")
if os.path.exists("bg.jpg"): set_page_bg_from_local('bg.jpg')

col_l, col_m, col_r = st.columns([1, 2, 1])
with col_l:
    if os.path.exists("college_logo.png"): st.image("college_logo.png", width=110)
with col_r:
    if os.path.exists("uni_logo.png"): st.image("uni_logo.png", width=110)

st.markdown("<h1>Clinical PK Dose Calculator</h1>", unsafe_allow_html=True)
st.markdown("<h4>Faculty of Pharmacy - Mansoura National University</h4>", unsafe_allow_html=True)

# --- 3. المربع الرئيسي والعناوين ---
st.markdown('''
<div class="main-container">
    <div class="custom-title">📋 Patient Clinical Profile</div>
''', unsafe_allow_html=True)

selected_drug = st.selectbox("💊 Select Medication", ["Vancomycin", "Gentamicin", "Digoxin"])

c1, c2 = st.columns(2)
with c1:
    age = st.number_input("Age (Years)", min_value=1, value=60)
    weight = st.number_input("Weight (kg)", min_value=10.0, value=80.0)
    gender = st.selectbox("Gender", ["Male", "Female"])
with c2:
    scr = st.number_input("SCr (mg/dL)", min_value=0.1, value=1.40)
    
    if selected_drug == "Vancomycin":
        target = st.slider("Target Trough (mg/L)", 10, 20, 15)
        intervals = [8, 12, 24, 48]
    elif selected_drug == "Gentamicin":
        target = st.slider("Target Trough (mg/L)", 0.5, 2.0, 1.0)
        intervals = [8, 12, 24]
    else: # Digoxin
        target = st.slider("Target CSS (ng/mL)", 0.5, 2.0, 0.8)
        intervals = [24, 48]
        
    interval = st.selectbox("Interval (Hours)", intervals)

# الحسابات العلمية
if gender == "Male": crcl = ((140 - age) * weight) / (72 * scr)
else: crcl = (((140 - age) * weight) / (72 * scr)) * 0.85

unit, step = ("mg", 250) if selected_drug == "Vancomycin" else ("mg", 20) if selected_drug == "Gentamicin" else ("mcg", 62.5)

if selected_drug == "Vancomycin":
    k, vd, ld_val = (0.00083 * crcl + 0.0044), (0.7 * weight), (25 * weight)
elif selected_drug == "Gentamicin":
    k, vd, ld_val = (0.00293 * crcl + 0.014), (0.25 * weight), (2 * weight)
else: # Digoxin
    k, vd, ld_val = ((0.0138 * crcl + 0.02) / 24), (7 * weight + (3 * crcl)), (10 * weight)

md = (target * k * vd * interval) / (1 - (2.71828 ** (-k * interval)))

if st.button("Generate Recommendation"):
    st.markdown("---")
    st.markdown(f'<div class="custom-title">📊 {selected_drug} PK Results</div>', unsafe_allow_html=True)
    m1, m2, m3 = st.columns(3)
    m1.metric("CrCl", f"{crcl:.1f}")
    m2.metric("Half-life", f"{0.693/k:.1f}h")
    m3.metric("Interval", f"{interval}h")
    
    f_ld = round(ld_val/step)*step
    f_md = round(md/step)*step
    st.success(f"**Recommendation:** {f_ld} {unit} LD, then {f_md} {unit} every {interval}h")
    
    # --- الجزء اللي كان ناقص (Safety & Monitoring) ---
    with st.expander("🛡️ Safety & Monitoring Plan"):
        if selected_drug == "Vancomycin":
            st.write("**TDM:** Check trough level before the 4th dose (Steady State).")
            st.write("**Renal:** Monitor Serum Creatinine daily for Nephrotoxicity.")
        elif selected_drug == "Gentamicin":
            st.write("**TDM:** Monitor Peak (efficacy) and Trough (safety).")
            st.write("**Toxicity:** Watch for Ototoxicity (Hearing) and Nephrotoxicity.")
        else: # Digoxin
            st.write("**TDM:** Level should be measured 6-8 hours post-dose.")
            st.write("**Safety:** Monitor Potassium levels (Hypokalemia increases toxicity risk).")

# قفل المربع
st.markdown('</div>', unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray; font-size: 0.8em;'>Clinical PK Project | MNU</p>", unsafe_allow_html=True)
