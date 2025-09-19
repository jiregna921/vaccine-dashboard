# immunization_dashboard_fixed.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from config.thresholds import VACCINE_THRESHOLDS  # optional; code will handle if values differ
from pptx import Presentation
from io import BytesIO

# ========= Page config (must be first Streamlit call) =========
st.set_page_config(
    page_title="Vaccine Utilization Analytics Dashboard",
    layout="wide",
    page_icon="💉",
)

# --- Custom CSS for improved styling + special unmatched-info box ---
st.markdown(
    """
<style>
/* (your original large CSS omitted here for brevity in message) */
/* keep full CSS you had originally, plus this small addition for unmatched-info */
.unmatched-info {
    background: white !important;
    color: #000000 !important;
    border: 1px solid #e9ecef;
    padding: 0.75rem;
    border-radius: 8px;
    font-weight: 500;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    margin-bottom: 0.5rem;
}
.plotly .modebar { background: rgba(255,255,255,0.95) !important; border: 1px solid #e9ecef !important; }
</style>
""",
    unsafe_allow_html=True,
)

# --- Helper functions ------------------------------------------------
def to_excel(df: pd.DataFrame) -> bytes:
    out = BytesIO()
    with pd.ExcelWriter(out, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Sheet1")
    return out.getvalue()


def _normalize_thresholds_to_pct(src: dict) -> dict:
    """
    Convert a thresholds dict (either decimals like 1.2/0.3 or percentages 120/30)
    into a consistent mapping where values are percentages (e.g., 120, 30).
    Expected input shape: { 'BCG': {'high': 1.2, 'low': 0.3}, ... } OR
                             { 'BCG': {'high': 120, 'low': 30}, ... }
    """
    normalized = {}
    for vac, thr in src.items():
        high = thr.get("high")
        low = thr.get("low")
        if high is None or low is None:
            continue
        # If value looks like fraction (<= 2.0), convert to percent
        if float(high) <= 2.0:
            high_pct = float(high) * 100.0
        else:
            high_pct = float(high)
        if float(low) <= 2.0:
            low_pct = float(low) * 100.0
        else:
            low_pct = float(low)
        normalized[vac] = {"high": high_pct, "low": low_pct}
    return normalized


# Default thresholds (percent) if config not present or incomplete
DEFAULT_THRESHOLDS = {
    "BCG": {"high": 120.0, "low": 30.0},
    "IPV": {"high": 130.0, "low": 75.0},
    "Measles": {"high": 125.0, "low": 50.0},
    "Penta": {"high": 130.0, "low": 80.0},
    "Rota": {"high": 130.0, "low": 75.0},
}

# Merge VACCINE_THRESHOLDS (if provided) with defaults and normalize
try:
    user_thr = VACCINE_THRESHOLDS if isinstance(VACCINE_THRESHOLDS, dict) else {}
except Exception:
    user_thr = {}
THRESHOLDS = DEFAULT_THRESHOLDS.copy()
THRESHOLDS.update(_normalize_thresholds_to_pct(user_thr))

# Count extremes: comparisons use percentage values directly
def count_extremity(df: pd.DataFrame, vaccine: str):
    rate_col = f"{vaccine}_Utilization_Rate"
    if rate_col not in df.columns:
        return None
    thr = THRESHOLDS.get(vaccine, None)
    if not thr:
        return None
    high_count = int((df[rate_col] > thr["high"]).sum())
    low_count = int((df[rate_col] < thr["low"]).sum())
    return high_count, low_count


# --------- Header ----------
st.markdown(
    """
<div class="main-header-container">
    <h1>📊 Vaccine Discrepancies and Utilization Analysis</h1>
    <p>Comprehensive Vaccine Performance Monitoring</p>
</div>
""",
    unsafe_allow_html=True,
)

# --------- Authentication guard (keeps your original behavior) ----------
if not st.session_state.get("authenticated", False):
    st.warning("Please log in on the main page to view this dashboard.")
    st.stop()

# --------- Main dashboard logic ----------
if st.session_state.get("matched_df") is None:
    st.info("Please upload and process data on the Data Upload page to view this dashboard.")
    st.stop()

# use the stored dataframe
df_all: pd.DataFrame = st.session_state["matched_df"].copy()

# verify required columns (names remain the same as your original code)
required_cols = ["Region_Admin", "Zone_Admin", "Woreda_Admin", "Period"]
if not all(col in df_all.columns for col in required_cols):
    st.error("Essential columns (Region_Admin, Zone_Admin, Woreda_Admin, Period) are missing from the processed data.")
    st.stop()

# vaccines list
vaccines = ["BCG", "IPV", "Measles", "Penta", "Rota"]

# compute utilization rates (percentage). We keep original clipping behavior.
for vaccine in vaccines:
    admin_col = f"{vaccine}_Administered"
    dist_col = f"{vaccine}_Distributed"
    rate_col = f"{vaccine}_Utilization_Rate"
    if admin_col in df_all.columns and dist_col in df_all.columns:
        # avoid division by zero: replace distributed 0 with NaN then fill after calculation
        df_all[rate_col] = (df_all[admin_col] / df_all[dist_col].replace({0: pd.NA})) * 100
        df_all[rate_col] = df_all[rate_col].fillna(0)  # if distributed was 0 set rate 0
        df_all[rate_col] = df_all[rate_col].clip(lower=0, upper=1000)  # keep your original clip

# ---------- Sidebar filters ----------
st.sidebar.markdown('<div class="filter-section">', unsafe_allow_html=True)
st.sidebar.header("🧪 Filter Data")

regions = sorted(df_all["Region_Admin"].dropna().unique().tolist())
selected_region = st.sidebar.selectbox("Select Region", ["All"] + regions)

# zones chained
if selected_region != "All":
    zone_candidates = sorted(df_all[df_all["Region_Admin"] == selected_region]["Zone_Admin"].dropna().unique().tolist())
else:
    zone_candidates = sorted(df_all["Zone_Admin"].dropna().unique().tolist())
selected_zone = st.sidebar.selectbox("Select Zone", ["All"] + zone_candidates)

# woredas chained
if selected_zone != "All":
    woredas_candidates = sorted(
        df_all[(df_all["Region_Admin"] == selected_region) & (df_all["Zone_Admin"] == selected_zone)]["Woreda_Admin"].dropna().unique().tolist()
    )
elif selected_region != "All":
    woredas_candidates = sorted(df_all[df_all["Region_Admin"] == selected_region]["Woreda_Admin"].dropna().unique().tolist())
else:
    woredas_candidates = sorted(df_all["Woreda_Admin"].dropna().unique().tolist())
selected_woreda = st.sidebar.selectbox("Select Woreda", ["All"] + woredas_candidates)

# Period filter
periods = sorted(df_all["Period"].dropna().unique().tolist())
selected_period = st.sidebar.selectbox("Select Period", ["All"] + periods)

# Vaccine filter
selected_vaccine = st.sidebar.selectbox("Select Vaccine", ["All"] + vaccines)
st.sidebar.markdown('</div>', unsafe_allow_html=True)

# apply filters
filtered_df = df_all.copy()
if selected_region != "All":
    filtered_df = filtered_df[filtered_df["Region_Admin"] == selected_region]
if selected_zone != "All":
    filtered_df = filtered_df[filtered_df["Zone_Admin"] == selected_zone]
if selected_woreda != "All":
    filtered_df = filtered_df[filtered_df["Woreda_Admin"] == selected_woreda]
if selected_period != "All":
    filtered_df = filtered_df[filtered_df["Period"] == selected_period]

if filtered_df.empty:
    st.warning("⚠️ No data found for the selected filters.")
    st.stop()

# ---------- Scorecards ----------
total_woredas = int(filtered_df["Woreda_Admin"].nunique())

dist_cols = [f"{v}_Distributed" for v in vaccines]
admin_cols = [f"{v}_Administered" for v in vaccines]

if selected_vaccine != "All":
    dist_col = f"{selected_vaccine}_Distributed"
    admin_col = f"{selected_vaccine}_Administered"
    if dist_col in filtered_df.columns and admin_col in filtered_df.columns:
        total_admin = int(filtered_df[admin_col].sum())
        total_dist = int(filtered_df[dist_col].sum())
    else:
        st.warning(f"Data for '{selected_vaccine}' is not available in the processed files.")
        st.stop()
else:
    existing_dist_cols = [c for c in dist_cols if c in filtered_df.columns]
    existing_admin_cols = [c for c in admin_cols if c in filtered_df.columns]
    total_dist = int(filtered_df[existing_dist_cols].sum().sum()) if existing_dist_cols else 0
    total_admin = int(filtered_df[existing_admin_cols].sum().sum()) if existing_admin_cols else 0

utilization_rate = (total_admin / total_dist) * 100 if total_dist > 0 else 0.0

st.markdown("---")
st.markdown('<div class="section-header"><h3>📊 Performance Overview</h3></div>', unsafe_allow_html=True)
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f'<div class="custom-metric-box"><div class="custom-metric-label">Total Woredas</div><div class="custom-metric-value">{total_woredas}</div></div>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div class="custom-metric-box"><div class="custom-metric-label">Total Doses Distributed</div><div class="custom-metric-value">{total_dist:,.0f}</div></div>', unsafe_allow_html=True)
with col3:
    st.markdown(f'<div class="custom-metric-box"><div class="custom-metric-label">Total Doses Administered</div><div class="custom-metric-value">{total_admin:,.0f}</div></div>', unsafe_allow_html=True)
with col4:
    st.markdown(f'<div class="custom-metric-box"><div class="custom-metric-label">Utilization Rate</div><div class="custom-metric-value">{utilization_rate:.2f}%</div></div>', unsafe_allow_html=True)
st.markdown("---")

# ---------- Extremities Count ----------
st.markdown('<div class="section-header"><h3>🚨 Extreme Utilization Rates</h3></div>', unsafe_allow_html=True)
counts_cols = st.columns(len(vaccines))
for i, vaccine in enumerate(vaccines):
    counts = count_extremity(filtered_df, vaccine)
    if counts:
        with counts_cols[i]:
            st.markdown(f'<div class="custom-metric-box"><div class="custom-metric-label">{vaccine}</div><div class="custom-metric-value">{counts[0]}↑ | {counts[1]}↓</div></div>', unsafe_allow_html=True)
st.markdown("---")

# ---------- Extreme utilization summary table ----------
st.markdown('<div class="section-header"><h3>📋 Extreme Utilization by Region and Zone</h3></div>', unsafe_allow_html=True)
if selected_vaccine == "All":
    # for convenience show aggregated counts across vaccines by region/zone (optional)
    st.info("Select a specific vaccine in the sidebar to see region/zone breakdown.")
else:
    rate_col = f"{selected_vaccine}_Utilization_Rate"
    if rate_col not in filtered_df.columns:
        st.warning(f"Utilization data for {selected_vaccine} is not available in the processed files.")
    else:
        thr = THRESHOLDS.get(selected_vaccine, DEFAULT_THRESHOLDS[selected_vaccine])
        extreme_df = filtered_df.copy()
        # group by Region or Region+Zone
        group_cols = ["Region_Admin"] if selected_region == "All" else ["Region_Admin", "Zone_Admin"]
        extreme_df["High_Extremity"] = extreme_df[rate_col] > thr["high"]
        extreme_df["Low_Extremity"] = extreme_df[rate_col] < thr["low"]
        extreme_summary = (
            extreme_df.groupby(group_cols)
            .agg(total_woredas=("Woreda_Admin", "nunique"),
                 high_extremity_count=("High_Extremity", "sum"),
                 low_extremity_count=("Low_Extremity", "sum"))
            .reset_index()
        )
        # rename for neat display
        rename_map = {"Region_Admin": "Region", "Zone_Admin": "Zone"}
        extreme_summary.rename(columns=rename_map, inplace=True)
        st.dataframe(extreme_summary, use_container_width=True, hide_index=True)
        st.download_button(
            label="📥 Download Data as Excel",
            data=to_excel(extreme_summary),
            file_name=f"Extreme_Utilization_Data_{selected_vaccine}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )

st.markdown("---")

# ---------- Utilization Rate by Woreda (improved contrast) ----------
st.markdown('<div class="section-header"><h3>📈 Utilization Rate by Woreda</h3></div>', unsafe_allow_html=True)

if selected_vaccine == "All":
    st.info("Please select a specific vaccine to view utilization rate plots.")
else:
    rate_col = f"{selected_vaccine}_Utilization_Rate"
    if rate_col not in filtered_df.columns:
        st.warning(f"Utilization data for {selected_vaccine} is not available in the processed files.")
    else:
        fig = px.scatter(
            filtered_df,
            x="Woreda_Admin",
            y=rate_col,
            title=f"{selected_vaccine} Utilization Rate by Woreda",
            labels={"Woreda_Admin": "Woreda", rate_col: "Utilization Rate (%)"},
        )
        # improved contrast/background
        fig.update_traces(marker=dict(size=9, opacity=0.85))
        fig.update_layout(
            plot_bgcolor="#ffffff",
            paper_bgcolor="#f6f8fa",
            font=dict(color="#0b2545", size=12),
            title_font=dict(size=16, color="#0b2545"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            hoverlabel=dict(bgcolor="white", font_size=11, font_family="Arial", font_color="#0b2545"),
            margin=dict(t=60, b=120),
        )
        # threshold horizontal lines in percent
        thr_pct = THRESHOLDS.get(selected_vaccine, DEFAULT_THRESHOLDS[selected_vaccine])
        fig.add_hline(y=thr_pct["high"], line_dash="dash", line_color="red", annotation_text="High Threshold", annotation_position="top right")
        fig.add_hline(y=thr_pct["low"], line_dash="dash", line_color="orange", annotation_text="Low Threshold", annotation_position="bottom right")

        fig.update_xaxes(tickangle=45, tickfont=dict(size=9, color="#0b2545"))
        fig.update_yaxes(tickfont=dict(size=10, color="#0b2545"))
        st.plotly_chart(fig, use_container_width=True)

# ---------- Unmatched Records ----------
st.markdown('<div class="section-header"><h3>🔍 Unmatched Records</h3></div>', unsafe_allow_html=True)
unmatched_col1, unmatched_col2 = st.columns(2)

with unmatched_col1:
    st.markdown('<div class="unmatched-section">', unsafe_allow_html=True)
    if "unmatched_admin_df" in st.session_state and isinstance(st.session_state["unmatched_admin_df"], pd.DataFrame) and not st.session_state["unmatched_admin_df"].empty:
        st.write("**Unmatched Administered Records**")
        st.dataframe(st.session_state["unmatched_admin_df"], use_container_width=True)
        st.download_button("Download Unmatched Administered", to_excel(st.session_state["unmatched_admin_df"]), "unmatched_admin.xlsx", use_container_width=True)
    else:
        # use white background + black text box for visibility (per your request)
        st.markdown('<div class="unmatched-info">No unmatched administered records found.</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with unmatched_col2:
    st.markdown('<div class="unmatched-section">', unsafe_allow_html=True)
    if "unmatched_dist_df" in st.session_state and isinstance(st.session_state["unmatched_dist_df"], pd.DataFrame) and not st.session_state["unmatched_dist_df"].empty:
        st.write("**Unmatched Distributed Records**")
        st.dataframe(st.session_state["unmatched_dist_df"], use_container_width=True)
        st.download_button("Download Unmatched Distributed", to_excel(st.session_state["unmatched_dist_df"]), "unmatched_dist.xlsx", use_container_width=True)
    else:
        st.markdown('<div class="unmatched-info">No unmatched distributed records found.</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")

# ---------- PPTX report ----------
def create_ppt(filtered_df: pd.DataFrame, selected_vaccine: str):
    prs = Presentation()
    # Title slide
    title_slide_layout = prs.slide_layouts[0]
    slide = prs.slides.add_slide(title_slide_layout)
    slide.shapes.title.text = "Immunization Triangulation Report"
    slide.placeholders[1].text = f"Report generated for {selected_vaccine}."

    # Recommendation slides (kept your content)
    recs = {
        "High Utilization": [
            "Conduct a targeted audit of administered dose records for potential data entry errors.",
            "Investigate potential lags in reporting of distributed doses.",
            "Recommend a physical stock count at facilities to reconcile administered and distributed doses.",
        ],
        "Low Utilization": [
            "Assess inventory levels to prevent vaccine expiration due to overstocking.",
            "Investigate if there are service delivery issues affecting vaccine demand.",
            "Verify that administered doses are being reported accurately and on time.",
        ],
        "High Discrepancies": [
            "Provide training on accurate reporting for both administered and distributed doses.",
            "Implement a process to regularly cross-reference data to catch discrepancies early.",
            "Establish a feedback loop where Woredas are alerted to discrepancies.",
        ],
    }
    for title, bullets in recs.items():
        s = prs.slides.add_slide(prs.slide_layouts[1])
        s.shapes.title.text = f"Recommendations for {title}"
        tf = s.placeholders[1].text_frame
        for b in bullets:
            p = tf.add_paragraph()
            p.text = b
            p.level = 0

    buf = BytesIO()
    prs.save(buf)
    buf.seek(0)
    return buf

ppt_buffer = create_ppt(filtered_df, selected_vaccine)
st.download_button(
    label="📊 Download Report as PPT",
    data=ppt_buffer,
    file_name="immunization_report.pptx",
    mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
    use_container_width=True,
)
