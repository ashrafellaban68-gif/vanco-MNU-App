import streamlit as st
import os
import base64

# --- 1. وظيفة الخلفية والستايل الـ Premium ---
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
        background-image: linear-gradient(rgba(255, 255, 255, 0.7), rgba(255, 255, 255, 0.7)), {bg_img};
        background-size: cover;
        background-attachment: fixed;
    }}
    
    .logo-img {{
        width: 100px;
        filter: drop-shadow(0px 4px 8px rgba(0,0,0,0.2)) brightness(1.1);
        margin-bottom: 5px;
    }}
    
    .hero-header {{
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        padding: 20px;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(30, 58, 138, 0.4);
        margin-bottom: 10px;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }}
    
    .hero-header h1 {{
        color: white !important;
        text-align: center;
        font-weight: 900 !important;
        font-size: 32px !important;
        margin: 0;
    }}

    .university-label {{
        color: #1e3a8a;
        text-align: center;
        font-weight: 700;
        font-size: 17px;
        margin-top: 10px;
        margin-bottom: 25px;
    }}
    
    .glass-title {{
        background: rgba(30, 58, 138, 0.9);
        color: white;
        padding: 10px 20px;
        border-radius: 50px;
        font-weight: bold;
        text-align: center;
        width: fit-content;
        margin: 15px auto;
    }}

    .stButton>button {{
        background: linear-gradient(45deg, #1e3a8a, #3b82f6);
        color: white;
        border-radius: 50px;
        font-weight: bold;
        width: 100%;
        height: 3.5em;
    }}
    </style>
    ''', unsafe_allow_html=True)

# --- 2. الإعدادات واللوجو ---
st.set_page_config(page_title="AED PK Pro", layout="centered")
set_page_style('bg.jpg' if os.path.exists("bg.jpg") else "")

# اللوجو "على جنب" (يسار)
if os.path.exists("my_logo.png"):
    col_l, col_r = st.columns([1, 4])
    with col_l:
        logo_b64 = base64.b64encode(open("my_logo.png", "rb").read()).decode()
        st.markdown(f'<img src="data:image/png;base64,{logo_b64}" class="logo-img">', unsafe_allow_html=True)

# العنوان
st.markdown('''
    <div class="hero-header">
        <h1>AED PK CALCULATOR</h1>
    </div>
    <div class="university-label">
        Faculty of Pharmacy <br> Mansoura National University
    </div>
''', unsafe_allow_html=True)

# --- 3. المحتوى ---
st.markdown('<div class="glass-title">📋 Patient Clinical Profile</div>', unsafe_allow_html=True)

selected_drug = st.selectbox("💊 Select Drug", ["Phenytoin", "Valproic acid", "Carbamazepine", "Levetiracetam"])
calc_type = st.radio("Calculation Type", ["Initial Regimen", "Dose Adjustment"], horizontal=True)

st.divider()

col1, col2 = st.columns(2)
with col1:
    age = st.number_input("Age (Years)", 1, 100, 30)
    weight = st.number_input("Weight (kg)", 10.0, 150.0, 70.0)
    height = st.number_input("Height (cm)", 50, 250, 170)
with col2:
    gender = st.selectbox("Gender", ["Male", "Female"])
    scr = st.number_input("Serum Creatinine", 0.1, 5.0, 1.0)
    target = st.slider("Target Conc (mg/L)", 5, 100, 15)

interval = st.selectbox("Dosing Interval (Hours)", [4, 6, 8, 12, 24, 48], index=3)

# الحسابات العلمية
if gender == "Male": crcl = ((140 - age) * weight) / (72 * scr)
else: crcl = (((140 - age) * weight) / (72 * scr)) * 0.85

if selected_drug == "Phenytoin":
    vmax, km = 7 * weight, 4; md = (vmax * target) / (km + target); ld_val, unit, step = 15 * weight, "mg", 50
elif selected_drug == "Valproic acid":
    cl = 0.008 * weight; vd = 0.15 * weight; k = cl / vd; md = (target * cl * interval) / (1 - (2.71828 ** (-k * interval))); ld_val, unit, step = 20 * weight, "mg", 250
elif selected_drug == "Carbamazepine":
    cl = 0.06 * weight; vd = 1.4 * weight; k = cl / vd; md = (target * cl * interval); ld_val, unit, step = 0, "mg", 200
else: # Levetiracetam
    cl = (crcl * 0.6) / 1000 * 60; vd = 0.6 * weight; k = cl / vd; md = (target * cl * interval); ld_val, unit, step = 1000, "mg", 500

if st.button("Generate Recommendation"):
    st.markdown('<div class="glass-title" style="background: #10b981;">📊 Final Results</div>', unsafe_allow_html=True)
    m1, m2, m3 = st.columns(3)
    m1.metric("CrCl", f"{crcl:.1f}")
    m2.metric("Target", f"{target}")
    m3.metric("t½ (h)", f"{0.693/k:.1f}" if selected_drug != "Phenytoin" else "N/A")
    
    f_md = round(md/step)*step
    st.success(f"**Final Plan:** Give {round(ld_val/50)*50 if ld_val>0 else 'no'} mg LD, then {f_md} {unit} every {interval}h.")

    # --- استرجاع جزء Monitoring & Safety ---
    with st.expander("🛡️ Clinical Monitoring & Safety Plan"):
        st.info(f"Clinical Guidance for **{selected_drug}**")
        if selected_drug == "Phenytoin":
            st.warning("**Saturation Kinetics:** Small dose increases can cause toxic jumps.")
            st.write("- **Monitoring:** Monitor SCr and Albumin levels (Free Phenytoin).")
            st.write("- **Side Effects:** Watch for Nystagmus, Ataxia, and Gingival Hyperplasia.")
        elif selected_drug == "Valproic acid":
            st.write("- **Liver Safety:** Periodic LFTs are mandatory.")
            st.write("- **Toxicity:** Watch for Ammonia levels and Pancreatitis symptoms.")
        elif selected_drug == "Carbamazepine":
            st.warning("**Auto-induction:** Metabolism increases after 2-4 weeks.")
            st.write("- **Skin Safety:** Screen for HLA-B*1502 risk.")
            st.write("- **Electrolytes:** Monitor for Hyponatremia.")
        else: # Levetiracetam
            st.write("- **Renal:** Adjust dose strictly based on CrCl.")
            st.write("- **Psychiatric:** Monitor for behavioral changes (Irritability).")

st.markdown("<br><p style='text-align: center; color: #1e3a8a; font-weight: bold;'>Clinical PK Project | MNU</p>", unsafe_allow_html=True)
