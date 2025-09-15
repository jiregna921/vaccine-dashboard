import streamlit as st
import pandas as pd
import re
import io
from config.thresholds import VACCINE_THRESHOLDS

# --- Enhanced Custom CSS with white background and black text ---
st.markdown("""
<style>
/* Overall page styling - White background */
.stApp {
    background: #ffffff;
    color: #333333;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

/* Header styling */
.main-header-container {
    background: linear-gradient(90deg, #05667F 0%, #034758 100%);
    padding: 1.5rem;
    border-radius: 12px;
    margin-bottom: 1.5rem;
    box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
    border-left: 5px solid #00b4d8;
}

.main-header-container h1 {
    color: white;
    margin: 0;
    text-align: center;
    font-size: 2rem;
    font-weight: 700;
    text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.2);
}

/* Section headers */
h3 {
    color: #05667F;
    border-bottom: 2px solid #00b4d8;
    padding-bottom: 0.5rem;
    margin-top: 1.5rem;
    font-weight: 600;
}

/* Card styling for metrics */
.custom-metric-box {
    background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
    padding: 1.2rem;
    border-radius: 12px;
    text-align: center;
    margin-bottom: 1.5rem;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.08);
    border: 1px solid #dee2e6;
    transition: transform 0.3s ease;
}

.custom-metric-box:hover {
    transform: translateY(-5px);
    box-shadow: 0 6px 12px rgba(0, 0, 0, 0.12);
}

.custom-metric-label {
    font-size: 1rem;
    font-weight: 600;
    color: #05667F;
    margin-bottom: 0.5rem;
}

.custom-metric-value {
    font-size: 1.8rem;
    font-weight: 700;
    color: #034758;
}

/* Button styling */
.stButton > button {
    background: linear-gradient(90deg, #00b4d8 0%, #0077b6 100%);
    color: white;
    border: none;
    padding: 0.75rem 1.5rem;
    border-radius: 8px;
    font-weight: 600;
    transition: all 0.3s ease;
    width: 100%;
}

.stButton > button:hover {
    background: linear-gradient(90deg, #0077b6 0%, #005b8a 100%);
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

/* File uploader styling */
.stFileUploader > div > div {
    background-color: #f8f9fa;
    border: 2px dashed #ced4da;
    border-radius: 8px;
    color: #495057;
}

.stFileUploader > div > div:hover {
    border-color: #00b4d8;
}

/* Dataframe styling */
.dataframe {
    background-color: #f8f9fa;
    border-radius: 8px;
    border: 1px solid #dee2e6;
}

/* Divider styling */
hr {
    height: 2px;
    background: linear-gradient(90deg, transparent 0%, #00b4d8 50%, transparent 100%);
    border: none;
    margin: 2rem 0;
}

/* Success and info messages */
.stSuccess {
    background: linear-gradient(90deg, rgba(0, 180, 216, 0.1) 0%, rgba(0, 180, 216, 0.05) 100%);
    border-left: 4px solid #00b4d8;
    border-radius: 4px;
    color: #034758;
}

.stInfo {
    background: linear-gradient(90deg, rgba(77, 171, 247, 0.1) 0%, rgba(77, 171, 247, 0.05) 100%);
    border-left: 4px solid #4dabf7;
    border-radius: 4px;
    color: #034758;
}

.stError {
    background: linear-gradient(90deg, rgba(235, 87, 87, 0.1) 0%, rgba(235, 87, 87, 0.05) 100%);
    border-left: 4px solid #eb5757;
    border-radius: 4px;
    color: #721c24;
}

/* Warning message */
.stWarning {
    background: linear-gradient(90deg, rgba(255, 193, 7, 0.1) 0%, rgba(255, 193, 7, 0.05) 100%);
    border-left: 4px solid #ffc107;
    border-radius: 4px;
    color: #856404;
}

/* Logo container */
.logo-container {
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 0.5rem;
    background: #f8f9fa;
    border-radius: 12px;
    border: 1px solid #dee2e6;
}

/* Column spacing */
.stColumn {
    padding: 0 1rem;
}

/* Text colors for better readability */
p, div, span {
    color: #333333 !important;
}

/* Table text color */
.dataframe th, .dataframe td {
    color: #333333 !important;
}

/* Metric numbers emphasis */
.metric-emphasis {
    font-weight: 700;
    color: #034758;
}

/* Upload section labels */
.upload-label {
    font-weight: 600;
    color: #05667F;
    margin-bottom: 0.5rem;
}
</style>
""", unsafe_allow_html=True)

st.set_page_config(
    page_title="Vaccine Data Processing",
    layout="wide",
    page_icon="⚕️"
)

# --- Check Authentication ---
if not st.session_state.get("authenticated", False):
    st.warning("Please log in on the main page to view this dashboard.")
    st.stop()

# --- Header with Logos and Title ---
col1, col2, col3 = st.columns([1, 4, 1])
with col1:
    st.markdown('<div class="logo-container">', unsafe_allow_html=True)
    st.image("assets/moh_logo.png", width=100)
    st.markdown('</div>', unsafe_allow_html=True)
    
with col2:
    st.markdown('<div class="main-header-container"><h1>Vaccine Data Upload & Triangulation</h1></div>', unsafe_allow_html=True)
    
with col3:
    st.markdown('<div class="logo-container">', unsafe_allow_html=True)
    st.image("assets/eth_flag.png", width=100)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")
st.markdown("<h3>Upload and Match Vaccine Data</h3>", unsafe_allow_html=True)

# --- File Uploaders with improved layout ---
upload_col1, upload_col2 = st.columns(2)

with upload_col1:
    st.markdown('<div class="custom-metric-box">', unsafe_allow_html=True)
    st.markdown('<div class="custom-metric-label">Administered Doses</div>', unsafe_allow_html=True)
    admin_file = st.file_uploader("Upload Excel or CSV file", type=["xlsx", "csv"], key="admin_uploader", label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)

with upload_col2:
    st.markdown('<div class="custom-metric-box">', unsafe_allow_html=True)
    st.markdown('<div class="custom-metric-label">Distributed Doses</div>', unsafe_allow_html=True)
    dist_file = st.file_uploader("Upload Excel or CSV file", type=["xlsx", "csv"], key="dist_uploader", label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)

# --- Main action button row ---
action_col1, action_col2, action_col3 = st.columns([2, 2, 1])

with action_col1:
    if st.button("📊 Process and Match Data", use_container_width=True):
        if admin_file is None or dist_file is None:
            st.error("Please upload both Administered and Distributed files.")
        else:
            try:
                # Function to read file based on extension
                def read_file(uploaded_file):
                    if uploaded_file.name.endswith('.csv'):
                        return pd.read_csv(uploaded_file)
                    else:
                        return pd.read_excel(uploaded_file)

                # Read and process files
                admin_df = read_file(admin_file)
                dist_df = read_file(dist_file)

                # Data Cleaning and Key Column Identification
                def clean_column_names(df):
                    df.columns = df.columns.str.strip().str.replace(' ', '_').str.replace('.', '').str.replace('-', '_').str.lower()
                    return df

                admin_df = clean_column_names(admin_df)
                dist_df = clean_column_names(dist_df)
                
                # --- Robust Key Column Identification ---
                def find_and_rename_cols(df, col_type):
                    """
                    Finds and renames columns based on a dictionary of patterns.
                    Returns a rename map and checks for essential columns.
                    """
                    patterns = {
                        'Woreda_Admin': ['woreda', 'woreda_administered', 'woreda_name', 'facility'],
                        'Region_Admin': ['region', 'region_administered', 'region_name'],
                        'Zone_Admin': ['zone', 'zone_administered', 'zone_name'],
                        'Period_Admin': ['period', 'month', 'date'],
                        'BCG_Administered': ['bcg', 'bcg_administered'],
                        'IPV_Administered': ['ipv', 'ipv_administered'],
                        'Measles_Administered': ['measles', 'measles_administered'],
                        'Penta_Administered': ['penta', 'penta_administered'],
                        'Rota_Administered': ['rota', 'rota_administered'],
                        'Woreda_Dist': ['woreda', 'woreda_distributed', 'woreda_name', 'facility'],
                        'Period_Dist': ['period', 'month', 'date'],
                        'BCG_Distributed': ['bcg', 'bcg_distributed', 'bcg_doses', 'bcg_dist'],
                        'IPV_Distributed': ['ipv', 'ipv_distributed', 'ipv_doses', 'ipv_dist'],
                        'Measles_Distributed': ['measles', 'measles_distributed', 'measles_doses', 'measles_dist'],
                        'Penta_Distributed': ['penta', 'penta_distributed', 'penta_doses', 'penta_dist'],
                        'Rota_Distributed': ['rota', 'rota_distributed', 'rota_doses', 'rota_dist']
                    }

                    rename_map = {}
                    found_cols = {}

                    if col_type == 'admin':
                        relevant_patterns = {k: v for k, v in patterns.items() if '_Admin' in k}
                    elif col_type == 'dist':
                        relevant_patterns = {k: v for k, v in patterns.items() if '_Dist' in k}
                    
                    for final_name, prefixes in relevant_patterns.items():
                        for raw_col in df.columns:
                            for prefix in prefixes:
                                if raw_col.startswith(prefix):
                                    if final_name not in found_cols:
                                        rename_map[raw_col] = final_name
                                        found_cols[final_name] = raw_col
                                        break
                        if final_name in found_cols:
                            continue

                    return rename_map, found_cols
                    
                # Find and rename Administered file columns
                admin_rename_map, admin_found_cols = find_and_rename_cols(admin_df, "admin")

                # Check for essential location columns
                essential_admin_cols = ['Woreda_Admin', 'Region_Admin', 'Zone_Admin', 'Period_Admin']
                if not all(col in admin_rename_map.values() for col in essential_admin_cols):
                    missing_cols = [col for col in essential_admin_cols if col not in admin_rename_map.values()]
                    st.error(f"Could not find essential columns in the Administered file: {missing_cols}. Please check your data.")
                    st.stop()
                
                # Find and rename Distributed file columns
                dist_rename_map, dist_found_cols = find_and_rename_cols(dist_df, "dist")
                
                # Check for essential distributed columns
                essential_dist_cols = ['Woreda_Dist', 'Period_Dist']
                if not all(col in dist_rename_map.values() for col in essential_dist_cols):
                    missing_cols = [col for col in essential_dist_cols if col not in dist_rename_map.values()]
                    st.error(f"Could not find essential columns in the Distributed file: {missing_cols}. Please check your data.")
                    st.stop()

                # Apply renaming
                admin_df = admin_df.rename(columns=admin_rename_map)
                dist_df = dist_df.rename(columns=dist_rename_map)

                # Normalize Woreda names for matching
                def normalize_woreda_name(name):
                    return re.sub(r'[^a-zA-Z0-9]', '', str(name)).lower()

                admin_df["woreda_normalized"] = admin_df["Woreda_Admin"].apply(normalize_woreda_name)
                dist_df["woreda_normalized"] = dist_df["Woreda_Dist"].apply(normalize_woreda_name)

                # Match based on normalized Woreda name and period
                matched_df = pd.merge(
                    admin_df,
                    dist_df,
                    left_on=["woreda_normalized", "Period_Admin"],
                    right_on=["woreda_normalized", "Period_Dist"],
                    how="inner",
                )
                
                # Remove duplicate period column
                matched_df = matched_df.drop(columns="Period_Dist")
                matched_df.rename(columns={"Period_Admin": "Period"}, inplace=True)
                
                # Store the final DataFrames and key names in session state
                st.session_state["matched_df"] = matched_df
                st.session_state["admin_df"] = admin_df
                st.session_state["dist_df"] = dist_df

                # Identify unmatched records
                unmatched_admin_df = admin_df[~admin_df["woreda_normalized"].isin(matched_df["woreda_normalized"])]
                unmatched_dist_df = dist_df[~dist_df["woreda_normalized"].isin(matched_df["woreda_normalized"])]

                st.session_state["unmatched_admin_df"] = unmatched_admin_df
                st.session_state["unmatched_dist_df"] = unmatched_dist_df

                st.success("Data processing and matching complete!")
                
                # Display metrics in a nice layout
                metric_col1, metric_col2, metric_col3 = st.columns(3)
                with metric_col1:
                    st.markdown('<div class="custom-metric-box">', unsafe_allow_html=True)
                    st.markdown('<div class="custom-metric-label">Matched Records</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="custom-metric-value">{len(matched_df)}</div>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                
                with metric_col2:
                    st.markdown('<div class="custom-metric-box">', unsafe_allow_html=True)
                    st.markdown('<div class="custom-metric-label">Unmatched Administered</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="custom-metric-value">{len(unmatched_admin_df)}</div>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                
                with metric_col3:
                    st.markdown('<div class="custom-metric-box">', unsafe_allow_html=True)
                    st.markdown('<div class="custom-metric-label">Unmatched Distributed</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="custom-metric-value">{len(unmatched_dist_df)}</div>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)

            except Exception as e:
                st.error(f"An error occurred during file processing: {e}")

with action_col2:
    if st.button("🔄 Reset Data", use_container_width=True):
        # Explicitly clear all data from session state
        st.session_state.clear()
        st.success("Data reset complete. Please upload new files.")
        st.experimental_rerun()

# --- Display Status ---
st.markdown("---")

if "matched_df" in st.session_state:
    st.success("Files are ready for analysis on the dashboard pages.")
else:
    st.info("Please upload and process datasets to enable dashboards.")
    
st.markdown("---")
st.markdown("<h3>Summary of Unmatched Data</h3>", unsafe_allow_html=True)

if "unmatched_admin_df" in st.session_state and "unmatched_dist_df" in st.session_state:
    st.write("Below are records from the administered and distributed files that could not be matched based on Woreda and Period.")
    
    col1, col2 = st.columns(2)
    with col1:
        if "unmatched_admin_df" in st.session_state and not st.session_state["unmatched_admin_df"].empty:
            st.write("**Administered Unmatched**")
            st.dataframe(st.session_state["unmatched_admin_df"][["Woreda_Admin", "Period_Admin"]].head(), use_container_width=True)
        else:
            st.info("No unmatched administered records found.")
    
    with col2:
        if "unmatched_dist_df" in st.session_state and not st.session_state["unmatched_dist_df"].empty:
            st.write("**Distributed Unmatched**")
            st.dataframe(st.session_state["unmatched_dist_df"][["Woreda_Dist", "Period_Dist"]].head(), use_container_width=True)
        else:
            st.info("No unmatched distributed records found.")
else:
    st.info("Please upload and process files to see a summary.")
