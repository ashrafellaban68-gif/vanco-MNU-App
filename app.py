import streamlit as st
import os
import base64

# --- 1. وظيفة الخلفية والستايل الشفاف ---
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
        .custom-title {{ 
            color: white; 
            font-size: 18px; 
            font-weight: bold; 
            background: linear-gradient(90deg, #1e3a8a, #3b82f6);
            padding: 10px 20px; 
            border-radius: 12px; 
            margin-bottom: 25px; 
            text-align: center;
            box-shadow: 0 4px 15px rgba(30, 58, 138, 0.2);
        }}
        .main-header {{ color: #1e3a8a; text-align: center; font-weight: 800; font-size: 32px; margin-bottom: 5px; }}
        .sub-header {{ color: #475569; text-align: center; font-size: 18px; font-weight: 500; margin-bottom: 25px; }}
        .stButton>button {{ 
            background: linear-gradient(45deg, #1e3a8a, #1e40af);
            color: white; font-weight: bold; border-radius: 15px; height: 3.5em; width: 100%;
        }}
        </style>
        ''', unsafe_allow_html=True)
    except:
        st.markdown("<style>.stApp {background-color: #f8fafc;}</style>", unsafe_allow_html=True)

# --- 2. الإعدادات واللوجوهات ---
st.set_page_config(page_title="AED PK Calculator", layout="centered")
if os.path.exists("bg.jpg"):
    set_page_bg_from_local('bg.jpg')

col_l, col_m, col_r = st.columns([1, 2, 1])
with col_l:
    if os.path.exists("uni_logo.png"): st.image("uni_logo.png", width=85)
with col_r:
    if os.path.exists("college_logo.png"): st.image("college_logo.png", width=85)

st.markdown('<div class="main-header">AED Dose Calculator</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Faculty of Pharmacy<br>Mansoura National University</div>', unsafe_allow_html=True)

# --- 3. المحتوى الشفاف ---
st.markdown('<div class="custom-title">📋 Patient Clinical Profile (AEDs)</div>', unsafe_allow_html=True)

selected_drug = st.selectbox("💊 Select Antiepileptic Drug (AED)", ["Phenytoin", "Valproic acid", "Carbamazepine", "Levetiracetam"])
calc_type = st.radio("Calculation Type", ["Initial Regimen", "Dose Adjustment"], horizontal=True)
diagnosis = st.text_input("Diagnosis / Clinical Condition")

st.markdown("<hr style='opacity: 0.1; margin: 20px 0;'>", unsafe_allow_html=True)

c1, c2 = st.columns(2)
with c1:
    age = st.number_input("Age (Years)", min_value=1, value=30)
    weight = st.number_input("Weight (kg)", min_value=10.0, value=70.0)
    height = st.number_input("Height (cm)", min_value=50, value=170)
    gender = st.selectbox("Gender", ["Male", "Female"])
with c2:
    scr = st.number_input("Serum Creatinine (mg/dL)", min_value=0.1, value=1.0, format="%.2f")
    interval_options = [4, 6, 8, 12, 24, 48]
    if selected_drug == "Phenytoin":
        target = st.slider("Target CSS (mg/L)", 10, 20, 15); interval = st.selectbox("Interval (Hours)", interval_options, index=4)
    elif selected_drug == "Valproic acid":
        target = st.slider("Target CSS (mg/L)", 50, 100, 75); interval = st.selectbox("Interval (Hours)", interval_options, index=3)
    elif selected_drug == "Carbamazepine":
        target = st.slider("Target CSS (mg/L)", 4, 12, 8); interval = st.selectbox("Interval (Hours)", interval_options, index=3)
    else:
        target = st.slider("Target CSS (mg/L)", 12, 46, 20); interval = st.selectbox("Interval (Hours)", interval_options, index=3)

# الحسابات
if gender == "Male": crcl = ((140 - age) * weight) / (72 * scr)
else: crcl = (((140 - age) * weight) / (72 * scr)) * 0.85

if selected_drug == "Phenytoin":
    vmax, km = 7 * weight, 4; md = (vmax * target) / (km + target); ld_val, unit, step = 15 * weight, "mg", 50
elif selected_drug == "Valproic acid":
    cl = 0.008 * weight; vd = 0.15 * weight; k = cl / vd
    md = (target * cl * interval) / (1 - (2.71828 ** (-k * interval))); ld_val, unit, step = 20 * weight, "mg", 250
elif selected_drug == "Carbamazepine":
    cl = 0.06 * weight; vd = 1.4 * weight; k = cl / vd; md = (target * cl * interval); ld_val, unit, step = 0, "mg", 200
else: # Levetiracetam
    cl = (crcl * 0.6) / 1000 * 60; vd = 0.6 * weight; k = cl / vd; md = (target * cl * interval); ld_val, unit, step = 1000, "mg", 500

if st.button("Generate AED Recommendation"):
    st.markdown("<br><div class='custom-title' style='background: #10b981;'>📊 Results</div>", unsafe_allow_html=True)
    m1, m2, m3 = st.columns(3)
    m1.metric("CrCl", f"{crcl:.1f}")
    m2.metric("Target", f"{target} mg/L")
    m3.metric("t½ (h)", f"{0.693/(k):.1f}" if selected_drug != "Phenytoin" else "N/A")
    
    f_md = round(md/step)*step
    st.success(f"**Recommendation:** Give {round(ld_val/50)*50 if ld_val>0 else 'no'} mg LD, then {f_md} {unit} every {interval}h.")
    
    # --- رجعنا كل تفاصيل الـ Monitoring هنا ---
    with st.expander("🛡️ Full AED Monitoring & Safety Plan"):
        st.info(f"Clinical Guidance for **{selected_drug}**")
        if selected_drug == "Phenytoin":
            st.warning("**Saturation Kinetics:** Small dose increases can cause toxic jumps in plasma levels.")
            st.write("1. **Lab Monitoring:** Monitor Free Phenytoin if Albumin is low (< 3.5 g/dL).")
            st.write("2. **CBC:** Check for blood dyscrasias.")
            st.write("3. **Side Effects:** Watch for Nystagmus, Ataxia, and Gingival Hyperplasia.")
        elif selected_drug == "Valproic acid":
            st.warning("**High Protein Binding:** Displaced by other drugs like Aspirin.")
            st.write("1. **Liver Safety:** Periodic LFTs (Liver Function Tests) are mandatory.")
            st.write("2. **Pancreas:** Monitor for symptoms of Pancreatitis.")
            st.write("3. **Toxicity:** Monitor Ammonia levels if confusion occurs.")
        elif selected_drug == "Carbamazepine":
            st.warning("**Auto-induction:** Clearane increases after 2-4 weeks; dose may need adjustment.")
            st.write("1. **Skin Safety:** Screen for HLA-B*1502 to avoid SJS/TEN.")
            st.write("2. **Electrolytes:** Monitor for Hyponatremia (SIADH).")
            st.write("3. **CBC:** Monitor for Aplastic Anemia (rare but serious).")
        else: # Levetiracetam
            st.write("1. **Renal Function:** Must adjust dose if CrCl drops.")
            st.write("2. **Psychiatric:** Monitor for 'Keppra-rage' (Irritability, Depression).")
            st.write("3. **Interactions:** Low protein binding = fewer drug interactions.")

st.markdown("<br><p style='text-align: center; color: #64748b; font-size: 0.8em;'>Clinical PK Project | MNU</p>", unsafe_allow_html=True)
