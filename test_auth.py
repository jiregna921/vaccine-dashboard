import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import os

st.set_page_config(page_title="Auth Test", layout="centered")

# --- Load Config ---
config_file_path = "config.yaml"
try:
    with open(config_file_path) as file:
        config = yaml.load(file, Loader=SafeLoader)
except Exception as e:
    st.error(f"Error loading config: {e}")
    st.stop()

# --- Authenticator ---
try:
    authenticator = stauth.Authenticate(
        credentials=config["credentials"],
        cookie_name=config["cookie"]["name"],
        cookie_key=config["cookie"]["key"],
        cookie_expiry_days=config["cookie"]["expiry_days"],
    )

    # --- Login Form ---
    name, authentication_status, username = authenticator.login("Login", "sidebar")

    # --- Display Status ---
    if authentication_status:
        st.success(f"Login successful for {name}!")
    elif authentication_status is False:
        st.error("Username/password is incorrect")
    elif authentication_status is None:
        st.warning("Please enter your username and password")

except Exception as e:
    st.error(f"An error occurred during authentication: {str(e)}")
    st.stop()