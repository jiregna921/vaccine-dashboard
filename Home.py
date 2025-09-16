import streamlit as st
import pandas as pd
import numpy as np
import io
import os
import re
from datetime import datetime

st.set_page_config(
    page_title="Immunization Data Triangulation",
    layout="wide",
    page_icon="🩺"
)

# --- Enhanced Custom CSS for professional styling ---
st.markdown("""
<style>
/* Overall page styling */
.stApp {
    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    color: #212529;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

/* Header styling */
.main-header-container {
    background: linear-gradient(90deg, #0077b6 0%, #00b4d8 100%);
    padding: 1rem;
    border-radius: 10px;
    margin-bottom: 1rem;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    border-left: 5px solid #03045e;
}
.main-header-container h1 {
    color: white;
    text-align: center;
    font-size: 1.8rem;
    font-weight: 700;
    margin: 0;
}

/* Subtitle */
.subtitle {
    color: #495057;
    font-size: 1rem;
    text-align: center;
    margin-top: 0.25rem;
}

/* Login container */
.login-container {
    background: white;
    padding: 1.5rem;
    border-radius: 10px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    margin: auto;
    max-width: 400px;
}

/* Input fields */
.stTextInput > div > div > input {
    background-color: #ffffff !important;
    color: #000000 !important;
    border: 2px solid #ced4da !important;
    border-radius: 6px;
    padding: 0.6rem;
}
.stTextInput > div > div > input:focus {
    border-color: #0077b6 !important;
    box-shadow: 0 0 0 2px rgba(0,119,182,0.2) !important;
}
.stTextInput > div > div > input::placeholder {
    color: #6c757d !important;
}
.stTextInput label {
    color: #000000 !important;
    font-weight: 600;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(90deg, #0077b6 0%, #00b4d8 100%);
    color: white !important;
    border: none;
    padding: 0.6rem 1rem;
    border-radius: 6px;
    font-weight: 600;
    transition: all 0.3s ease;
}
.stButton > button:hover {
    background: linear-gradient(90deg, #005b8a 0%, #0077b6 100%);
    transform: translateY(-2px);
    box-shadow: 0 3px 6px rgba(0,0,0,0.15);
}

/* Messages */
.stSuccess {
    background: #d1e7dd !important;
    border-left: 4px solid #0f5132 !important;
    color: #0f5132 !important;
    font-weight: 600;
    padding: 1rem !important;
    border-radius: 6px !important;
}
.stInfo {
    background: #cff4fc !important;
    border-left: 4px solid #055160 !important;
    color: #055160 !important;
    font-weight: 600;
    padding: 1rem !important;
    border-radius: 6px !important;
}
.stError {
    background: #f8d7da !important;
    border-left: 4px solid #842029 !important;
    color: #842029 !important;
    font-weight: 600;
    padding: 1rem !important;
    border-radius: 6px !important;
}

/* Feature cards */
.feature-card {
    background: white;
    padding: 1rem;
    border-radius: 10px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.1);
    text-align: center;
    transition: transform 0.3s ease;
}
.feature-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 4px 10px rgba(0,0,0,0.15);
}
.feature-icon {
    font-size: 1.8rem;
    color: #0077b6;
    margin-bottom: 0.5rem;
}

/* Welcome message */
.welcome-message {
    background: white;
    padding: 1.5rem;
    border-radius: 10px;
    box-shadow: 0 3px 8px rgba(0,0,0,0.1);
    text-align: center;
    margin: 1rem 0;
}
.welcome-icon {
    font-size: 2rem;
    margin-bottom: 0.5rem;
    color: #0077b6;
}
</style>
""", unsafe_allow_html=True)

# --- User Authentication ---
def login():
    st.session_state["authenticated"] = True

def logout():
    st.session_state.clear()
    st.rerun()

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

# --- Page Header ---
col1, col2, col3 = st.columns([1,4,1])
with col1:
    st.image("assets/moh_logo.png", width=100)
with col2:
    st.markdown('<div class="main-header-container"><h1>Immunization Data Triangulation Application</h1></div>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Comprehensive analysis of vaccine administration and distribution data</p>', unsafe_allow_html=True)
with col3:
    st.image("assets/eth_flag.png", width=100)

if st.session_state["authenticated"]:
    st.sidebar.button("🚪 Logout", on_click=logout)

# --- Login Page ---
if not st.session_state["authenticated"]:
    st.markdown("---")
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    st.markdown('<h2 style="color:#0077b6;text-align:center;">🔐 System Access</h2>', unsafe_allow_html=True)

    username = st.text_input("👤 Username", placeholder="Enter your username")
    password = st.text_input("🔒 Password", type="password", placeholder="Enter your password")
    login_button = st.button("🚀 Login", use_container_width=True)

    if login_button:
        if username == "user" and password == "password":  # Demo credentials
            login()
            st.success("✅ Logged in successfully! Refresh the page to continue.")
        else:
            st.error("❌ Invalid username or password")

    st.markdown('</div>', unsafe_allow_html=True)
else:
    st.markdown("---")
    st.markdown('<div class="welcome-message">', unsafe_allow_html=True)
    st.markdown('<div class="welcome-icon">📈</div>', unsafe_allow_html=True)
    st.markdown('<h2 style="color: #0077b6; text-align: center;">Welcome to the Immunization Data Portal</h2>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">You are successfully logged in! Use the navigation menu to begin analyzing immunization data.</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""<div class="feature-card"><div class="feature-icon">📥</div><h3 style='color: #0077b6;'>Data Upload</h3><p>Upload administered and distributed vaccine data.</p></div>""", unsafe_allow_html=True)
    with col2:
        st.markdown("""<div class="feature-card"><div class="feature-icon">📊</div><h3 style='color: #0077b6;'>Analysis Dashboard</h3><p>Analyze vaccine utilization rates and track metrics.</p></div>""", unsafe_allow_html=True)
    with col3:
        st.markdown("""<div class="feature-card"><div class="feature-icon">📋</div><h3 style='color: #0077b6;'>Reporting</h3><p>Generate reports and export in Excel, PDF, and PPT.</p></div>""", unsafe_allow_html=True)
