import streamlit as st
import pandas as pd
import re
import time

st.set_page_config(
    page_title="Immunization Data Triangulation",
    layout="wide",
    page_icon="🩺"
)

# --- Custom CSS for styling ---
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
    color: #333333;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

/* Add padding to main container */
.main .block-container {
    padding-top: 2.5rem !important;
    padding-bottom: 2rem !important;
}

/* Header styling */
.main-header-container {
    background: linear-gradient(90deg, #0077b6 0%, #00b4d8 100%);
    padding: 1.5rem;
    border-radius: 12px;
    margin: 1.5rem 0 2rem 0;
    box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
    border-left: 5px solid #03045e;
    text-align: center;
}
.main-header-container h1 {
    color: white;
    margin: 0;
    font-size: 2rem;
    font-weight: 700;
    text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.2);
}

/* Sidebar */
[data-testid="stSidebar"] {
    color: #000000 !important;
}

/* File uploader */
.stFileUploader > div > div {
    background-color: #ffffff !important;
    border: 2px dashed #cfd8dc !important;
    border-radius: 8px !important;
    padding: 1rem !important;
    color: #212529 !important;
}
.stFileUploader button, .stFileUploader div[role="button"] {
    background: #ffffff !important;
    color: #212529 !important;
    border: 1px solid #ced4da !important;
}
.stFileUploader span, .stFileUploader p, .stFileUploader div {
    color: #212529 !important;
}

/* General buttons */
.stButton > button {
    background: linear-gradient(90deg, #00b4d8 0%, #0077b6 100%);
    color: #ffffff !important;
    border: none;
    padding: 0.7rem 1rem;
    border-radius: 8px;
    font-weight: 600;
    transition: all 0.25s ease;
    width: 100%;
}
.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 10px rgba(0,0,0,0.12);
}

/* Alerts */
.stSuccess, .stInfo, .stError, .stWarning {
    border-radius: 8px;
    padding: 0.85rem 1rem;
    margin: 0.9rem 0;
    font-weight: 600;
    color: #0b0b0b !important;
}
.stSuccess { background: #e9f7ef !important; border-left: 4px solid #28a745 !important; }
.stInfo { background: #e8f4fd !important; border-left: 4px solid #007bff !important; }
.stError { background: #f8d7da !important; border-left: 4px solid #dc3545 !important; }
.stWarning { background: #fff3cd !important; border-left: 4px solid #ffc107 !important; }

/* Metric cards */
.custom-metric-box {
    background: #f9fafb;
    padding: 1rem;
    border-radius: 10px;
    text-align: center;
    box-shadow: 0 3px 6px rgba(0,0,0,0.06);
    border: 1px solid #e6e9ec;
}
.custom-metric-label { color: #05667F; font-weight: 700; margin-bottom: 0.25rem; }
.custom-metric-value { font-size: 1.6rem; color: #034758; font-weight: 700; }

/* Dataframe text */
.dataframe th, .dataframe td { color: #212529 !important; }
</style>
""", unsafe_allow_html=True)

# ----------------- Authentication -----------------
if not st.session_state.get("authenticated", False):
    st.warning("Please log in on the main page to view this dashboard.")
    st.stop()

# ----------------- Sidebar -----------------
with st.sidebar:
    st.markdown("<h3 style='margin-bottom:0.1rem;'>Vaccine Data System</h3>", unsafe_allow_html=True)
    st.markdown("<div style='color:#6c757d; margin-bottom:1rem;'>Ministry of Health</div>", unsafe_allow_html=True)
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
st.markdown('<div class="stInfo">📌 <b>Info:</b> Upload administered and distributed vaccine files (.xlsx or .csv). After clicking <i>Process</i> the progress bar and spinner will show processing progress.</div>', unsafe_allow_html=True)

# ----------------- Upload -----------------
st.subheader("Upload Vaccine Data")
u_col1, u_col2 = st.columns(2)

with u_col1:
    st.markdown('<div class="custom-metric-box">', unsafe_allow_html=True)
    st.markdown('<div class="custom-metric-label">Administered Doses File</div>', unsafe_allow_html=True)
    admin_file = st.file_uploader("Drag & drop or click to browse", type=["xlsx", "csv"], key="admin_upload", label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)

with u_col2:
    st.markdown('<div class="custom-metric-box">', unsafe_allow_html=True)
    st.markdown('<div class="custom-metric-label">Distributed Doses File</div>', unsafe_allow_html=True)
    dist_file = st.file_uploader("Drag & drop or click to browse", type=["xlsx", "csv"], key="dist_upload", label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)

# ----------------- Buttons -----------------
a_col, r_col = st.columns([2, 1])
with a_col:
    process_btn = st.button("📊 Process and Match Data", use_container_width=True)
with r_col:
    reset_btn = st.button("🔄 Reset Data", use_container_width=True)

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
        status_ph.markdown('<div class="stWarning">⚠️ Please upload both Administered and Distributed files.</div>', unsafe_allow_html=True)
    else:
        status_ph.markdown('<div class="stInfo">ℹ️ Data processing started...</div>', unsafe_allow_html=True)
        progress = st.progress(0)
        try:
            # Step 1: read files
            progress.progress(5)
            with st.spinner("Reading files..."):
                admin_df = read_file(admin_file)
                dist_df = read_file(dist_file)
                time.sleep(0.2)
            progress.progress(20)

            # Step 2: clean column names
            with st.spinner("Cleaning column names..."):
                admin_df = clean_column_names(admin_df)
                dist_df = clean_column_names(dist_df)
            progress.progress(35)

            # Step 3: rename columns
            with st.spinner("Identifying key columns..."):
                admin_rename_map, admin_found = find_and_rename_cols(admin_df, "admin")
                dist_rename_map, dist_found = find_and_rename_cols(dist_df, "dist")
            progress.progress(55)

            essential_admin = ['Woreda_Admin', 'Region_Admin', 'Zone_Admin', 'Period_Admin']
            if not all(col in admin_rename_map.values() for col in essential_admin):
                missing = [c for c in essential_admin if c not in admin_rename_map.values()]
                status_ph.markdown(f'<div class="stError">❌ Missing essential Admin columns: {missing}. Please check your file.</div>', unsafe_allow_html=True)
                progress.empty()
                st.stop()

            essential_dist = ['Woreda_Dist', 'Period_Dist']
            if not all(col in dist_rename_map.values() for col in essential_dist):
                missing = [c for c in essential_dist if c not in dist_rename_map.values()]
                status_ph.markdown(f'<div class="stError">❌ Missing essential Distributed columns: {missing}. Please check your file.</div>', unsafe_allow_html=True)
                progress.empty()
                st.stop()

            # Step 4: apply renaming
            admin_df = admin_df.rename(columns=admin_rename_map)
            dist_df = dist_df.rename(columns=dist_rename_map)
            progress.progress(70)

            # Step 5: normalize woreda names
            def normalize_woreda_name(name):
                return re.sub(r'[^a-zA-Z0-9]', '', str(name)).lower()
            admin_df["woreda_normalized"] = admin_df["Woreda_Admin"].apply(normalize_woreda_name)
            dist_df["woreda_normalized"] = dist_df["Woreda_Dist"].apply(normalize_woreda_name)
            progress.progress(80)

            # Step 6: match
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
            progress.progress(95)

            # Save session
            st.session_state["matched_df"] = matched_df
            st.session_state["admin_df"] = admin_df
            st.session_state["dist_df"] = dist_df
            st.session_state["unmatched_admin_df"] = admin_df[~admin_df["woreda_normalized"].isin(matched_df["woreda_normalized"])]
            st.session_state["unmatched_dist_df"] = dist_df[~dist_df["woreda_normalized"].isin(matched_df["woreda_normalized"])]

            progress.progress(100)
            status_ph.markdown('<div class="stSuccess">✅ Data processed successfully! Files are ready for dashboard analysis.</div>', unsafe_allow_html=True)

            # Metrics
            mcol1, mcol2, mcol3 = st.columns(3)
            mcol1.markdown(f'<div class="custom-metric-box"><div class="custom-metric-label">Matched Records</div><div class="custom-metric-value">{len(matched_df)}</div></div>', unsafe_allow_html=True)
            mcol2.markdown(f'<div class="custom-metric-box"><div class="custom-metric-label">Unmatched Admin</div><div class="custom-metric-value">{len(st.session_state["unmatched_admin_df"])}</div></div>', unsafe_allow_html=True)
            mcol3.markdown(f'<div class="custom-metric-box"><div class="custom-metric-label">Unmatched Dist</div><div class="custom-metric-value">{len(st.session_state["unmatched_dist_df"])}</div></div>', unsafe_allow_html=True)

        except Exception as e:
            status_ph.markdown(f'<div class="stError">⚠️ An error occurred during processing: {e}</div>', unsafe_allow_html=True)
            progress.empty()

if reset_btn:
    st.session_state.clear()
    st.success("🔁 Data and session cleared. Please upload new files.")
    st.experimental_rerun()

# ----------------- Summary -----------------
st.markdown("---")
st.markdown("<h3>Summary of Unmatched Data</h3>", unsafe_allow_html=True)

if "unmatched_admin_df" in st.session_state and "unmatched_dist_df" in st.session_state:
    st.write("Records that could not be matched by Woreda+Period:")
    c1, c2 = st.columns(2)
    with c1:
        if not st.session_state["unmatched_admin_df"].empty:
            st.markdown("**Administered — Unmatched**")
            st.dataframe(st.session_state["unmatched_admin_df"].head(10), use_container_width=True)
        else:
            st.info("No unmatched administered records.")
    with c2:
        if not st.session_state["unmatched_dist_df"].empty:
            st.markdown("**Distributed — Unmatched**")
            st.dataframe(st.session_state["unmatched_dist_df"].head(10), use_container_width=True)
        else:
            st.info("No unmatched distributed records.")
else:
    st.info("Upload and process files to see unmatched summaries.")
