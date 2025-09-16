import streamlit as st
import pandas as pd
import re
import time

st.set_page_config(
    page_title="Immunization Data Triangulation",
    layout="wide",
    page_icon="🩺"
)

# --- Custom CSS for styling ---
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
    color: #333333;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

/* Add padding to main container */
.main .block-container {
    padding-top: 2.5rem !important;
    padding-bottom: 2rem !important;
}

/* Header styling */
.main-header-container {
    background: linear-gradient(90deg, #0077b6 0%, #00b4d8 100%);
    padding: 1.5rem;
    border-radius: 12px;
    margin: 1.5rem 0 2rem 0;
    box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
    border-left: 5px solid #03045e;
    text-align: center;
}
.main-header-container h1 {
    color: white;
    margin: 0;
    font-size: 2rem;
    font-weight: 700;
    text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.2);
}

/* Sidebar */
[data-testid="stSidebar"] {
    color: #000000 !important;
}

/* File uploader */
.stFileUploader > div > div {
    background-color: #ffffff !important;
    border: 2px dashed #cfd8dc !important;
    border-radius: 8px !important;
    padding: 1rem !important;
    color: #212529 !important;
}
.stFileUploader button, .stFileUploader div[role="button"] {
    background: #ffffff !important;
    color: #212529 !important;
    border: 1px solid #ced4da !important;
}
.stFileUploader span, .stFileUploader p, .stFileUploader div {
    color: #212529 !important;
}

/* General buttons */
.stButton > button {
    background: linear-gradient(90deg, #00b4d8 0%, #0077b6 100%);
    color: #ffffff !important;
    border: none;
    padding: 0.7rem 1rem;
    border-radius: 8px;
    font-weight: 600;
    transition: all 0.25s ease;
    width: 100%;
}
.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 10px rgba(0,0,0,0.12);
}

/* Alerts */
.stSuccess, .stInfo, .stError, .stWarning {
    border-radius: 8px;
    padding: 0.85rem 1rem;
    margin: 0.9rem 0;
    font-weight: 600;
    color: #0b0b0b !important;
}
.stSuccess { background: #e9f7ef !important; border-left: 4px solid #28a745 !important; }
.stInfo { background: #e8f4fd !important; border-left: 4px solid #007bff !important; }
.stError { background: #f8d7da !important; border-left: 4px solid #dc3545 !important; }
.stWarning { background: #fff3cd !important; border-left: 4px solid #ffc107 !important; }

/* Metric cards */
.custom-metric-box {
    background: #f9fafb;
    padding: 1rem;
    border-radius: 10px;
    text-align: center;
    box-shadow: 0 3px 6px rgba(0,0,0,0.06);
    border: 1px solid #e6e9ec;
}
.custom-metric-label { color: #05667F; font-weight: 700; margin-bottom: 0.25rem; }
.custom-metric-value { font-size: 1.6rem; color: #034758; font-weight: 700; }

/* Dataframe text */
.dataframe th, .dataframe td { color: #212529 !important; }
</style>
""", unsafe_allow_html=True)

# ----------------- Authentication -----------------
if not st.session_state.get("authenticated", False):
    st.warning("Please log in on the main page to view this dashboard.")
    st.stop()

# ----------------- Sidebar -----------------
with st.sidebar:
    st.markdown("<h3 style='margin-bottom:0.1rem;'>Vaccine Data System</h3>", unsafe_allow_html=True)
    st.markdown("<div style='color:#6c757d; margin-bottom:1rem;'>Ministry of Health</div>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### Navigation")
    nav = st.radio("", ["🏠 Dashboard", "📊 Upload & Process", "📈 Analytics", "⚙️ Settings"], index=1, label_visibility="collapsed")
    st.markdown("---")
    st.markdown(f"**Username:** {st.session_state.get('username','User')}")
    st.markdown("**Role:** Data Manager")
    st.markdown("---")
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.clear()
        st.experimental_rerun()

# ----------------- Header -----------------
st.markdown('<div class="main-header-container"><h1>Vaccine Data Processing & Matching</h1></div>', unsafe_allow_html=True)

# ----------------- Info -----------------
st.markdown('<div class="stInfo">📌 <b>Info:</b> Upload administered and distributed vaccine files (.xlsx or .csv). After clicking <i>Process</i> the progress bar and spinner will show processing progress.</div>', unsafe_allow_html=True)

# ----------------- Upload -----------------
st.subheader("Upload Vaccine Data")
u_col1, u_col2 = st.columns(2)

with u_col1:
    st.markdown('<di
