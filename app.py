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
            background-size: cover; background-attachment: fixed;
        }}
        .aesthetic-box {{
            width: 100%; background: rgba(255, 255, 255, 0.95);
            border-radius: 25px; border-collapse: separate; overflow: hidden;
            box-shadow: 0 15px 35px rgba(30, 58, 138, 0.15);
            border: 1px solid rgba(30, 58, 138, 0.1);
        }}
        .main-cell {{ padding: 30px; }}
        .custom-title {{ 
            color: white; font-size: 20px; font-weight: bold; 
            background: linear-gradient(90deg, #1e3a8a, #3b82f6);
            padding: 12px 20px; border-radius: 12px; margin-bottom: 25px; text-align: center;
        }}
        .stButton>button {{ 
            background: linear-gradient(45deg, #1e3a8a, #1e40af);
            color: white; font-weight: bold; border-radius: 15px; height: 3.5em;
        }}
        </style>
        ''', unsafe_allow_html=True)
    except:
        st.markdown("<style>.stApp {background-color: #f8fafc;}</style>", unsafe_allow_html=True)

# --- 2. الإعدادات ---
st.set_page_config(page_title="AED PK Calculator", layout="centered")
if os.path.exists("bg.jpg"):
    set_page_bg_from_local('bg.jpg')

col_l, col_m, col_r = st.columns([1, 2, 1])
with col_l:
    if os.path.exists("college_logo.png"): st.image("college_logo.png", width=85)
with col_r:
    if os.path.exists("uni_logo.png"): st.image("uni_logo.png", width=85)

st.markdown("<h1>AED Dose Calculator</h1>", unsafe_allow_html=True)
st.markdown("<h4>Faculty of Pharmacy - Mansoura National University</h4>", unsafe_allow_html=True)

# --- 3. المربع الجمالي ---
st.markdown('''
<table class="aesthetic-box">
    <tr>
        <td class="main-cell">
            <div class="custom-title">📋 Patient Clinical Profile (AEDs)</div>
''', unsafe_allow_html=True)

# أدوية الصرع من الصورة
selected_drug = st.selectbox("💊 Select Antiepileptic Drug (AED)", [
    "Phenytoin", 
    "Valproic acid", 
    "Carbamazepine",
    "Levetiracetam"
])

calc_type = st.radio("Calculation Type", ["Initial Regimen", "Dose Adjustment"], horizontal=True)
diagnosis = st.text_input("Diagnosis (e.g., Tonic-Clonic Seizures, Focal Epilepsy)")

st.markdown("<hr style='opacity: 0.1; margin: 20px 0;'>", unsafe_allow_html=True)

c1, c2 = st.columns(2)
with c1:
    age = st.number_input("Age (Years)", min_value=1, value=30)
    weight = st.number_input("Weight (kg)", min_value=10.0, value=70.0)
    height = st.number_input("Height (cm)", min_value=50, value=170)
    gender = st.selectbox("Gender", ["Male", "Female"])
with c2:
    scr = st.number_input("Serum Creatinine (mg/dL)", min_value=0.1, value=1.0, format="%.2f")
    # أهداف التركيز لأدوية الصرع (Therapeutic Ranges)
    if selected_drug == "Phenytoin":
        target = st.slider("Target CSS (mg/L)", 10, 20, 15)
        interval = st.selectbox("Interval (Hours)", [8, 12, 24])
    elif selected_drug == "Valproic acid":
        target = st.slider("Target CSS (mg/L)", 50, 100, 75)
        interval = st.selectbox("Interval (Hours)", [8, 12])
    elif selected_drug == "Carbamazepine":
        target = st.slider("Target CSS (mg/L)", 4, 12, 8)
        interval = st.selectbox("Interval (Hours)", [6, 8, 12])
    else: # Levetiracetam
        target = st.slider("Target CSS (mg/L)", 12, 46, 20)
        interval = st.selectbox("Interval (Hours)", [12])

# --- الحسابات العلمية ---
# CrCl
if gender == "Male": crcl = ((140 - age) * weight) / (72 * scr)
else: crcl = (((140 - age) * weight) / (72 * scr)) * 0.85

# Drug Parameters (Simplified Clinical Estimates)
if selected_drug == "Phenytoin":
    # Michaelis-Menten (Vmax/Km)
    vmax = 7 * weight
    km = 4
    md = (vmax * target) / (km + target)
    ld_val = 15 * weight
    unit, step = "mg", 50
elif selected_drug == "Valproic acid":
    cl = 0.008 * weight * 1000 # ml/hr
    vd = 0.15 * weight
    k = cl / (vd * 1000)
    md = (target * k * vd * interval) / (1 - (2.71828 ** (-k * interval)))
    ld_val = 20 * weight
    unit, step = "mg", 250
elif selected_drug == "Carbamazepine":
    cl = 0.06 * weight * 1000
    vd = 1.4 * weight
    k = cl / (vd * 1000)
    md = (target * k * vd * interval) / (1 - (2.71828 ** (-k * interval)))
    ld_val = 0 # No LD usually
    unit, step = "mg", 200
else: # Levetiracetam
    cl = (crcl * 0.6) * 60 # ml/hr
    vd = 0.6 * weight
    k = cl / (vd * 1000)
    md = (target * k * vd * interval) / (1 - (2.71828 ** (-k * interval)))
    ld_val = 1000
    unit, step = "mg", 500

if st.button("Generate AED Recommendation"):
    st.markdown("<br><div class='custom-title' style='background: #10b981;'>📊 Results</div>", unsafe_allow_html=True)
    m1, m2, m3 = st.columns(3)
    m1.metric("CrCl", f"{crcl:.1f}")
    m2.metric("Target", f"{target} mg/L")
    m3.metric("Interval", f"{interval}h")
    
    f_md = round(md/step)*step
    if ld_val > 0:
        st.success(f"**Recommendation:** Give {round(ld_val/50)*50} mg Loading Dose, then {f_md} {unit} every {interval}h.")
    else:
        st.success(f"**Recommendation:** Start {f_md} {unit} every {interval}h (Titrate slowly).")
    
    with st.expander("🛡️ AED Monitoring & Safety"):
        if selected_drug == "Phenytoin":
            st.write("- **Zero-order kinetics:** Small dose changes lead to large concentration jumps.\n- **Monitoring:** Check Albumin level.")
        elif selected_drug == "Valproic acid":
            st.write("- **Monitoring:** Liver Function Tests (LFTs) and Ammonia levels.\n- **Safety:** Teratogenic (Avoid in pregnancy).")
        elif selected_drug == "Carbamazepine":
            st.write("- **Auto-induction:** Drug clearance increases after 2-4 weeks.\n- **Safety:** Check for HLA-B*1502 in Asian patients (SJS risk).")
        else:
            st.write("- **Renal Adjustment:** Primarily cleared by kidneys.\n- **Safety:** Monitor for behavioral/psychiatric side effects.")

st.markdown('</td></tr></table>', unsafe_allow_html=True)
st.markdown("<br><p style='text-align: center; color: #64748b; font-size: 0.8em;'>AED PK Project | MNU</p>", unsafe_allow_html=True)
