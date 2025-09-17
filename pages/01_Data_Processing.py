import streamlit as st
import pandas as pd
import re
import time

st.set_page_config(
    page_title="Immunization Data Triangulation",
    layout="wide",
    page_icon="🩺"
)

# --- Enhanced Custom CSS for styling ---
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
    color: #333333;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

/* Add padding to main container */
.main .block-container {
    padding-top: 2rem !important;
    padding-bottom: 2rem !important;
    max-width: 95% !important;
}

/* Header styling */
.main-header-container {
    background: linear-gradient(90deg, #005792 0%, #0086B3 100%);
    padding: 1.8rem;
    border-radius: 12px;
    margin: 1.5rem 0 2.5rem 0;
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.12);
    border-left: 6px solid #003655;
    text-align: center;
}
.main-header-container h1 {
    color: white;
    margin: 0;
    font-size: 2.4rem;
    font-weight: 800;
    text-shadow: 1px 1px 4px rgba(0, 0, 0, 0.25);
    letter-spacing: 0.5px;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #f0f8ff 0%, #e1f5fe 100%) !important;
    color: #000000 !important;
    padding: 1rem;
}
[data-testid="stSidebar"] .stButton button {
    background: linear-gradient(90deg, #0086B3 0%, #005792 100%) !important;
}

/* File uploader */
.stFileUploader > div > div {
    background-color: #ffffff !important;
    border: 2px dashed #0077b6 !important;
    border-radius: 10px !important;
    padding: 1.5rem !important;
    color: #212529 !important;
    transition: all 0.3s ease;
}
.stFileUploader > div > div:hover {
    border-color: #005792 !important;
    background-color: #f8fdff !important;
}
.stFileUploader button, .stFileUploader div[role="button"] {
    background: #ffffff !important;
    color: #212529 !important;
    border: 1px solid #ced4da !important;
    border-radius: 6px !important;
}
.stFileUploader span, .stFileUploader p, .stFileUploader div {
    color: #212529 !important;
}

/* General buttons */
.stButton > button {
    background: linear-gradient(90deg, #0086B3 0%, #005792 100%);
    color: #ffffff !important;
    border: none;
    padding: 0.8rem 1.2rem;
    border-radius: 8px;
    font-weight: 600;
    transition: all 0.25s ease;
    width: 100%;
    box-shadow: 0 4px 6px rgba(0, 119, 182, 0.2);
}
.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
    background: linear-gradient(90deg, #0077b6 0%, #004d73 100%);
}

/* Alerts - Improved contrast */
.stSuccess, .stInfo, .stError, .stWarning {
    border-radius: 10px;
    padding: 1rem 1.2rem;
    margin: 1rem 0;
    font-weight: 600;
    border-left: 5px solid;
    box-shadow: 0 4px 8px rgba(0,0,0,0.08);
}
.stSuccess {
  background: #d4edda !important;
  color: #0f5132 !important;
  border-left-color: #198754 !important;
}

.stInfo {
  background: #d1ecf1 !important;
  color: #055160 !important;
  border-left-color: #0dcaf0 !important;
}

.stError {
  background: #f8d7da !important;
  color: #842029 !important;
  border-left-color: #dc3545 !important;
}

.stWarning {
  background: #fff3cd !important;
  color: #664d03 !important;
  border-left-color: #ffc107 !important;
}

/* Metric cards */
.custom-metric-box {
    background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
    padding: 1.2rem;
    border-radius: 12px;
    text-align: center;
    box-shadow: 0 4px 8px rgba(0,0,0,0.08);
    border: 1px solid #e3e8ee;
    transition: all 0.3s ease;
    height: 100%;
}
.custom-metric-box:hover {
    transform: translateY(-3px);
    box-shadow: 0 6px 12px rgba(0,0,0,0.1);
}
.custom-metric-label { 
    color: #005792; 
    font-weight: 700; 
    margin-bottom: 0.5rem;
    font-size: 0.9rem;
}
.custom-metric-value { 
    font-size: 1.8rem; 
    color: #003655; 
    font-weight: 800; 
}

/* Progress bar */
.stProgress > div > div {
    background: linear-gradient(90deg, #0086B3 0%, #005792 100%);
}

/* Dataframe styling */
.dataframe {
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 4px 8px rgba(0,0,0,0.08);
}
.dataframe th {
    background: linear-gradient(90deg, #0086B3 0%, #005792 100%) !important;
    color: white !important;
    font-weight: 700;
}
.dataframe td {
    background-color: #ffffff !important;
    color: #212529 !important;
}

/* Section headers */
h2, h3 {
    border-bottom: 2px solid #0086B3;
    padding-bottom: 0.5rem;
    color: #005792;
}

/* Spinner color */
.stSpinner > div {
    border-top-color: #0086B3 !important;
}

/* Card style for sections */
.section-card {
    background: white;
    border-radius: 12px;
    padding: 1.5rem;
    box-shadow: 0 4px 8px rgba(0,0,0,0.08);
    margin-bottom: 1.5rem;
    border-left: 4px solid #0086B3;
}
</style>
""", unsafe_allow_html=True)

# ----------------- Authentication -----------------
if not st.session_state.get("authenticated", False):
    st.warning("Please log in on the main page to view this dashboard.")
    st.stop()

# ----------------- Sidebar -----------------
with st.sidebar:
    st.markdown("<h2 style='margin-bottom:0.5rem; color: #005792;'>Vaccine Data System</h2>", unsafe_allow_html=True)
    st.markdown("<div style='color:#6c757d; margin-bottom:1.5rem;'>Ministry of Health</div>", unsafe_allow_html=True)
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
st.markdown("""
<div class="section-card">
    <h3 style="margin-top: 0; color: #005792;">Instructions</h3>
    <p>Upload administered and distributed vaccine files (.xlsx or .csv). The system will automatically:</p>
    <ol>
        <li>Detect and standardize column names</li>
        <li>Match records by Woreda and Period</li>
        <li>Identify unmatched records for review</li>
    </ol>
    <p>After clicking <b>Process</b>, the progress bar and spinner will show processing status.</p>
</div>
""", unsafe_allow_html=True)

# ----------------- Upload -----------------
st.subheader("Upload Vaccine Data")
u_col1, u_col2 = st.columns(2)

with u_col1:
    st.markdown('<div class="custom-metric-box">', unsafe_allow_html=True)
    st.markdown('<div class="custom-metric-label">Administered Doses File</div>', unsafe_allow_html=True)
    admin_file = st.file_uploader("Drag & drop or click to browse", type=["xlsx", "csv"], key="admin_upload", 
                                 help="Upload file with vaccine administration data", label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)

with u_col2:
    st.markdown('<div class="custom-metric-box">', unsafe_allow_html=True)
    st.markdown('<div class="custom-metric-label">Distributed Doses File</div>', unsafe_allow_html=True)
    dist_file = st.file_uploader("Drag & drop or click to browse", type=["xlsx", "csv"], key="dist_upload", 
                                help="Upload file with vaccine distribution data", label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)

# ----------------- Buttons -----------------
a_col, r_col = st.columns([2, 1])
with a_col:
    process_btn = st.button("📊 Process and Match Data", use_container_width=True, 
                           help="Process the uploaded files and match records")
with r_col:
    reset_btn = st.button("🔄 Reset Data", use_container_width=True, 
                         help="Clear all uploaded data and start over")

status_ph = st.empty()

# ----------------- Processing -----------------
def read_file(uploaded_file):
    if uploaded_file.name.lower().endswith(".csv"):
        return pd.read_csv(uploaded_file)
    else:
        return pd.read_excel(uploaded_file)

def clean_column_names(df):
    df.columns = (
        df.columns.str.strip()
        .str.replace(' ', '_', regex=False)
        .str.replace('.', '', regex=False)
        .str.replace('-', '_', regex=False)
        .str.lower()
    )
    return df

def find_and_rename_cols(df, col_type):
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
        relevant_patterns = {k: v for k, v in patterns.items() if '_admin' in k.lower()}
    else:
        relevant_patterns = {k: v for k, v in patterns.items() if '_dist' in k.lower()}

    for final_name, prefixes in relevant_patterns.items():
        for raw_col in df.columns:
            for prefix in prefixes:
                if raw_col.startswith(prefix):
                    if final_name not in found_cols:
                        rename_map[raw_col] = final_name
                        found_cols[final_name] = raw_col
                        break
            if final_name in found_cols:
                break

    return rename_map, found_cols

if process_btn:
    if admin_file is None or dist_file is None:
        status_ph.markdown("""
        <div class="stError">
            <b>⚠️ Missing Files</b><br>
            Please upload both Administered and Distributed files to proceed.
        </div>
        """, unsafe_allow_html=True)
    else:
        status_ph.markdown("""
        <div class="stInfo">
            <b>ℹ️ Processing Started</b><br>
            Reading and analyzing your vaccine data files...
        </div>
        """, unsafe_allow_html=True)
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Step 1: read files
            status_text.text("Reading files...")
            admin_df = read_file(admin_file)
            dist_df = read_file(dist_file)
            progress_bar.progress(10)
            time.sleep(0.5)

            # Step 2: clean column names
            status_text.text("Cleaning column names...")
            admin_df = clean_column_names(admin_df)
            dist_df = clean_column_names(dist_df)
            progress_bar.progress(25)
            time.sleep(0.5)

            # Step 3: rename columns
            status_text.text("Identifying key columns...")
            admin_rename_map, admin_found = find_and_rename_cols(admin_df, "admin")
            dist_rename_map, dist_found = find_and_rename_cols(dist_df, "dist")
            progress_bar.progress(45)
            time.sleep(0.5)

            essential_admin = ['Woreda_Admin', 'Region_Admin', 'Zone_Admin', 'Period_Admin']
            if not all(col in admin_rename_map.values() for col in essential_admin):
                missing = [c for c in essential_admin if c not in admin_rename_map.values()]
                status_ph.markdown(f"""
                <div class="stError">
                    <b>❌ Missing Essential Admin Columns</b><br>
                    Could not find: {', '.join(missing)}<br>
                    Please check your Administered file structure and try again.
                </div>
                """, unsafe_allow_html=True)
                progress_bar.empty()
                status_text.empty()
                st.stop()

            essential_dist = ['Woreda_Dist', 'Period_Dist']
            if not all(col in dist_rename_map.values() for col in essential_dist):
                missing = [c for c in essential_dist if c not in dist_rename_map.values()]
                status_ph.markdown(f"""
                <div class="stError">
                    <b>❌ Missing Essential Distributed Columns</b><br>
                    Could not find: {', '.join(missing)}<br>
                    Please check your Distributed file structure and try again.
                </div>
                """, unsafe_allow_html=True)
                progress_bar.empty()
                status_text.empty()
                st.stop()

            # Step 4: apply renaming
            status_text.text("Standardizing column names...")
            admin_df = admin_df.rename(columns=admin_rename_map)
            dist_df = dist_df.rename(columns=dist_rename_map)
            progress_bar.progress(60)
            time.sleep(0.5)

            # Step 5: normalize woreda names
            status_text.text("Normalizing location names...")
            def normalize_woreda_name(name):
                return re.sub(r'[^a-zA-Z0-9]', '', str(name)).lower()
            admin_df["woreda_normalized"] = admin_df["Woreda_Admin"].apply(normalize_woreda_name)
            dist_df["woreda_normalized"] = dist_df["Woreda_Dist"].apply(normalize_woreda_name)
            progress_bar.progress(75)
            time.sleep(0.5)

            # Step 6: match
            status_text.text("Matching records...")
            matched_df = pd.merge(
                admin_df,
                dist_df,
                left_on=["woreda_normalized", "Period_Admin"],
                right_on=["woreda_normalized", "Period_Dist"],
                how="inner",
            )
            if "Period_Dist" in matched_df:
                matched_df = matched_df.drop(columns="Period_Dist")
            matched_df.rename(columns={"Period_Admin": "Period"}, inplace=True)
            progress_bar.progress(90)
            time.sleep(0.5)

            # Save session
            st.session_state["matched_df"] = matched_df
            st.session_state["admin_df"] = admin_df
            st.session_state["dist_df"] = dist_df
            st.session_state["unmatched_admin_df"] = admin_df[~admin_df["woreda_normalized"].isin(matched_df["woreda_normalized"])]
            st.session_state["unmatched_dist_df"] = dist_df[~dist_df["woreda_normalized"].isin(matched_df["woreda_normalized"])]

            progress_bar.progress(100)
            status_text.text("Complete!")
            time.sleep(0.5)
            
            status_ph.markdown("""
            <div class="stSuccess">
                <b>✅ Processing Complete</b><br>
                Data successfully processed and matched. Files are ready for dashboard analysis.
            </div>
            """, unsafe_allow_html=True)

            # Metrics
            st.markdown("### Processing Results")
            mcol1, mcol2, mcol3 = st.columns(3)
            mcol1.markdown(f'<div class="custom-metric-box"><div class="custom-metric-label">Matched Records</div><div class="custom-metric-value">{len(matched_df):,}</div></div>', unsafe_allow_html=True)
            mcol2.markdown(f'<div class="custom-metric-box"><div class="custom-metric-label">Unmatched Admin</div><div class="custom-metric-value">{len(st.session_state["unmatched_admin_df"]):,}</div></div>', unsafe_allow_html=True)
            mcol3.markdown(f'<div class="custom-metric-box"><div class="custom-metric-label">Unmatched Dist</div><div class="custom-metric-value">{len(st.session_state["unmatched_dist_df"]):,}</div></div>', unsafe_allow_html=True)

            progress_bar.empty()
            status_text.empty()

        except Exception as e:
            status_ph.markdown(f"""
            <div class="stError">
                <b>❌ Processing Error</b><br>
                An unexpected error occurred: {str(e)}<br>
                Please check your file formats and try again.
            </div>
            """, unsafe_allow_html=True)
            progress_bar.empty()
            status_text.empty()

if reset_btn:
    for key in list(st.session_state.keys()):
        if key != "authenticated" and key != "username":
            del st.session_state[key]
    st.success("""
    <div class="stSuccess">
        <b>🔁 Data Reset</b><br>
        All uploaded data has been cleared. You can now upload new files.
    </div>
    """, unsafe_allow_html=True)
    st.experimental_rerun()

# ----------------- Summary -----------------
st.markdown("---")
st.markdown("""
<div class="section-card">
    <h3>Summary of Unmatched Data</h3>
    <p>Records that could not be matched by Woreda and Period:</p>
</div>
""", unsafe_allow_html=True)

if "unmatched_admin_df" in st.session_state and "unmatched_dist_df" in st.session_state:
    c1, c2 = st.columns(2)
    with c1:
        if not st.session_state["unmatched_admin_df"].empty:
            st.markdown("**Administered — Unmatched Records**")
            st.dataframe(st.session_state["unmatched_admin_df"].head(10), use_container_width=True)
            st.caption(f"Showing 10 of {len(st.session_state['unmatched_admin_df'])} unmatched administered records")
        else:
            st.markdown("""
            <div class="stSuccess">
                <b>✅ Perfect Match</b><br>
                All administered records were successfully matched with distribution data.
            </div>
            """, unsafe_allow_html=True)
    with c2:
        if not st.session_state["unmatched_dist_df"].empty:
            st.markdown("**Distributed — Unmatched Records**")
            st.dataframe(st.session_state["unmatched_dist_df"].head(10), use_container_width=True)
            st.caption(f"Showing 10 of {len(st.session_state['unmatched_dist_df'])} unmatched distributed records")
        else:
            st.markdown("""
            <div class="stSuccess">
                <b>✅ Perfect Match</b><br>
                All distributed records were successfully matched with administration data.
            </div>
            """, unsafe_allow_html=True)
else:
    st.info("""
    **ℹ️ Data Processing Required**  
    Upload and process files to see matching summaries and analysis.
    """)
