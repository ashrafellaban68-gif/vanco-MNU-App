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
            display: block;
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

col_l, col_m, col_r =
