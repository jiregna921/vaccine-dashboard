import streamlit as st
import pandas as pd
import numpy as np
import io
import os
import re
from datetime import datetime
import time

st.set_page_config(
    page_title="Immunization Data Triangulation",
    layout="wide",
    page_icon="🩺"
)

# --- Enhanced Custom CSS for professional styling ---
st.markdown("""
<style>
/* Add top spacing so header isn't stuck */
.stApp {
    background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
    color: #333333;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    padding-top: 20px !important;  /* pushes everything down */
}

/* Header styling */
.main-header-container {
    background: linear-gradient(90deg, #0077b6 0%, #00b4d8 100%);
    padding: 1.5rem;
    border-radius: 12px;
    margin-bottom: 1.5rem;
    box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
    border-left: 5px solid #03045e;
}

.main-header-container h1 {
    color: white;
    margin: 0;
    text-align: center;
    font-size: 2rem;
    font-weight: 700;
    text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.2);
}

/* Logo alignment */
.logo-left, .logo-right, .logo-center {
    display: flex;
    align-items: center;
    padding: 0.5rem;
    background: rgba(255, 255, 255, 0.2);
    border-radius: 12px;
    height: 100%;
}
.logo-left { justify-content: flex-start; }
.logo-right { justify-content: flex-end; }
.logo-center { justify-content: center; }

/* Login container */
.login-container {
    background: white;
    padding: 2rem;
    border-radius: 12px;
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
    margin: 2rem auto;
    max-width: 500px;
}

/* Login header */
.login-header {
    text-align: center;
    color: #0077b6;
    margin-bottom: 1.5rem;
    font-weight: 600;
    background: linear-gradient(90deg, #0077b6 0%, #00b4d8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

/* Subtitle */
.subtitle {
    color: #5a6169;
    font-size: 1.1rem;
    text-align: center;
    margin-top: 0.5rem;
    font-weight: 400;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(90deg, #0077b6 0%, #00b4d8 100%);
    color: white !important;
    border: none;
    padding: 0.75rem 1.5rem;
    border-radius: 8px;
    font-weight: 600;
    transition: all 0.3s ease;
    width: 100%;
}
.stButton > button:hover {
    background: linear-gradient(90deg, #005b8a 0%, #0077b6 100%);
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

/* Input fields */
.stTextInput > div > div > input {
    border: 2px solid #e9ecef;
    border-radius: 8px;
    padding: 0.75rem;
    transition: all 0.3s ease;
    color: #000000 !important;
    background: #ffffff !important;
}
.stTextInput > div > div > input::placeholder {
    color: #6c757d !important;
}
.stTextInput label {
    color: #000000 !important;
    font-weight: 600;
}

/* Messages */
.stSuccess, .stInfo, .stError, .stWarning {
    border-radius: 4px !important;
    padding: 1rem !important;
    color: #000000 !important; /* black text */
}
.stSuccess {
    background: #d4f8e8 !important;
    border-left: 4px solid #28a745 !important;
}
.stInfo {
    background: #e6f0ff !important;
    border-left: 4px solid #007bff !important;
}
.stError {
    background: #fde2e2 !important;
    border-left: 4px solid #eb5757 !important;
}
.stWarning {
    background: #fff4e6 !important;
    border-left: 4px solid #ff9800 !important;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #f8f9fa !important;
    color: #000000 !important;
}
section[data-testid="stSidebar"] * {
    color: #000000 !important;
}

/* File uploader */
.stFileUploader {
    color: #000000 !important;
}
.stFileUploader label {
    color: #000000 !important;
    font-weight: 600;
}
.stFileUploader div[data-testid="stFileUploaderDropzone"] {
    background: #ffffff !important;
    color: #000000 !important;
    border: 2px dashed #0077b6;
}
.stFileUploader div[data-testid="stFileUploaderDropzone"] * {
    color: #000000 !important;
}

/* Welcome */
.welcome-message {
    background: white;
    padding: 2rem;
    border-radius: 12px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    text-align: center;
    margin: 2rem 0;
}
.welcome-icon {
    font-size: 3rem;
    margin-bottom: 1rem;
    color: #0077b6;
}

/* Feature cards */
.feature-card {
    background: white;
    padding: 1.5rem;
    border-radius: 12px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    text-align: center;
    height: 100%;
    transition: transform 0.3s ease;
}
.feature-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
}
.feature-icon {
    font-size: 2rem;
    color: #0077b6;
    margin-bottom: 1rem;
}
</style>
""", unsafe_allow_html=True)

# --- User Authentication (Simplified) ---
def login():
    st.session_state["authenticated"] = True

def logout():
    st.session_state.clear()
    st.rerun()

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

# --- Header ---
col1, col2, col3 = st.columns([1, 4, 1])
with col1:
    st.markdown('<div class="logo-left">', unsafe_allow_html=True)
    st.image("assets/moh_logo.png", width=100)
    st.markdown('</div>', unsafe_allow_html=True)
with col2:
    st.markdown('<div class="main-header-container"><h1>Immunization Data Triangulation Application</h1></div>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Comprehensive analysis of vaccine administration and distribution data</p>', unsafe_allow_html=True)
with col3:
    st.markdown('<div class="logo-right">', unsafe_allow_html=True)
    st.image("assets/eth_flag.png", width=100)
    st.markdown('</div>', unsafe_allow_html=True)

# Sidebar logout
if st.session_state["authenticated"]:
    st.sidebar.button("🚪 Logout", on_click=logout)

# --- Content ---
if not st.session_state["authenticated"]:
    st.markdown("---")
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    st.markdown('<h2 class="login-header">🔐 System Access</h2>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        username = st.text_input("👤 Username", placeholder="Enter your username")
        password = st.text_input("🔒 Password", type="password", placeholder="Enter your password")
        if st.button("🚀 Login", use_container_width=True):
            if username == "user" and password == "password":
                login()
                st.success("Logged in successfully!")
                st.rerun()
            else:
                st.error("Invalid username or password")
    st.markdown('</div>', unsafe_allow_html=True)
else:
    st.markdown("---")
    st.markdown('<div class="welcome-message">', unsafe_allow_html=True)
    st.markdown('<div class="welcome-icon">📈</div>', unsafe_allow_html=True)
    st.markdown('<h2 style="color: #0077b6; text-align: center;">Welcome to the Immunization Data Portal</h2>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">You are successfully logged in! Use the navigation menu to begin analyzing immunization data.</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # File upload
    uploaded_file = st.file_uploader("📂 Upload your data file", type=["csv", "xlsx"])
    if uploaded_file is not None:
        st.info("Data Processing started ...")
        progress = st.progress(0)
        for percent in range(100):
            time.sleep(0.02)
            progress.progress(percent + 1)
        st.success("Data processed successfully! (matching logic goes here)")
