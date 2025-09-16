import streamlit as st
import pandas as pd
import re
import io
import time

# ----------------- Page Config -----------------
st.set_page_config(
    page_title="Vaccine Data Processing",
    layout="wide",
    page_icon="⚕️"
)

# ----------------- CSS (contrast fixes + layout) -----------------
st.markdown("""
<style>
/* App base */
.stApp {
    background: #ffffff;
    color: #212529;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

/* Sidebar: force dark text and readable backgrounds */
section[data-testid="stSidebar"] {
    background-color: #f8f9fa !important;
    border-right: 1px solid #dee2e6;
    padding-top: 1rem;
}
section[data-testid="stSidebar"] * {
    color: #212529 !important;
    background: transparent !important;
}

/* Ensure sidebar buttons also look normal */
section[data-testid="stSidebar"] .stButton > button {
    background: #ffffff !important;
    color: #212529 !important;
    border: 1px solid #ced4da !important;
}

/* Header container - moved a bit from top */
.main-header-container {
    background: linear-gradient(90deg, #05667F 0%, #034758 100%);
    padding: 1.2rem;
    border-radius: 12px;
    margin: 1.6rem auto 1rem auto;  /* push down from top */
    box-shadow: 0 6px 12px rgba(0, 0, 0, 0.12);
    border-left: 5px solid #00b4d8;
    text-align: center;
}
.main-header-container h1 {
    color: white;
    margin: 0;
    font-size: 1.8rem;
    font-weight: 700;
    text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.25);
}

/* File uploader: light background, readable button text & filename */
.stFileUploader > div > div {
    background-color: #ffffff !important; /* white inside uploader */
    border: 2px dashed #cfd8dc !important;
    border-radius: 8px !important;
    padding: 1rem !important;
    color: #212529 !important;
}

/* "Browse files" button inside uploader */
.stFileUploader button, .stFileUploader .stButton > button, .stFileUploader div[role="button"] {
    background: #ffffff !important;
    color: #212529 !important;
    border: 1px solid #ced4da !important;
}

/* Filename / attached file text */
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

/* Alerts / status - ensure text is dark and readable */
.stSuccess, .stInfo, .stError, .stWarning {
    border-radius: 8px;
    padding: 0.85rem 1rem;
    margin: 0.9rem 0;
    font-weight: 600;
    color: #0b0b0b !important;  /* force dark text for readability */
}

/* specific backgrounds but with dark text */
.stSuccess {
    background: #e9f7ef !important;
    border-left: 4px solid #28a745 !important;
}
.stInfo {
    background: #e8f4fd !important;
    border-left: 4px solid #007bff !important;
}
.stError {
    background: #f8d7da !important;
    border-left: 4px solid #dc3545 !important;
}
.stWarning {
    background: #fff3cd !important;
    border-left: 4px solid #ffc107 !important;
}

/* Metric card */
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

/* Reduce vertical whitespace slightly */
.block-container { padding-top: 0.6rem; padding-bottom: 1rem; }

/* Dataframe text color */
.dataframe th, .dataframe td { color: #212529 !important; }
</style>
""", unsafe_allow_html=True)

# ----------------- Authentication check -----------------
if not st.session_state.get("authenticated", False):
    st.warning("Please log in on the main page to view this dashboard.")
    st.stop()

# ----------------- Sidebar (kept simple but readable) -----------------
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
col1, col2, col3 = st.columns([1, 4, 1])
with col1:
    try:
        st.image("assets/moh_logo.png", width=84)
    except Exception:
        st.write("")  # ignore if missing
with col2:
    st.markdown('<div class="main-header-container"><h1>Vaccine Data Processing & Matching</h1></div>', unsafe_allow_html=True)
with col3:
    try:
        st.image("assets/eth_flag.png", width=84)
    except Exception:
        st.write("")

st.markdown("---")

# ----------------- Info box (immediately visible) -----------------
st.markdown('<div class="stInfo">📌 <b>Info:</b> Upload administered and distributed vaccine files (.xlsx or .csv). After clicking <i>Process</i> the progress bar and spinner will show processing progress.</div>', unsafe_allow_html=True)

# ----------------- Upload area -----------------
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

# ----------------- Action buttons -----------------
a_col, r_col = st.columns([2, 1])
with a_col:
    process_btn = st.button("📊 Process and Match Data", use_container_width=True)
with r_col:
    reset_btn = st.button("🔄 Reset Data", use_container_width=True)

# placeholder to show status messages and update in-place
status_ph = st.empty()

# ----------------- Processing logic with progress updates -----------------
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
    # immediate validation message (dark text)
    if admin_file is None or dist_file is None:
        status_ph.markdown('<div class="stWarning">⚠️ Please upload both Administered and Distributed files.</div>', unsafe_allow_html=True)
    else:
        status_ph.markdown('<div class="stInfo">ℹ️ Data processing started... </div>', unsafe_allow_html=True)

        progress = st.progress(0)
        # start processing steps and update progress for user feedback
        try:
            # Step 1 - read files
            progress.progress(5)
            with st.spinner("Reading files..."):
                admin_df = read_file(admin_file)
                dist_df = read_file(dist_file)
                time.sleep(0.2)  # small pause to show spinner
            progress.progress(20)

            # Step 2 - clean column names
            with st.spinner("Cleaning column names..."):
                admin_df = clean_column_names(admin_df)
                dist_df = clean_column_names(dist_df)
                time.sleep(0.15)
            progress.progress(35)

            # Step 3 - identify and rename columns
            with st.spinner("Identifying key columns..."):
                admin_rename_map, admin_found = find_and_rename_cols(admin_df, "admin")
                dist_rename_map, dist_found = find_and_rename_cols(dist_df, "dist")
                time.sleep(0.15)
            progress.progress(55)

            # Check essential columns
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

            # Step 4 - apply renaming
            with st.spinner("Normalizing and renaming..."):
                admin_df = admin_df.rename(columns=admin_rename_map)
                dist_df = dist_df.rename(columns=dist_rename_map)
                time.sleep(0.15)
            progress.progress(70)

            # Step 5 - normalize woreda names for matching
            def normalize_woreda_name(name):
                return re.sub(r'[^a-zA-Z0-9]', '', str(name)).lower()

            admin_df["woreda_normalized"] = admin_df["Woreda_Admin"].apply(normalize_woreda_name)
            dist_df["woreda_normalized"] = dist_df["Woreda_Dist"].apply(normalize_woreda_name)
            progress.progress(80)

            # Step 6 - match on woreda_normalized + period
            with st.spinner("Matching records..."):
                matched_df = pd.merge(
                    admin_df,
                    dist_df,
                    left_on=["woreda_normalized", "Period_Admin"],
                    right_on=["woreda_normalized", "Period_Dist"],
                    how="inner",
                )
                # Clean up
                if "Period_Dist" in matched_df:
                    matched_df = matched_df.drop(columns="Period_Dist")
                matched_df.rename(columns={"Period_Admin": "Period"}, inplace=True)
                time.sleep(0.1)
            progress.progress(95)

            # Store results in session_state
            st.session_state["matched_df"] = matched_df
            st.session_state["admin_df"] = admin_df
            st.session_state["dist_df"] = dist_df

            unmatched_admin_df = admin_df[~admin_df["woreda_normalized"].isin(matched_df["woreda_normalized"])]
            unmatched_dist_df = dist_df[~dist_df["woreda_normalized"].isin(matched_df["woreda_normalized"])]

            st.session_state["unmatched_admin_df"] = unmatched_admin_df
            st.session_state["unmatched_dist_df"] = unmatched_dist_df

            # Finalize progress and show success (replace earlier status)
            progress.progress(100)
            status_ph.markdown('<div class="stSuccess">✅ Data processed successfully! Files are ready for dashboard analysis.</div>', unsafe_allow_html=True)

            # display quick metrics
            mcol1, mcol2, mcol3 = st.columns(3)
            with mcol1:
                st.markdown('<div class="custom-metric-box"><div class="custom-metric-label">Matched Records</div><div class="custom-metric-value">{}</div></div>'.format(len(matched_df)), unsafe_allow_html=True)
            with mcol2:
                st.markdown('<div class="custom-metric-box"><div class="custom-metric-label">Unmatched Admin</div><div class="custom-metric-value">{}</div></div>'.format(len(unmatched_admin_df)), unsafe_allow_html=True)
            with mcol3:
                st.markdown('<div class="custom-metric-box"><div class="custom-metric-label">Unmatched Dist</div><div class="custom-metric-value">{}</div></div>'.format(len(unmatched_dist_df)), unsafe_allow_html=True)

        except Exception as e:
            status_ph.markdown(f'<div class="stError">⚠️ An error occurred during processing: {e}</div>', unsafe_allow_html=True)
            progress.empty()

if reset_btn:
    st.session_state.clear()
    st.success("🔁 Data and session cleared. Please upload new files.")
    st.experimental_rerun()

# ----------------- Summary / unmatched preview (if available) -----------------
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
    st.info("Upload and process files to see unmatched-summaries.")
