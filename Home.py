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

# --- Custom CSS for improved styling ---
st.markdown("""
<style>
/* Overall page layout and styling */
.stApp {
    padding-top: 1rem;
    background-color: #05667F; /* Dark blue background */
    color: white; /* All text is white */
}

/* Header styling with background color and padding */
.main-header-container {
    background-color: #044b5e; /* Slightly darker shade of blue */
    padding: 1rem;
    border-radius: 10px;
    margin-bottom: 0.25rem;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.main-header-container h1 {
    color: white;
    margin: 0;
    text-align: center;
    font-size: 1.5rem;
}

/* Sidebar styling */
.sidebar .sidebar-content {
    background-color: #044b5e;
    color: white;
}

/* Custom metric boxes */
.custom-metric-box {
    background-color: #044b5e;
    padding: 0.5rem;
    border-radius: 10px;
    text-align: center;
    margin-bottom: 1rem;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.custom-metric-label {
    font-size: 1rem;
    font-weight: bold;
    color: white;
    margin-bottom: 0.25rem;
}

.custom-metric-value {
    font-size: 1.5rem;
    font-weight: bold;
    color: white;
}

/* Adjustments for logo */
.logo-container {
    display: flex;
    justify-content: center;
    align-items: center;
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
    st.image("assets/moh_logo.png", width=100)
with col2:
    st.markdown('<div class="main-header-container"><h1>Immunization Data Triangulation Application</h1></div>', unsafe_allow_html=True)
with col3:
    st.image("assets/eth_flag.png", width=100)

st.sidebar.button("Logout", on_click=logout)

if not st.session_state["authenticated"]:
    st.markdown("---")
    st.header("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username == "user" and password == "password": # Dummy credentials
            login()
            st.success("Logged in successfully! Navigate to the 'Data Processing' page in the sidebar to begin.")
        else:
            st.error("Invalid username or password")
    st.info("Hint: Use username 'user' and password 'password'")
else:
    st.markdown("---")
    st.success("You are logged in! Use the navigation menu on the left to select a page.")
