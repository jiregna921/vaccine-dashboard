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
    background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
    color: #333333;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
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

/* Logo alignment adjustments */
.logo-left {
    display: flex;
    justify-content: flex-start;
    align-items: center;
    padding: 0.5rem;
    background: rgba(255, 255, 255, 0.2);
    border-radius: 12px;
    height: 100%;
}

.logo-right {
    display: flex;
    justify-content: flex-end;
    align-items: center;
    padding: 0.5rem;
    background: rgba(255, 255, 255, 0.2);
    border-radius: 12px;
    height: 100%;
}

.logo-center {
    display: flex;
    justify-content: center;
    align-items: center;
}

/* Login container styling */
.login-container {
    background: white;
    padding: 2rem;
    border-radius: 12px;
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
    margin: 2rem auto;
    max-width: 500px;
}

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

/* Subtitle styling */
.subtitle {
    color: #5a6169;
    font-size: 1.1rem;
    text-align: center;
    margin-top: 0.5rem;
    font-weight: 400;
}

.feature-subtitle {
    color: #0077b6;
    font-size: 1.1rem;
    font-weight: 600;
    margin-bottom: 0.5rem;
    margin-top: 1rem;
}

.feature-description {
    color: #5a6169;
    margin-bottom: 0.5rem;
    line-height: 1.5;
}

/* Button styling */
.stButton > button {
    background: linear-gradient(90deg, #0077b6 0%, #00b4d8 100%);
    color: white;
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

/* Input field styling */
.stTextInput > div > div > input {
    border: 2px solid #e9ecef;
    border-radius: 8px;
    padding: 0.75rem;
    transition: all 0.3s ease;
}

.stTextInput > div > div > input:focus {
    border-color: #0077b6;
    box-shadow: 0 0 0 2px rgba(0, 119, 182, 0.2);
}

/* Success and info messages */
.stSuccess {
    background: linear-gradient(90deg, rgba(0, 180, 216, 0.1) 0%, rgba(0, 180, 216, 0.05) 100%);
    border-left: 4px solid #00b4d8;
    border-radius: 4px;
    color: #005b8a;
}

.stInfo {
    background: linear-gradient(90deg, rgba(77, 171, 247, 0.1) 0%, rgba(77, 171, 247, 0.05) 100%);
    border-left: 4px solid #4dabf7;
    border-radius: 4px;
    color: #005b8a;
}

.stError {
    background: linear-gradient(90deg, rgba(235, 87, 87, 0.1) 0%, rgba(235, 87, 87, 0.05) 100%);
    border-left: 4px solid #eb5757;
    border-radius: 4px;
    color: #8b0000;
}

/* Sidebar styling */
.sidebar .sidebar-content {
    background: linear-gradient(180deg, #0077b6 0%, #03045e 100%);
    color: white;
}

/* Logout button */
.sidebar .stButton > button {
    background: linear-gradient(90deg, #e63946 0%, #d90429 100%);
}

.sidebar .stButton > button:hover {
    background: linear-gradient(90deg, #d90429 0%, #9d0208 100%);
}

/* Welcome message */
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

/* Divider styling */
hr {
    height: 2px;
    background: linear-gradient(90deg, transparent 0%, #00b4d8 50%, transparent 100%);
    border: none;
    margin: 2rem 0;
}

/* Credentials info box */
.credentials-box {
    background: linear-gradient(135deg, #e6f7ff 0%, #f0f8ff 100%);
    padding: 1rem;
    border-radius: 8px;
    border-left: 4px solid #0077b6;
    margin: 1rem 0;
}

/* Feature list styling */
.feature-list {
    list-style-type: none;
    padding-left: 0;
}

.feature-list li {
    margin-bottom: 1.5rem;
    padding-left: 0;
}
</style>
""", unsafe_allow_html=True)

# --- User Authentication (Simplified) ---
def login():
    st.session_state["authenticated"] = True

def logout():
    st.session_state.clear()
    st.experimental_rerun()

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

# --- Page Content ---
# --- Header with Logos and Title ---
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

if st.session_state["authenticated"]:
    st.sidebar.button("🚪 Logout", on_click=logout)

if not st.session_state["authenticated"]:
    st.markdown("---")
    
    # Login form in a centered container
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    st.markdown('<h2 class="login-header">🔐 System Access</h2>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        username = st.text_input("👤 Username", placeholder="Enter your username")
        password = st.text_input("🔒 Password", type="password", placeholder="Enter your password")
        
        if st.button("🚀 Login", use_container_width=True):
            if username == "user" and password == "password": # Dummy credentials
                login()
                st.success("Logged in successfully!")
                st.experimental_rerun()
            else:
                st.error("Invalid username or password")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Info section
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div class="credentials-box">
            <p class="feature-subtitle">💡 Demo Credentials</p>
            <p>Use username <strong>user</strong> and password <strong>password</strong></p>
        </div>
        """, unsafe_allow_html=True)
        
        # Features list - FIXED HTML STRUCTURE
        st.markdown("""
        <div class="feature-card">
            <h3 style='color: #0077b6; text-align: center;'>📊 Application Features</h3>
            <ul class="feature-list">
                <li>
                    <p class="feature-subtitle">Data Management</p>
                    <p class="feature-description">Upload and process immunization data from multiple sources</p>
                </li>
                <li>
                    <p class="feature-subtitle">Analysis Tools</p>
                    <p class="feature-description">Analyze vaccine utilization rates and identify discrepancies</p>
                </li>
                <li>
                    <p class="feature-subtitle">Reporting</p>
                    <p class="feature-description">Generate comprehensive reports with visualization</p>
                </li>
                <li>
                    <p class="feature-subtitle">Export Capabilities</p>
                    <p class="feature-description">Export data for further analysis in multiple formats</p>
                </li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
else:
    st.markdown("---")
    
    # Welcome message with icon and description
    st.markdown('<div class="welcome-message">', unsafe_allow_html=True)
    st.markdown('<div class="welcome-icon">📈</div>', unsafe_allow_html=True)
    st.markdown('<h2 style="color: #0077b6; text-align: center;">Welcome to the Immunization Data Portal</h2>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">You are successfully logged in! Use the navigation menu to begin analyzing immunization data.</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Quick stats or features overview
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📥</div>
            <h3 style='color: #0077b6;'>Data Upload</h3>
            <p class="feature-description">Upload administered and distributed vaccine data for analysis with support for multiple file formats</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📊</div>
            <h3 style='color: #0077b6;'>Analysis Dashboard</h3>
            <p class="feature-description">Analyze vaccine utilization rates, identify discrepancies, and track performance metrics</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📋</div>
            <h3 style='color: #0077b6;'>Reporting</h3>
            <p class="feature-description">Generate comprehensive reports and export data in Excel, PDF, and PowerPoint formats</p>
        </div>
        """, unsafe_allow_html=True)
