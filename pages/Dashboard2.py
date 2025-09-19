import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from config.thresholds import VACCINE_THRESHOLDS
from pptx import Presentation
from io import BytesIO

# =======================
# Page Config & Styling
# =======================
st.set_page_config(
    page_title="Vaccine Utilization Analytics Dashboard",
    layout="wide",
    page_icon="💉"
)

st.markdown("""
    <style>
        body, .stApp, .st-emotion-cache-1dp5vir, .block-container {
            background-color: white !important;
            color: black !important;
        }
        .stSidebar {
            background-color: white !important;
            color: black !important;
        }
        .stSidebar .st-emotion-cache-1a85o2b h4, .stSidebar .st-emotion-cache-1a85o2b label {
            color: black !important;
        }
        .stSidebar .st-emotion-cache-1a85o2b selectbox > div > div {
            background-color: white !important;
            color: black !important;
        }
        .stSidebar .st-emotion-cache-1a85o2b selectbox > div > div > div {
            color: black !important;
        }
        .stSidebar select {
            background-color: white !important;
            color: black !important;
        }
        .stSidebar select option {
            background-color: white !important;
            color: black !important;
        }
        .stSidebar .css-1d391kg {
            background-color: white !important;
            color: black !important;
        }
        .stSidebar .css-1v0mbdj {
            background-color: white !important;
            color: black !important;
        }
        .stSidebar .css-2trqtx {
            background-color: white !important;
            color: black !important;
        }
        .stSidebar .css-1d391kg option {
            background-color: white !important;
            color: black !important;
        }
        .stSidebar .stSelectbox {
            background-color: white !important;
            color: black !important;
        }
        .stSidebar .stSelectbox > div > div > div {
            background-color: white !important;
            color: black !important;
        }
        /* Multi-page sidebar navigation */
        .stSidebar [data-testid="stSidebar"] {
            background-color: white !important;
        }
        .stSidebar .css-1d391kg a {
            color: black !important;
        }
        .stSidebar .css-1d391kg a:hover {
            color: #3498db !important;
        }
        .stSidebar .css-1d391kg li {
            color: black !important;
        }
        .stSidebar .css-1d391kg ul {
            background-color: white !important;
        }
        .stSidebar .css-1d391kg .nav-link {
            color: black !important;
        }
        .stSidebar .css-1d391kg .nav-link:hover {
            color: #3498db !important;
            background-color: #f8f9fa !important;
        }
        .stSidebar .css-2trqtx a {
            color: black !important;
        }
        .stSidebar .css-2trqtx a:hover {
            color: #3498db !important;
        }
        /* Additional selectors for page links */
        section[data-testid="stSidebar"] div[role="main"] a {
            color: black !important;
        }
        section[data-testid="stSidebar"] div[role="main"] a:hover {
            color: #3498db !important;
        }
        .title-text {
            font-size: 36px;
            font-weight: bold;
            color: black;
            text-align: center;
            margin-bottom: 20px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        }
        .section-header {
            font-size: 24px;
            font-weight: bold;
            color: black;
            margin-top: 30px;
            margin-bottom: 15px;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
        }
        .highlight-box {
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 10px;
            border: 1px solid #e0e0e0;
            color: black;
        }
        .metric-title {
            font-size: 18px;
            font-weight: bold;
            color: black;
            margin-bottom: 5px;
        }
        .metric-value {
            font-size: 22px;
            font-weight: bold;
            color: black;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 0;
            background-color: transparent;
            border-radius: 8px;
            padding: 5px;
            margin-bottom: 20px;
        }
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            white-space: pre-wrap;
            background-color: white;
            border-radius: 8px;
            gap: 8px;
            padding: 10px 20px;
            font-weight: bold;
            color: black;
            border: 2px solid #bdc3c7;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            margin-right: 5px;
            transition: all 0.3s ease;
        }
        .stTabs [data-baseweb="tab"]:hover {
            border-color: #3498db;
            box-shadow: 0 4px 8px rgba(52, 152, 219, 0.2);
        }
        .stTabs [aria-selected="true"] {
            background-color: #3498db;
            color: white;
            border-color: #3498db;
            box-shadow: 0 4px 12px rgba(52, 152, 219, 0.3);
        }
        .stTabs [aria-selected="true"]:hover {
            box-shadow: 0 6px 16px rgba(52, 152, 219, 0.4);
        }
        .stTabs [data-baseweb="tab-panel"] {
            padding-top: 20px;
            margin-top: 20px;
        }
        .custom-metric-box {
            background: white;
            padding: 1rem;
            border-radius: 12px;
            text-align: center;
            margin-bottom: 1rem;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06);
            border: 1px solid #e0e0e0;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
            height: 120px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            color: black;
        }
        .custom-metric-box:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
        }
        .custom-metric-label {
            font-size: 0.75rem;
            font-weight: 600;
            color: #404040 !important;
            margin-bottom: 0.5rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .custom-metric-value {
            font-size: 1.5rem;
            font-weight: 700;
            color: #000000 !important;
        }
        .plot-container {
            background: white;
            padding: 15px;
            border-radius: 10px;
            border: 1px solid #e0e0e0;
            margin-bottom: 20px;
            color: black;
        }
        .stDataFrame {
            background-color: white !important;
            color: black !important;
        }
        .stDataFrame table {
            background-color: white !important;
            color: black !important;
        }
        .stDataFrame th, .stDataFrame td {
            color: black !important;
            border-color: #e0e0e0 !important;
        }
        .st-emotion-cache-1a85o2b {
            color: black !important;
        }
        .stWarning, .stInfo {
            background-color: #f8f9fa;
            color: black;
            border: 1px solid #e0e0e0;
        }
    </style>
""", unsafe_allow_html=True)

# =======================
# Helper Functions
# =======================
def to_excel(df):
    """Convert DataFrame to Excel file for download"""
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    processed_data = output.getvalue()
    return processed_data

def count_extremity(df, vaccine):
    """Calculates high and low extremity counts based on user-defined thresholds."""
    rate_col = f"{vaccine}_Utilization_Rate"
    if rate_col not in df.columns:
        return None
   
    # User-provided thresholds (as decimals)
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

def setup_filters(df_all):
    """Set up sidebar filters and return filtered DataFrame"""
    st.sidebar.header("🧪 Filter Data")
   
    # Region filter
    regions = sorted(df_all["Region_Admin"].unique())
    selected_region = st.sidebar.selectbox("Select Region", ["All"] + regions)
    st.session_state.selected_region = selected_region
   
    # Zone filter (chained to Region)
    filtered_zones = df_all[df_all["Region_Admin"] == selected_region]["Zone_Admin"].unique() if selected_region != "All" else df_all["Zone_Admin"].unique()
    zones = sorted(filtered_zones)
    selected_zone = st.sidebar.selectbox("Select Zone", ["All"] + zones)
   
    # Woreda filter (chained to Zone)
    if selected_zone != "All":
        filtered_woredas = df_all[(df_all["Region_Admin"] == selected_region) & (df_all["Zone_Admin"] == selected_zone)]["Woreda_Admin"].unique()
    elif selected_region != "All":
        filtered_woredas = df_all[df_all["Region_Admin"] == selected_region]["Woreda_Admin"].unique()
    else:
        filtered_woredas = df_all["Woreda_Admin"].unique()
    woredas = sorted(filtered_woredas)
    selected_woreda = st.sidebar.selectbox("Select Woreda", ["All"] + woredas)
    # Period filter
    periods = sorted(df_all["Period"].unique())
    selected_period = st.sidebar.selectbox("Select Period", ["All"] + periods)
   
    # Vaccine filter
    vaccines = ["BCG", "IPV", "Measles", "Penta", "Rota"]
    selected_vaccine = st.sidebar.selectbox("Select Vaccine", ["All"] + vaccines)
   
    # Filtering Logic
    filtered_df = df_all
    if selected_region != "All":
        filtered_df = filtered_df[filtered_df["Region_Admin"] == selected_region]
    if selected_zone != "All":
        filtered_df = filtered_df[filtered_df["Zone_Admin"] == selected_zone]
    if selected_woreda != "All":
        filtered_df = filtered_df[filtered_df["Woreda_Admin"] == selected_woreda]
    if selected_period != "All":
        filtered_df = filtered_df[filtered_df["Period"] == selected_period]
       
    return filtered_df, selected_vaccine, vaccines

def display_kpis(filtered_df, selected_vaccine, vaccines):
    """Display Key Performance Indicators"""
    total_woredas = filtered_df["Woreda_Admin"].nunique()
   
    if selected_vaccine != "All":
        dist_col = f"{selected_vaccine}_Distributed"
        admin_col = f"{selected_vaccine}_Administered"
        if dist_col in filtered_df.columns and admin_col in filtered_df.columns:
            total_admin = filtered_df[admin_col].sum()
            total_dist = filtered_df[dist_col].sum()
        else:
            st.warning(f"Data for '{selected_vaccine}' is not available in the processed files.")
            return
    else:
        dist_cols = [f"{v}_Distributed" for v in vaccines]
        admin_cols = [f"{v}_Administered" for v in vaccines]
       
        existing_dist_cols = [col for col in dist_cols if col in filtered_df.columns]
        existing_admin_cols = [col for col in admin_cols if col in filtered_df.columns]
       
        total_dist = filtered_df[existing_dist_cols].sum().sum()
        total_admin = filtered_df[existing_admin_cols].sum().sum()
   
    utilization_rate = (total_admin / total_dist) * 100 if total_dist > 0 else 0
   
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f'<div class="custom-metric-box"><div class="custom-metric-label">Total Woredas</div><div class="custom-metric-value">{total_woredas}</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="custom-metric-box"><div class="custom-metric-label">Total Doses Distributed</div><div class="custom-metric-value">{total_dist:,.0f}</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="custom-metric-box"><div class="custom-metric-label">Total Doses Administered</div><div class="custom-metric-value">{total_admin:,.0f}</div></div>', unsafe_allow_html=True)
    with col4:
        st.markdown(f'<div class="custom-metric-box"><div class="custom-metric-label">Utilization Rate</div><div class="custom-metric-value">{utilization_rate:.2f}%</div></div>', unsafe_allow_html=True)

def display_extremities(filtered_df, vaccines):
    """Display extremity counts for each vaccine"""
    counts_col1, counts_col2, counts_col3, counts_col4, counts_col5 = st.columns(5)
   
    for i, vaccine in enumerate(vaccines):
        counts = count_extremity(filtered_df, vaccine)
        if counts:
            with [counts_col1, counts_col2, counts_col3, counts_col4, counts_col5][i]:
                st.markdown(f'<div class="custom-metric-box"><div class="custom-metric-label">{vaccine}</div><div class="custom-metric-value">{counts[0]}↑ | {counts[1]}↓</div></div>', unsafe_allow_html=True)

def display_extreme_utilization_table(filtered_df, selected_vaccine):
    """Display table of extreme utilization by region and zone"""
    if selected_vaccine == "All":
        st.info("Please select a specific vaccine to view this table.")
        return
   
    # Check if the required column exists
    rate_col = f"{selected_vaccine}_Utilization_Rate"
    if rate_col not in filtered_df.columns:
        st.warning(f"Utilization data for {selected_vaccine} is not available in the processed files.")
        return
   
    # User-provided thresholds (as decimals)
    thresholds = {
        "BCG": {"high": 1.20, "low": 0.30},
        "IPV": {"high": 1.30, "low": 0.75},
        "Measles": {"high": 1.25, "low": 0.50},
        "Penta": {"high": 1.30, "low": 0.80},
        "Rota": {"high": 1.30, "low": 0.75},
    }
    # Create a copy of the filtered data
    extreme_df = filtered_df.copy()
   
    # Determine grouping columns based on filter selection
    selected_region = st.session_state.get('selected_region', 'All')
    if selected_region == "All":
        group_cols = ["Region_Admin"]
    else:
        group_cols = ["Region_Admin", "Zone_Admin"]
   
    # Calculate counts for each category
    extreme_df["High_Extremity"] = extreme_df[rate_col] / 100 > thresholds[selected_vaccine]["high"]
    extreme_df["Low_Extremity"] = extreme_df[rate_col] / 100 < thresholds[selected_vaccine]["low"]
    extreme_summary = extreme_df.groupby(group_cols).agg(
        total_woredas=("Woreda_Admin", "nunique"),
        high_extremity_count=("High_Extremity", "sum"),
        low_extremity_count=("Low_Extremity", "sum")
    ).reset_index()
   
    # Rename columns for display
    extreme_summary.rename(columns={
        "Region_Admin": "Region",
        "Zone_Admin": "Zone",
        "total_woredas": "Total Woredas",
        "high_extremity_count": "High Extremity",
        "low_extremity_count": "Low Extremity",
    }, inplace=True)
    st.dataframe(extreme_summary, use_container_width=True, hide_index=True)
   
    st.download_button(
        label="📥 Download Data as Excel",
        data=to_excel(extreme_summary),
        file_name=f"Extreme_Utilization_Data_{selected_vaccine}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )

def display_utilization_chart(filtered_df, selected_vaccine):
    """Display utilization rate chart by Woreda"""
    if selected_vaccine == "All":
        st.info("Please select a specific vaccine to view utilization rate plots.")
        return
   
    # Check if the required column exists
    rate_col = f"{selected_vaccine}_Utilization_Rate"
    if rate_col not in filtered_df.columns:
        st.warning(f"Utilization data for {selected_vaccine} is not available in the processed files.")
        return
   
    # Create a scatter plot of utilization rates
    fig = px.scatter(
        filtered_df,
        x="Woreda_Admin",
        y=rate_col,
        title=f"{selected_vaccine} Utilization Rate by Woreda",
        labels={"Woreda_Admin": "Woreda", rate_col: "Utilization Rate (%)"},
        color_discrete_sequence=["#3498db"]
    )
   
    # Add threshold lines
    thresholds = {
        "BCG": {"high": 120, "low": 30},
        "IPV": {"high": 130, "low": 75},
        "Measles": {"high": 125, "low": 50},
        "Penta": {"high": 130, "low": 80},
        "Rota": {"high": 130, "low": 75},
    }
   
    if selected_vaccine in thresholds:
        fig.add_hline(y=thresholds[selected_vaccine]["high"], line_dash="dash", line_color="red",
                     annotation_text="High Threshold", annotation_position="bottom right", annotation_font_color="black")
        fig.add_hline(y=thresholds[selected_vaccine]["low"], line_dash="dash", line_color="orange",
                     annotation_text="Low Threshold", annotation_position="top right", annotation_font_color="black")
   
    # Improve visibility of labels and legends
    fig.update_layout(
        xaxis_title="Woreda",
        yaxis_title="Utilization Rate (%)",
        xaxis_tickangle=45,
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(color='black', size=12),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=11, color='black'),
            bgcolor='rgba(255,255,255,0.9)',
            bordercolor='#e0e0e0',
            borderwidth=1
        ),
        hoverlabel=dict(
            bgcolor="white",
            font_size=11,
            font_family="Arial",
            font_color="black",
            bordercolor="#e0e0e0"
        )
    )
   
    # Improve x-axis label visibility
    fig.update_xaxes(tickfont=dict(size=9, color='black'), showgrid=True, gridcolor='rgba(0,0,0,0.1)')
    fig.update_yaxes(tickfont=dict(color='black'), showgrid=True, gridcolor='rgba(0,0,0,0.1)')
   
    st.plotly_chart(fig, use_container_width=True)

def create_ppt(filtered_df, selected_vaccine):
    """Create PowerPoint report"""
    prs = Presentation()
   
    # Slide 1: Title Slide
    title_slide_layout = prs.slide_layouts[0]
    slide = prs.slides.add_slide(title_slide_layout)
    title = slide.shapes.title
    title.text = "Immunization Triangulation Report"
   
    body = slide.placeholders[1]
    body.text = f"Report generated for {selected_vaccine}."
    # Slide 2: Recommendations for High Utilization
    rec_high_layout = prs.slide_layouts[1]
    rec_high_slide = prs.slides.add_slide(rec_high_layout)
    rec_high_slide.shapes.title.text = "Recommendations for High Utilization"
   
    rec_high_text = rec_high_slide.placeholders[1].text_frame
   
    p_high_bullet1 = rec_high_text.add_paragraph()
    p_high_bullet1.text = "Conduct a targeted audit of administered dose records for potential data entry errors."
    p_high_bullet1.level = 0
    p_high_bullet2 = rec_high_text.add_paragraph()
    p_high_bullet2.text = "Investigate potential lags in reporting of distributed doses."
    p_high_bullet2.level = 0
   
    p_high_bullet3 = rec_high_text.add_paragraph()
    p_high_bullet3.text = "Recommend a physical stock count at facilities to reconcile administered and distributed doses."
    p_high_bullet3.level = 0
    # Slide 3: Recommendations for Low Utilization
    rec_low_layout = prs.slide_layouts[1]
    rec_low_slide = prs.slides.add_slide(rec_low_layout)
    rec_low_slide.shapes.title.text = "Recommendations for Low Utilization"
   
    rec_low_text = rec_low_slide.placeholders[1].text_frame
    p_low_bullet1 = rec_low_text.add_paragraph()
    p_low_bullet1.text = "Assess inventory levels to prevent vaccine expiration due to overstocking."
    p_low_bullet1.level = 0
    p_low_bullet2 = rec_low_text.add_paragraph()
    p_low_bullet2.text = "Investigate if there are service delivery issues affecting vaccine demand."
    p_low_bullet2.level = 0
    p_low_bullet3 = rec_low_text.add_paragraph()
    p_low_bullet3.text = "Verify that administered doses are being reported accurately and on time."
    p_low_bullet3.level = 0
    # Slide 4: Recommendations for High Discrepancies
    rec_disc_layout = prs.slide_layouts[1]
    rec_disc_slide = prs.slides.add_slide(rec_disc_layout)
    rec_disc_slide.shapes.title.text = "Recommendations for High Discrepancies"
   
    rec_disc_text = rec_disc_slide.placeholders[1].text_frame
   
    p_disc_bullet1 = rec_disc_text.add_paragraph()
    p_disc_bullet1.text = "Provide training on accurate reporting for both administered and distributed doses."
    p_disc_bullet1.level = 0
    p_disc_bullet2 = rec_disc_text.add_paragraph()
    p_disc_bullet2.text = "Implement a process to regularly cross-reference data to catch discrepancies early."
    p_disc_bullet2.level = 0
    p_disc_bullet3 = rec_disc_text.add_paragraph()
    p_disc_bullet3.text = "Establish a feedback loop where Woredas are alerted to discrepancies."
    p_disc_bullet3.level = 0
   
    ppt_file = BytesIO()
    prs.save(ppt_file)
    ppt_file.seek(0)
    return ppt_file

# =======================
# Main Dashboard Logic
# =======================
def main():
    """Main dashboard function"""
    st.markdown("<div class='title-text'>Vaccine Discrepancies and Utilization Analysis</div>", unsafe_allow_html=True)
    if not st.session_state.get("authenticated", False):
        st.warning("Please log in on the main page to view this dashboard.")
        return
    if st.session_state.get("matched_df") is None:
        st.info("Please upload and process data on the Data Upload page to view this dashboard.")
        return
       
    df_all = st.session_state["matched_df"]
   
    # Check for required columns
    required_cols = ["Region_Admin", "Zone_Admin", "Woreda_Admin", "Period"]
    if not all(col in df_all.columns for col in required_cols):
        st.error("Essential columns (Region, Zone, Woreda, Period) are missing from the processed data.")
        return
   
    # Prepare data for calculation
    vaccines = ["BCG", "IPV", "Measles", "Penta", "Rota"]
    for vaccine in vaccines:
        admin_col = f"{vaccine}_Administered"
        dist_col = f"{vaccine}_Distributed"
        rate_col = f"{vaccine}_Utilization_Rate"
        if admin_col in df_all.columns and dist_col in df_all.columns:
            df_all[rate_col] = df_all[admin_col] / df_all[dist_col].replace(0, 1) * 100
            df_all[rate_col] = df_all[rate_col].clip(0, 1000)
    # Setup filters
    filtered_df, selected_vaccine, vaccines = setup_filters(df_all)
    if filtered_df.empty:
        st.warning("⚠️ No data found for the selected filters.")
        return
    # Create tabs for different sections
    tab1, tab2, tab3, tab4 = st.tabs(["Performance", "Extremes", "Charts", "Download Report as PPT"])
   
    # --- Performance Tab ---
    with tab1:
        st.markdown("<div class='section-header'>Performance Metrics</div>", unsafe_allow_html=True)
        display_kpis(filtered_df, selected_vaccine, vaccines)
   
    # --- Extremes Tab ---
    with tab2:
        st.markdown("<div class='section-header'>Utilization Extremes</div>", unsafe_allow_html=True)
        display_extremities(filtered_df, vaccines)
        st.markdown("<div class='section-header'>Extreme Utilization by Region and Zone</div>", unsafe_allow_html=True)
        display_extreme_utilization_table(filtered_df, selected_vaccine)
   
    # --- Charts Tab ---
    with tab3:
        st.markdown("<div class='section-header'>Usage Charts</div>", unsafe_allow_html=True)
        display_utilization_chart(filtered_df, selected_vaccine)
   
    # --- Download Report as PPT Tab ---
    with tab4:
        st.markdown("<div class='section-header'>Download Report</div>", unsafe_allow_html=True)
       
        # PPT Download Button
        ppt_buffer = create_ppt(filtered_df, selected_vaccine)
        st.download_button(
            label="📊 Download Report as PPT",
            data=ppt_buffer,
            file_name="immunization_report.pptx",
            mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
            use_container_width=True
        )

# Run the main function
if __name__ == "__main__":
    main()
