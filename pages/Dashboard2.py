# immunization_dashboard.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from config.thresholds import VACCINE_THRESHOLDS
from pptx import Presentation
from io import BytesIO

# ---------------------------------------------------------------------
# Page configuration  (Must be before other Streamlit calls that affect layout)
# ---------------------------------------------------------------------
st.set_page_config(
    page_title="Vaccine Utilization Analytics Dashboard",
    layout="wide",
    page_icon="💉"
)

# ---------------------------------------------------------------------
# CSS - keep original styles but enforce white background + black text
# ---------------------------------------------------------------------
st.markdown(
    """
    <style>
    /* Force main background and sidebar white and text black */
    body, .stApp, .block-container, .stSidebar, .css-1d391kg {
        background: #ffffff !important;
        color: #000000 !important;
    }

    /* Keep original card and header styling but adjust text colors where necessary */
    .main-header-container {
        background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.12);
        text-align: center;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    .main-header-container h1 { color: white; margin: 0; font-size: 1.8rem; font-weight: 700; }
    .main-header-container p { color: #bdc3c7; margin: 0.5rem 0 0 0; font-size: 1rem; }

    .custom-metric-box {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        padding: 1rem;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 1rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        border: 1px solid rgba(52, 152, 219, 0.1);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
        height: 120px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .custom-metric-label { font-size: 0.75rem; font-weight: 600; color: #7f8c8d; text-transform: uppercase; }
    .custom-metric-value { font-size: 1.5rem; font-weight: 700; color: #000000; }

    /* Make plotly containers and hover text visible on white bg */
    .js-plotly-plot { border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); background: white; padding: 1rem; border: 1px solid rgba(52,152,219,0.06); }
    .plotly .hovertext { background: #ffffff !important; color: #000000 !important; border: 1px solid #e9ecef !important; }

    /* Dataframe styling adjustments */
    .dataframe { background: white !important; color: black !important; }

    /* Unmatched message box (white bg, black text) */
    .unmatched-info { background: white !important; color: black !important; border: 1px solid #e9ecef; padding: 0.75rem; border-radius: 8px; }

    /* Keep other original classes for compatibility, but ensure text is black where they overlap */
    .stInfo, .stWarning, .stSuccess { color: #000000 !important; }
    .stSidebar * { color: #000000 !important; }

    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------
# Helper functions (modularized - keep original logic)
# ---------------------------------------------------------------------
def to_excel(df: pd.DataFrame) -> bytes:
    out = BytesIO()
    with pd.ExcelWriter(out, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Sheet1")
    return out.getvalue()


def compute_utilization_rates(df: pd.DataFrame, vaccines):
    """
    Compute utilization rates as percentage (administered / distributed * 100).
    Clip to [0, 1000] like original code.
    """
    df = df.copy()
    for vaccine in vaccines:
        admin_col = f"{vaccine}_Administered"
        dist_col = f"{vaccine}_Distributed"
        rate_col = f"{vaccine}_Utilization_Rate"
        if admin_col in df.columns and dist_col in df.columns:
            df[rate_col] = df[admin_col] / df[dist_col].replace(0, 1) * 100
            df[rate_col] = df[rate_col].clip(0, 1000)
    return df


def count_extremity(df: pd.DataFrame, vaccine: str):
    """
    Counts extremities using the original thresholds format (decimals) and the original comparison (rate/100).
    Returns (high_count, low_count) or None if not available.
    """
    rate_col = f"{vaccine}_Utilization_Rate"
    if rate_col not in df.columns:
        return None

    thresholds = {
        "BCG": {"high": 1.20, "low": 0.30},
        "IPV": {"high": 1.30, "low": 0.75},
        "Measles": {"high": 1.25, "low": 0.50},
        "Penta": {"high": 1.30, "low": 0.80},
        "Rota": {"high": 1.30, "low": 0.75},
    }

    if vaccine not in thresholds:
        return None

    high_count = len(df[df[rate_col] / 100 > thresholds[vaccine]["high"]])
    low_count = len(df[df[rate_col] / 100 < thresholds[vaccine]["low"]])
    return high_count, low_count


def render_sidebar_filters(df_all: pd.DataFrame, vaccines):
    """Render sidebar and return selected filters."""
    st.sidebar.markdown('<div class="filter-section">', unsafe_allow_html=True)
    st.sidebar.header("🧪 Filter Data")

    regions = sorted(df_all["Region_Admin"].dropna().unique().tolist())
    selected_region = st.sidebar.selectbox("Select Region", ["All"] + regions)

    filtered_zones = (
        df_all[df_all["Region_Admin"] == selected_region]["Zone_Admin"].unique()
        if selected_region != "All"
        else df_all["Zone_Admin"].unique()
    )
    zones = sorted([z for z in filtered_zones if pd.notna(z)])
    selected_zone = st.sidebar.selectbox("Select Zone", ["All"] + zones)

    if selected_zone != "All":
        filtered_woredas = df_all[(df_all["Region_Admin"] == selected_region) & (df_all["Zone_Admin"] == selected_zone)]["Woreda_Admin"].unique()
    elif selected_region != "All":
        filtered_woredas = df_all[df_all["Region_Admin"] == selected_region]["Woreda_Admin"].unique()
    else:
        filtered_woredas = df_all["Woreda_Admin"].unique()
    woredas = sorted([w for w in filtered_woredas if pd.notna(w)])
    selected_woreda = st.sidebar.selectbox("Select Woreda", ["All"] + woredas)

    periods = sorted(df_all["Period"].dropna().unique().tolist())
    selected_period = st.sidebar.selectbox("Select Period", ["All"] + periods)

    selected_vaccine = st.sidebar.selectbox("Select Vaccine", ["All"] + vaccines)
    st.sidebar.markdown('</div>', unsafe_allow_html=True)

    return selected_region, selected_zone, selected_woreda, selected_period, selected_vaccine


def apply_filters(df: pd.DataFrame, selected_region, selected_zone, selected_woreda, selected_period):
    """Filter dataframe according to selected filters (preserve original logic)."""
    df_filtered = df.copy()
    if selected_region != "All":
        df_filtered = df_filtered[df_filtered["Region_Admin"] == selected_region]
    if selected_zone != "All":
        df_filtered = df_filtered[df_filtered["Zone_Admin"] == selected_zone]
    if selected_woreda != "All":
        df_filtered = df_filtered[df_filtered["Woreda_Admin"] == selected_woreda]
    if selected_period != "All":
        df_filtered = df_filtered[df_filtered["Period"] == selected_period]
    return df_filtered


def render_scorecards(filtered_df: pd.DataFrame, vaccines, selected_vaccine):
    """Render the 4 KPIs (Total Woredas, Total Doses Distributed/Administered, Utilization Rate)."""
    total_woredas = filtered_df["Woreda_Admin"].nunique()

    dist_cols = [f"{v}_Distributed" for v in vaccines]
    admin_cols = [f"{v}_Administered" for v in vaccines]

    if selected_vaccine != "All":
        dist_col = f"{selected_vaccine}_Distributed"
        admin_col = f"{selected_vaccine}_Administered"
        if dist_col in filtered_df.columns and admin_col in filtered_df.columns:
            total_admin = filtered_df[admin_col].sum()
            total_dist = filtered_df[dist_col].sum()
        else:
            st.warning(f"Data for '{selected_vaccine}' is not available in the processed files.")
            st.stop()
    else:
        existing_dist_cols = [col for col in dist_cols if col in filtered_df.columns]
        existing_admin_cols = [col for col in admin_cols if col in filtered_df.columns]

        total_dist = filtered_df[existing_dist_cols].sum().sum() if existing_dist_cols else 0
        total_admin = filtered_df[existing_admin_cols].sum().sum() if existing_admin_cols else 0

    utilization_rate = (total_admin / total_dist) * 100 if total_dist > 0 else 0

    st.markdown("---")
    st.markdown('<div class="section-header"><h3>📊 Performance Overview</h3></div>', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f'<div class="custom-metric-box"><div class="custom-metric-label">Total Woredas</div><div class="custom-metric-value">{total_woredas}</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="custom-metric-box"><div class="custom-metric-label">Total Doses Distributed</div><div class="custom-metric-value">{int(total_dist):,}</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="custom-metric-box"><div class="custom-metric-label">Total Doses Administered</div><div class="custom-metric-value">{int(total_admin):,}</div></div>', unsafe_allow_html=True)
    with col4:
        st.markdown(f'<div class="custom-metric-box"><div class="custom-metric-label">Utilization Rate</div><div class="custom-metric-value">{utilization_rate:.2f}%</div></div>', unsafe_allow_html=True)
    st.markdown("---")


def render_extremities_counts(filtered_df: pd.DataFrame, vaccines):
    st.markdown('<div class="section-header"><h3>🚨 Extreme Utilization Rates</h3></div>', unsafe_allow_html=True)
    counts_cols = st.columns(len(vaccines))
    for i, vaccine in enumerate(vaccines):
        counts = count_extremity(filtered_df, vaccine)
        if counts:
            with counts_cols[i]:
                st.markdown(f'<div class="custom-metric-box"><div class="custom-metric-label">{vaccine}</div><div class="custom-metric-value">{counts[0]}↑ | {counts[1]}↓</div></div>', unsafe_allow_html=True)
    st.markdown("---")


def render_extremes_table(filtered_df: pd.DataFrame, selected_vaccine, selected_region):
    st.markdown('<div class="section-header"><h3>📋 Extreme Utilization by Region and Zone</h3></div>', unsafe_allow_html=True)
    if selected_vaccine == "All":
        st.info("Please select a specific vaccine to view this table.")
        return

    rate_col = f"{selected_vaccine}_Utilization_Rate"
    if rate_col not in filtered_df.columns:
        st.warning(f"Utilization data for {selected_vaccine} is not available in the processed files.")
        return

    thresholds = {
        "BCG": {"high": 1.20, "low": 0.30},
        "IPV": {"high": 1.30, "low": 0.75},
        "Measles": {"high": 1.25, "low": 0.50},
        "Penta": {"high": 1.30, "low": 0.80},
        "Rota": {"high": 1.30, "low": 0.75},
    }

    extreme_df = filtered_df.copy()
    if selected_region == "All":
        group_cols = ["Region_Admin"]
    else:
        group_cols = ["Region_Admin", "Zone_Admin"]

    extreme_df["High_Extremity"] = extreme_df[rate_col] / 100 > thresholds[selected_vaccine]["high"]
    extreme_df["Low_Extremity"] = extreme_df[rate_col] / 100 < thresholds[selected_vaccine]["low"]

    extreme_summary = extreme_df.groupby(group_cols).agg(
        total_woredas=("Woreda_Admin", "nunique"),
        high_extremity_count=("High_Extremity", "sum"),
        low_extremity_count=("Low_Extremity", "sum")
    ).reset_index()

    # Rename for display
    rename_map = {"Region_Admin": "Region", "Zone_Admin": "Zone"}
    extreme_summary.rename(columns=rename_map, inplace=True)

    st.dataframe(extreme_summary, use_container_width=True, hide_index=True)
    st.download_button(
        label="📥 Download Data as Excel",
        data=to_excel(extreme_summary),
        file_name=f"Extreme_Utilization_Data_{selected_vaccine}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )
    st.markdown("---")


def render_utilization_scatter(filtered_df: pd.DataFrame, selected_vaccine):
    st.markdown('<div class="section-header"><h3>📈 Utilization Rate by Woreda</h3></div>', unsafe_allow_html=True)
    if selected_vaccine == "All":
        st.info("Please select a specific vaccine to view utilization rate plots.")
        return

    rate_col = f"{selected_vaccine}_Utilization_Rate"
    if rate_col not in filtered_df.columns:
        st.warning(f"Utilization data for {selected_vaccine} is not available in the processed files.")
        return

    fig = px.scatter(
        filtered_df,
        x="Woreda_Admin",
        y=rate_col,
        title=f"{selected_vaccine} Utilization Rate by Woreda",
        labels={"Woreda_Admin": "Woreda", rate_col: "Utilization Rate (%)"},
        color_discrete_sequence=["#3498db"]
    )

    thresholds = {
        "BCG": {"high": 120, "low": 30},
        "IPV": {"high": 130, "low": 75},
        "Measles": {"high": 125, "low": 50},
        "Penta": {"high": 130, "low": 80},
        "Rota": {"high": 130, "low": 75},
    }

    if selected_vaccine in thresholds:
        fig.add_hline(y=thresholds[selected_vaccine]["high"], line_dash="dash", line_color="red",
                      annotation_text="High Threshold", annotation_position="bottom right")
        fig.add_hline(y=thresholds[selected_vaccine]["low"], line_dash="dash", line_color="orange",
                      annotation_text="Low Threshold", annotation_position="top right")

    # Improved contrast/background for charts (white bg, black text)
    fig.update_layout(
        xaxis_title="Woreda",
        yaxis_title="Utilization Rate (%)",
        xaxis_tickangle=45,
        plot_bgcolor='#ffffff',
        paper_bgcolor='#ffffff',
        font=dict(color='#000000', size=12),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=11, color='#000000'),
            bgcolor='rgba(255,255,255,0.9)',
            bordercolor='#e9ecef',
            borderwidth=1
        ),
        hoverlabel=dict(
            bgcolor="white",
            font_size=11,
            font_family="Arial",
            font_color="#000000",
            bordercolor="#e9ecef"
        )
    )

    fig.update_xaxes(tickfont=dict(size=9, color='#000000'), showgrid=False)
    fig.update_yaxes(tickfont=dict(color='#000000'), showgrid=False)

    st.plotly_chart(fig, use_container_width=True)


def render_unmatched_sections():
    st.markdown('<div class="section-header"><h3>🔍 Unmatched Records</h3></div>', unsafe_allow_html=True)
    unmatched_col1, unmatched_col2 = st.columns(2)

    with unmatched_col1:
        st.markdown('<div class="unmatched-section">', unsafe_allow_html=True)
        if "unmatched_admin_df" in st.session_state and not st.session_state["unmatched_admin_df"].empty:
            st.write("**Unmatched Administered Records**")
            st.dataframe(st.session_state["unmatched_admin_df"], use_container_width=True)
            st.download_button("Download Unmatched Administered", to_excel(st.session_state["unmatched_admin_df"]), "unmatched_admin.xlsx", use_container_width=True)
        else:
            # white box + black text for visibility
            st.markdown('<div class="unmatched-info">No unmatched administered records found.</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with unmatched_col2:
        st.markdown('<div class="unmatched-section">', unsafe_allow_html=True)
        if "unmatched_dist_df" in st.session_state and not st.session_state["unmatched_dist_df"].empty:
            st.write("**Unmatched Distributed Records**")
            st.dataframe(st.session_state["unmatched_dist_df"], use_container_width=True)
            st.download_button("Download Unmatched Distributed", to_excel(st.session_state["unmatched_dist_df"]), "unmatched_dist.xlsx", use_container_width=True)
        else:
            st.markdown('<div class="unmatched-info">No unmatched distributed records found.</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("---")


def create_ppt(filtered_df: pd.DataFrame, selected_vaccine: str) -> BytesIO:
    prs = Presentation()
    # Slide 1: Title
    title_slide_layout = prs.slide_layouts[0]
    slide = prs.slides.add_slide(title_slide_layout)
    slide.shapes.title.text = "Immunization Triangulation Report"
    slide.placeholders[1].text = f"Report generated for {selected_vaccine}."

    # Recommendations slides (same text as original)
    rec_high = [
        "Conduct a targeted audit of administered dose records for potential data entry errors.",
        "Investigate potential lags in reporting of distributed doses.",
        "Recommend a physical stock count at facilities to reconcile administered and distributed doses.",
    ]
    rec_low = [
        "Assess inventory levels to prevent vaccine expiration due to overstocking.",
        "Investigate if there are service delivery issues affecting vaccine demand.",
        "Verify that administered doses are being reported accurately and on time.",
    ]
    rec_disc = [
        "Provide training on accurate reporting for both administered and distributed doses.",
        "Implement a process to regularly cross-reference data to catch discrepancies early.",
        "Establish a feedback loop where Woredas are alerted to discrepancies.",
    ]

    def add_bullet_slide(title, bullets):
        s = prs.slides.add_slide(prs.slide_layouts[1])
        s.shapes.title.text = title
        tf = s.placeholders[1].text_frame
        for b in bullets:
            p = tf.add_paragraph()
            p.text = b
            p.level = 0

    add_bullet_slide("Recommendations for High Utilization", rec_high)
    add_bullet_slide("Recommendations for Low Utilization", rec_low)
    add_bullet_slide("Recommendations for High Discrepancies", rec_disc)

    buf = BytesIO()
    prs.save(buf)
    buf.seek(0)
    return buf


# ---------------------------------------------------------------------
# MAIN: wire everything together (keeps original flow)
# ---------------------------------------------------------------------
def main():
    # Header
    st.markdown(
        """
        <div class="main-header-container">
            <h1>📊 Vaccine Discrepancies and Utilization Analysis</h1>
            <p>Comprehensive Vaccine Performance Monitoring</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not st.session_state.get("authenticated", False):
        st.warning("Please log in on the main page to view this dashboard.")
        st.stop()

    if st.session_state.get("matched_df") is None:
        st.info("Please upload and process data on the Data Upload page to view this dashboard.")
        st.stop()

    # Use a copy to avoid mutating session-state directly
    df_all = st.session_state["matched_df"].copy()

    required_cols = ["Region_Admin", "Zone_Admin", "Woreda_Admin", "Period"]
    if not all(col in df_all.columns for col in required_cols):
        st.error("Essential columns (Region_Admin, Zone_Admin, Woreda_Admin, Period) are missing from the processed data.")
        st.stop()

    vaccines = ["BCG", "IPV", "Measles", "Penta", "Rota"]

    # Compute utilization rates (keeps exactly original formula & clipping)
    df_all = compute_utilization_rates(df_all, vaccines)

    # Sidebar filters (returns selections)
    selected_region, selected_zone, selected_woreda, selected_period, selected_vaccine = render_sidebar_filters(df_all, vaccines)

    # Apply filters
    filtered_df = apply_filters(df_all, selected_region, selected_zone, selected_woreda, selected_period)
    if filtered_df.empty:
        st.warning("⚠️ No data found for the selected filters.")
        st.stop()

    # Scorecards
    render_scorecards(filtered_df, vaccines, selected_vaccine)

    # Extremities counts
    render_extremities_counts(filtered_df, vaccines)

    # Extremes summary table
    render_extremes_table(filtered_df, selected_vaccine, selected_region)

    # Utilization scatter plot by Woreda
    render_utilization_scatter(filtered_df, selected_vaccine)

    # Unmatched records
    render_unmatched_sections()

    # PPTX download (keeps original generation)
    ppt_buffer = create_ppt(filtered_df, selected_vaccine)
    st.download_button(
        label="📊 Download Report as PPT",
        data=ppt_buffer,
        file_name="immunization_report.pptx",
        mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        use_container_width=True,
    )


if __name__ == "__main__":
    main()
