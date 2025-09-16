import streamlit as st
import pandas as pd
import numpy as np
import io
import os
import re
from datetime import datetime

# ------------------ PAGE CONFIG ------------------
st.set_page_config(
    page_title="Immunization Data Triangulation",
    layout="wide",
    page_icon="🩺"
)

# ------------------ CUSTOM CSS ------------------
st.markdown("""
<style>
/* Overall page styling */
.stApp {
    background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
    color: #333333;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    overflow-x: hidden;
}

/* Header container */
.main-header-container {
    background: linear-gradient(90deg, #0077b6 0%, #00b4d8 100%);
    padding: 1rem;
    border-radius: 12px;
    margin: 0 auto 1rem auto;
    box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    border-left: 5px solid #03045e;
    max-width: 95%;
}

/* Header title */
.main-header-container h1 {
    color: #fff;
    margin: 0;
    text-align: center;
    font-size: 1.8rem;
    font-weight: 700;
    text-shadow: 1px 1px 3px rgba(0,0,0,0.25);
}

/* Subheader */
.subtitle {
    color: #333;
    text-align: center;
    margin-top: 0.25rem;
    font-size: 1rem;
}

/* Logo containers */
.logo-left, .logo-right {
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 0.25rem;
    height: 100%;
}

/* Login container */
.login-container {
    background: #fff;
    padding: 1.5rem;
    border-radius: 12px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    margin: 1rem auto;
    max-width: 420px;
    text-align: center;
}

.login-header {
    color: #0077b6;
    font-weight: 700;
    margin-bottom: 1rem;
    font-size: 1.4rem;
}

/* Input fields */
.stTextInput > div > div > input {
    border: 2px solid #e9ecef;
    border-radius: 8px;
    padding: 0.5rem;
    color: #000 !important;
}
.stTextInput > div > div > input:focus {
    border-color: #0077b6;
    box-shadow: 0 0 0 2px rgba(0,119,182,0.15);
}
.stTextInput > div > div > input::placeholder {
    color: #6c757d !important;
}
.stTextInput label {
    color: #000 !important;
    font-weight: 600;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(90deg, #0077b6 0%, #00b4d8 100%);
    color: #fff;
    border: none;
    padding: 0.6rem 1rem;
    border-radius: 8px;
    font-weight: 600;
    transition: all 0.3s ease;
}
.stButton > button:hover {
    background: linear-gradient(90deg, #005b8a 0%, #0077b6 100%);
    transform: translateY(-2px);
}

/* Cards */
.feature-card {
    background: #fff;
    padding: 1rem;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    text-align: center;
    height: 100%;
    transition: transform 0.25s ease;
}
.feature-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}
.feature-icon {
    font-size: 1.8rem;
    color: #0077b6;
    margin-bottom: 0.5rem;
}
.feature-description {
    font-size: 0.9rem;
    color: #555;
}

/* Welcome box */
.welcome-message {
    background: #fff;
    padding: 1.5rem;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    text-align: center;
    margin: 1rem auto;
    max-width: 95%;
}
.welcome-icon {
    font-size: 2.2rem;
    margin-bottom: 0.5rem;
    color: #0077b6;
}

/* Credentials info */
.credentials-box {
    background: #f1faff;
    padding: 0.75rem;
    border-radius: 8px;
    border-left: 4px solid #0077b6;
    margin: 0.5rem auto 1rem auto;
    max-width: 400px;
    font-size: 0.9rem;
    color: #333;
}
</style>
""", unsafe_allow_html=True)

# ------------------ AUTH FUNCTIONS ------------------
def login():
    st.session_state["authenticated"] = True

def logout():
    st.session_state.clear()
    st.rerun()

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

# ------------------ HEADER ------------------
col1, col2, col3 = st.columns([1, 5, 1])
with col1:
    st.image("assets/moh_logo.png", width=80)
with col2:
    st.markdown('<div class="main-header-container"><h1>Immunization Data Triangulation Application</h1></div>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Comprehensive analysis of vaccine administration and distribution data</p>', unsafe_allow_html=True)
with col3:
    st.image("assets/eth_flag.png", width=80)

# ------------------ AUTHENTICATION ------------------
if st.session_state["authenticated"]:
    st.sidebar.button("🚪 Logout", on_click=logout)

if not st.session_state["authenticated"]:
    # LOGIN FORM
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    st.markdown('<h2 class="login-header">🔐 System Access</h2>', unsafe_allow_html=True)

    username = st.text_input("👤 Username", placeholder="Enter your username")
    password = st.text_input("🔒 Password", type="password", placeholder="Enter your password")

    if st.button("🚀 Login", use_container_width=True):
        if username == "user" and password == "password":  # Demo credentials
            login()
            st.success("Logged in successfully! Please refresh the page to continue.")
        else:
            st.error("Invalid username or password")

    st.markdown('</div>', unsafe_allow_html=True)

    # DEMO INFO + FEATURES
    st.markdown('<div class="credentials-box">💡 Demo Login → Username: <b>user</b> | Password: <b>password</b></div>', unsafe_allow_html=True)

    cols = st.columns(3)
    with cols[0]:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📥</div>
            <h4 style="color:#0077b6;">Data Management</h4>
            <p class="feature-description">Upload and process immunization datasets from multiple sources.</p>
        </div>""", unsafe_allow_html=True)
    with cols[1]:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📊</div>
            <h4 style="color:#0077b6;">Analysis Tools</h4>
            <p class="feature-description">Evaluate utilization rates and identify discrepancies instantly.</p>
        </div>""", unsafe_allow_html=True)
    with cols[2]:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📋</div>
            <h4 style="color:#0077b6;">Reporting</h4>
            <p class="feature-description">Export visual reports in Excel, PDF, or PowerPoint formats.</p>
        </div>""", unsafe_allow_html=True)

else:
    # WELCOME SECTION
    st.markdown('<div class="welcome-message"><div class="welcome-icon">📈</div><h2 style="color:#0077b6;">Welcome to the Immunization Data Portal</h2><p class="subtitle">You are successfully logged in! Use the sidebar to start analyzing immunization data.</p></div>', unsafe_allow_html=True)

    cols = st.columns(3)
    with cols[0]:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📥</div>
            <h4 style="color:#0077b6;">Data Upload</h4>
            <p class="feature-description">Upload administered and distributed vaccine data in multiple formats.</p>
        </div>""", unsafe_allow_html=True)
    with cols[1]:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📊</div>
            <h4 style="color:#0077b6;">Dashboard</h4>
            <p class="feature-description">Track vaccine utilization trends, discrepancies, and performance metrics.</p>
        </div>""", unsafe_allow_html=True)
    with cols[2]:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📋</div>
            <h4 style="color:#0077b6;">Reports</h4>
            <p class="feature-description">Generate and export reports for decision-making support.</p>
        </div>""", unsafe_allow_html=True)
