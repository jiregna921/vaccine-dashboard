import streamlit as st
import time
import io
import pandas as pd
from config.thresholds import VACCINE_THRESHOLDS

# --- Page Config ---
st.set_page_config(
    page_title="Vaccine Data Processing",
    layout="wide",
    page_icon="⚕️"
)

# --- Enhanced Custom CSS ---
st.markdown("""
<style>
/* General page styling */
.stApp {
    background: #ffffff;
    color: #333333;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

/* Sidebar */
.stSidebar {
    background-color: #f8f9fa !important;
    border-right: 1px solid #dee2e6;
}
.stSidebar h1, .stSidebar h2, .stSidebar h3, .stSidebar h4, .stSidebar h5, .stSidebar h6,
.stSidebar p, .stSidebar label, .stSidebar div, .stSidebar button {
    color: #212529 !important;  /* Dark text for contrast */
}

/* Header container */
.main-header-container {
    background: linear-gradient(90deg, #05667F 0%, #034758 100%);
    padding: 1.5rem;
    border-radius: 12px;
    margin: 2rem auto 1rem auto;  /* Push down from the very top */
    box-shadow: 0 6px 12px rgba(0, 0, 0, 0.12);
    border-left: 5px solid #00b4d8;
    text-align: center;
}
.main-header-container h1 {
    color: white;
    margin: 0;
    font-size: 2rem;
    font-weight: 700;
    text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.25);
}

/* Section headers */
h2 {
    color: #05667F;
    border-bottom: 2px solid #00b4d8;
    padding-bottom: 0.4rem;
    margin-top: 1.5rem;
    font-weight: 600;
}

/* Metric cards */
.custom-metric-box {
    background: #f9f9f9;
    padding: 1rem;
    border-radius: 10px;
    text-align: center;
    margin-bottom: 1rem;
    box-shadow: 0 3px 6px rgba(0, 0, 0, 0.06);
    border: 1px solid #e0e0e0;
    transition: transform 0.2s ease;
}
.custom-metric-box:hover {
    transform: translateY(-3px);
    box-shadow: 0 6px 10px rgba(0, 0, 0, 0.12);
}
.custom-metric-label {
    font-size: 0.95rem;
    font-weight: 600;
    color: #05667F;
}
.custom-metric-value {
    font-size: 1.8rem;
    font-weight: 700;
    color: #034758;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(90deg, #00b4d8 0%, #0077b6 100%);
    color: white;
    border: none;
    padding: 0.7rem 1rem;
    border-radius: 8px;
    font-weight: 600;
    transition: all 0.3s ease;
    width: 100%;
}
.stButton > button:hover {
    background: linear-gradient(90deg, #0077b6 0%, #005b8a 100%);
    transform: translateY(-1px);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.18);
}

/* Alerts */
.stSuccess, .stInfo, .stError, .stWarning {
    border-radius: 6px;
    padding: 0.9rem 1rem;
    margin: 0.8rem 0;
    font-weight: 500;
}
.stSuccess {
    background: #e9f7ef;
    border-left: 4px solid #28a745;
    color: #155724;
}
.stInfo {
    background: #e8f4fd;
    border-left: 4px solid #007bff;
    color: #034758;
}
.stError {
    background: #f8d7da;
    border-left: 4px solid #dc3545;
    color: #721c24;
}
.stWarning {
    background: #fff3cd;
    border-left: 4px solid #ffc107;
    color: #856404;
}

/* File uploader */
.stFileUploader > div > div {
    background-color: #f9f9f9;
    border: 2px dashed #cfd8dc;
    border-radius: 8px;
    padding: 1.2rem;
    color: #495057;
}
.stFileUploader > div > div:hover {
    border-color: #00b4d8;
    background-color: #f0f4f8;
}

/* Dataframe tables */
.dataframe {
    background: white;
    border-radius: 8px;
    border: 1px solid #e0e0e0;
}
.dataframe th, .dataframe td {
    color: #333333 !important;
}

/* Reduce excess spacing */
.block-container {
    padding-top: 0.5rem;
    padding-bottom: 1.5rem;
}
</style>
""", unsafe_allow_html=True)

# --- Authentication check ---
if not st.session_state.get("authenticated", False):
    st.warning("Please log in on the main page to view this dashboard.")
    st.stop()

# --- Header ---
st.markdown('<div class="main-header-container"><h1>Vaccine Data Processing & Matching</h1></div>', unsafe_allow_html=True)

# --- Info message ---
st.markdown("""
<div class="stInfo">
<b>Info:</b> Upload administered and distributed vaccine data files to process and match records. Supported formats: Excel (.xlsx) and CSV.
</div>
""", unsafe_allow_html=True)

# --- File Upload Section ---
st.subheader("Upload Vaccine Data")
upload_col1, upload_col2 = st.columns(2)
with upload_col1:
    st.markdown('<div class="custom-metric-box">', unsafe_allow_html=True)
    st.markdown('<div class="custom-metric-label">Administered Doses File</div>', unsafe_allow_html=True)
    admin_file = st.file_uploader("Upload Excel or CSV", type=["xlsx", "csv"], key="admin_upload", label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)

with upload_col2:
    st.markdown('<div class="custom-metric-box">', unsafe_allow_html=True)
    st.markdown('<div class="custom-metric-label">Distributed Doses File</div>', unsafe_allow_html=True)
    dist_file = st.file_uploader("Upload Excel or CSV", type=["xlsx", "csv"], key="dist_upload", label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)

# --- Action buttons ---
action_col1, action_col2 = st.columns([2,1])
with action_col1:
    process_btn = st.button("📊 Process and Match Data", use_container_width=True)
with action_col2:
    reset_btn = st.button("🔄 Reset Data", use_container_width=True)

# --- Placeholder for further processing logic ---
if process_btn:
    if admin_file is None or dist_file is None:
        st.error("Please upload both Administered and Distributed files.")
    else:
        st.success("✅ Data processing started...")

        # Progress bar + spinner
        progress = st.progress(0)
        with st.spinner("Processing data, please wait..."):
            for i in range(100):
                time.sleep(0.03)  # Simulated processing time
                progress.progress(i + 1)

        st.success("🎉 Data processed successfully! (matching logic goes here)")

if reset_btn:
    st.session_state.clear()
    st.success("Data reset complete. Please upload new files.")
    st.experimental_rerun()
