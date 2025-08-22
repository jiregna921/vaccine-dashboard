import streamlit as st
import pandas as pd
import re
import io
from config.thresholds import VACCINE_THRESHOLDS

# --- Custom CSS for improved styling ---
st.markdown("""
<style>
/* Overall page layout and styling */
.stApp {
    padding-top: 1rem;
    background-color: #05667F;
    color: white;
}

/* Header styling with background color and padding */
.main-header-container {
    background-color: #044b5e;
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

st.set_page_config(
    page_title="Data Processing",
    layout="wide",
    page_icon="⚙️"
)

# --- Check Authentication ---
if not st.session_state.get("authenticated", False):
    st.warning("Please log in on the main page to view this dashboard.")
    st.stop()

# --- Header with Logos and Title ---
col1, col2, col3 = st.columns([1, 4, 1])
with col1:
    st.image("assets/moh_logo.png", width=100)
with col2:
    st.markdown('<div class="main-header-container"><h1>Data Upload & Triangulation</h1></div>', unsafe_allow_html=True)
with col3:
    st.image("assets/eth_flag.png", width=100)

st.markdown("---")
st.markdown("<h3>Upload and Match Data</h3>", unsafe_allow_html=True)

# --- File Uploaders ---
# Added 'key' to force Streamlit to re-render and check for new files
admin_file = st.file_uploader("Upload Administered Doses File (Excel or CSV)", type=["xlsx", "csv"], key="admin_uploader")
dist_file = st.file_uploader("Upload Distributed Doses File (Excel or CSV)", type=["xlsx", "csv"], key="dist_uploader")

# --- Main action button row ---
action_col1, action_col2 = st.columns(2)

with action_col1:
    if st.button("Process and Match Data"):
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
                st.write(f"**Total Matched Records:** {len(matched_df)}")
                st.write(f"**Total Unmatched Administered Records:** {len(unmatched_admin_df)}")
                st.write(f"**Total Unmatched Distributed Records:** {len(unmatched_dist_df)}")

            except Exception as e:
                st.error(f"An error occurred during file processing: {e}")

with action_col2:
    if st.button("Reset Data"):
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
            st.dataframe(st.session_state["unmatched_admin_df"][["Woreda_Admin", "Period_Admin"]].head())
        else:
            st.info("No unmatched administered records found.")
    
    with col2:
        if "unmatched_dist_df" in st.session_state and not st.session_state["unmatched_dist_df"].empty:
            st.write("**Distributed Unmatched**")
            st.dataframe(st.session_state["unmatched_dist_df"][["Woreda_Dist", "Period_Dist"]].head())
        else:
            st.info("No unmatched distributed records found.")
else:
    st.info("Please upload and process files to see a summary.")
