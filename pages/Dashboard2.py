import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from config.thresholds import VACCINE_THRESHOLDS
from pptx import Presentation
from io import BytesIO

# --- Custom CSS for improved styling ---
st.markdown("""
<style>
/* Overall page layout and styling */
.stApp {
    padding-top: 1rem;
    background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
    color: #2c3e50;
    min-height: 100vh;
}

/* Header styling - More professional */
.main-header-container {
    background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
    padding: 2rem;
    border-radius: 16px;
    margin-bottom: 2rem;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
    text-align: center;
    border: 1px solid rgba(255, 255, 255, 0.1);
}

.main-header-container h1 {
    color: white;
    margin: 0;
    font-size: 2.2rem;
    font-weight: 800;
    letter-spacing: 0.5px;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
}

/* Enhanced metric cards */
.custom-metric-box {
    background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
    padding: 1.5rem;
    border-radius: 16px;
    text-align: center;
    margin-bottom: 1.5rem;
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.08);
    border: 1px solid rgba(52, 152, 219, 0.1);
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
}

.custom-metric-box::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 4px;
    height: 100%;
    background: linear-gradient(135deg, #3498db 0%, #2c3e50 100%);
}

.custom-metric-box:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 30px rgba(0, 0, 0, 0.15);
}

.custom-metric-label {
    font-size: 0.85rem;
    font-weight: 700;
    color: #7f8c8d;
    margin-bottom: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 1px;
}

.custom-metric-value {
    font-size: 2rem;
    font-weight: 800;
    color: #2c3e50;
    background: linear-gradient(135deg, #3498db 0%, #2c3e50 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

/* Section headers */
.stSubheader {
    color: #2c3e50 !important;
    font-weight: 700 !important;
    border-bottom: 3px solid #3498db;
    padding-bottom: 0.75rem;
    margin-top: 3rem !important;
    font-size: 1.6rem !important;
    letter-spacing: 0.5px;
}

/* Chart titles and labels */
.js-plotly-plot .plotly .gtitle {
    color: #2c3e50 !important;
    font-weight: 800 !important;
    font-size: 1.3rem !important;
    text-align: center;
}

.js-plotly-plot .plotly .xtitle, .js-plotly-plot .plotly .ytitle {
    color: #2c3e50 !important;
    font-weight: 700 !important;
}

.js-plotly-plot .plotly .legend text {
    color: #2c3e50 !important;
    font-weight: 600 !important;
}

/* Enhanced chart containers */
.js-plotly-plot {
    border-radius: 16px;
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.08);
    background: white;
    padding: 1.5rem;
    border: 1px solid rgba(52, 152, 219, 0.1);
}

/* Warning and info message styling - FIXED */
.stWarning {
    background-color: #fff3cd !important;
    border: 1px solid #ffeaa7 !important;
    border-radius: 12px !important;
    color: #856404 !important;
    padding: 1.25rem !important;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.stInfo {
    background: linear-gradient(135deg, #3498db 0%, #2c3e50 100%) !important;
    border: 1px solid #2980b9 !important;
    border-radius: 12px !important;
    color: white !important;
    padding: 1.25rem !important;
    box-shadow: 0 4px 12px rgba(52, 152, 219, 0.3) !important;
}

.stWarning p, .stInfo p {
    color: inherit !important;
    font-weight: 600;
}

.stWarning code, .stInfo code {
    color: inherit !important;
    background-color: rgba(255, 255, 255, 0.2) !important;
}

/* Enhanced sidebar */
.stSidebar {
    background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%) !important;
    border-right: 1px solid #e9ecef;
    box-shadow: 4px 0 20px rgba(0, 0, 0, 0.06);
}

.stSidebar .stSelectbox, .stSidebar .stSlider, .stSidebar .stTextInput {
    background: white !important;
    border-radius: 12px;
    padding: 0.75rem;
    border: 1px solid #e9ecef;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    color: #2c3e50 !important;
}

.stSidebar .stSelectbox label, .stSidebar .stSlider label, .stSidebar .stTextInput label {
    color: #2c3e50 !important;
    font-weight: 700;
}

.stSidebar .stHeader {
    color: #2c3e50 !important;
    font-weight: 700;
    border-bottom: 2px solid #3498db;
    padding-bottom: 0.75rem;
    font-size: 1.2rem;
}

/* Enhanced buttons */
.stDownloadButton button {
    background: linear-gradient(135deg, #3498db 0%, #2c3e50 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.75rem 1.5rem !important;
    font-weight: 700 !important;
    box-shadow: 0 4px 12px rgba(52, 152, 219, 0.3);
    transition: all 0.3s ease;
}

.stDownloadButton button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 18px rgba(52, 152, 219, 0.4);
}

/* Enhanced dataframe */
.dataframe {
    border-radius: 12px;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
    border: 1px solid #e9ecef;
}

/* Enhanced expander */
.streamlit-expanderHeader {
    background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
    border-radius: 12px;
    padding: 1rem;
    font-weight: 700;
    color: #2c3e50;
    border: 1px solid #e9ecef;
}

.streamlit-expanderContent {
    background: white;
    border-radius: 0 0 12px 12px;
    padding: 1.5rem;
    border: 1px solid #e9ecef;
    border-top: none;
}

/* Divider styling */
.stMarkdown hr {
    margin: 2.5rem 0;
    border: none;
    height: 3px;
    background: linear-gradient(90deg, transparent, #3498db, transparent);
}

/* Filter section styling - ENHANCED */
.filter-section {
    background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%) !important;
    padding: 1.5rem;
    border-radius: 16px;
    margin-bottom: 1.5rem;
    border: 1px solid #e9ecef;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06);
    color: #2c3e50 !important;
}

.filter-section h2, .filter-section h3, .filter-section h4 {
    color: #2c3e50 !important;
    font-weight: 700;
}

.filter-section label {
    color: #2c3e50 !important;
    font-weight: 600;
}

/* Unmatched records styling - ENHANCED */
.unmatched-section {
    background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
    padding: 1.5rem;
    border-radius: 16px;
    border: 1px solid #e9ecef;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06);
    color: #2c3e50 !important;
    margin-bottom: 1rem;
}

.unmatched-section h3, .unmatched-section h4 {
    color: #2c3e50 !important;
    font-weight: 700;
    border-bottom: 2px solid #3498db;
    padding-bottom: 0.5rem;
    margin-bottom: 1rem;
}

/* Logo container styling */
.logo-container {
    text-align: center;
    padding: 1rem;
    background: white;
    border-radius: 12px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
    border: 1px solid #e9ecef;
}

/* Section header styling */
.section-header {
    background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
    padding: 1.5rem;
    border-radius: 16px;
    margin: 2rem 0;
    color: white !important;
    text-align: center;
}

.section-header h3 {
    color: white !important;
    margin: 0;
    font-weight: 700;
    font-size: 1.5rem;
}

/* Responsive adjustments */
@media (max-width: 768px) {
    .main-header-container h1 {
        font-size: 1.8rem;
    }
    
    .custom-metric-value {
        font-size: 1.6rem;
    }
    
    .stSubheader {
        font-size: 1.4rem !important;
    }
    
    .custom-metric-box {
        padding: 1.25rem;
    }
}

/* Animation for metrics */
@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.custom-metric-box {
    animation: fadeInUp 0.6s ease-out;
}

/* Grid line enhancements - REMOVED gridlines */
.js-plotly-plot .plotly .gridlayer .grid {
    stroke: none !important;
}

.js-plotly-plot .plotly .gridlayer .xgrid, 
.js-plotly-plot .plotly .gridlayer .ygrid {
    stroke: none !important;
}

/* Custom scrollbar */
::-webkit-scrollbar {
    width: 8px;
}

::-webkit-scrollbar-track {
    background: #f1f1f1;
    border-radius: 4px;
}

::-webkit-scrollbar-thumb {
    background: linear-gradient(135deg, #3498db 0%, #2c3e50 100%);
    border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
    background: linear-gradient(135deg, #2980b9 0%, #2c3e50 100%);
}

/* Fix for all text elements */
.stSidebar * {
    color: #2c3e50 !important;
}

.stSidebar .st-bb {
    background-color: white !important;
}

.stSidebar .st-at {
    background-color: white !important;
}
</style>
""", unsafe_allow_html=True)

st.set_page_config(
    page_title="Vaccine Utilization Analytics Dashboard",
    layout="wide",
    page_icon="💉"
)

# --- Helper Function for Downloads ---
def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    processed_data = output.getvalue()
    return processed_data
    
# --- Helper Function to Count Extremities ---
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

# --- Header with Logos and Title ---
col1, col2, col3 = st.columns([1, 4, 1])
with col1:
    st.markdown('<div class="logo-container">', unsafe_allow_html=True)
    st.image("assets/moh_logo.png", width=120)
    st.markdown('</div>', unsafe_allow_html=True)
    
with col2:
    st.markdown("""
    <div class="main-header-container">
        <h1>📊 Vaccine Discrepancies and Utilization Analysis</h1>
        <p style="color: #bdc3c7; margin: 0.5rem 0 0 0; font-size: 1.1rem;">Comprehensive Vaccine Performance Monitoring</p>
    </div>
    """, unsafe_allow_html=True)
    
with col3:
    st.markdown('<div class="logo-container">', unsafe_allow_html=True)
    st.image("assets/eth_flag.png", width=120)
    st.markdown('</div>', unsafe_allow_html=True)

if not st.session_state.get("authenticated", False):
    st.warning("Please log in on the main page to view this dashboard.")
    st.stop()

# --- Main Dashboard Logic ---
if st.session_state.get("matched_df") is not None:
    df_all = st.session_state["matched_df"]
    
    # Check for required columns
    required_cols = ["Region_Admin", "Zone_Admin", "Woreda_Admin", "Period"]
    if not all(col in df_all.columns for col in required_cols):
        st.error("Essential columns (Region, Zone, Woreda, Period) are missing from the processed data.")
        st.stop()
    
    # --- Prepare data for calculation ---
    vaccines = ["BCG", "IPV", "Measles", "Penta", "Rota"]
    for vaccine in vaccines:
        admin_col = f"{vaccine}_Administered"
        dist_col = f"{vaccine}_Distributed"
        rate_col = f"{vaccine}_Utilization_Rate"
        if admin_col in df_all.columns and dist_col in df_all.columns:
            df_all[rate_col] = df_all[admin_col] / df_all[dist_col].replace(0, 1) * 100
            df_all[rate_col] = df_all[rate_col].clip(0, 1000)

    # --- Sidebar filters ---
    st.sidebar.markdown('<div class="filter-section">', unsafe_allow_html=True)
    st.sidebar.header("🧪 Filter Data")
    
    # Region filter
    regions = sorted(df_all["Region_Admin"].unique())
    selected_region = st.sidebar.selectbox("Select Region", ["All"] + regions)
    
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
    selected_vaccine = st.sidebar.selectbox("Select Vaccine", ["All"] + vaccines)
    st.sidebar.markdown('</div>', unsafe_allow_html=True)
    
    # --- Filtering Logic ---
    filtered_df = df_all
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

    # --- Scorecards (Robust against missing vaccine columns) ---
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
        
        total_dist = filtered_df[existing_dist_cols].sum().sum()
        total_admin = filtered_df[existing_admin_cols].sum().sum()
    
    utilization_rate = (total_admin / total_dist) * 100 if total_dist > 0 else 0
    
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

    # --- Extremities Count ---
    st.markdown('<div class="section-header"><h3>🚨 Extreme Utilization Rates</h3></div>', unsafe_allow_html=True)
    
    counts_col1, counts_col2, counts_col3, counts_col4, counts_col5 = st.columns(5)
    
    for i, vaccine in enumerate(vaccines):
        counts = count_extremity(filtered_df, vaccine)
        if counts:
            with [counts_col1, counts_col2, counts_col3, counts_col4, counts_col5][i]:
                st.markdown(f'<div class="custom-metric-box"><div class="custom-metric-label">{vaccine}</div><div class="custom-metric-value">{counts[0]}↑ | {counts[1]}↓</div></div>', unsafe_allow_html=True)
    st.markdown("---")
    
    # --- New Table for Extreme Utilization ---
    st.markdown('<div class="section-header"><h3>📋 Extreme Utilization by Region and Zone</h3></div>', unsafe_allow_html=True)
    
    if selected_vaccine == "All":
        st.info("Please select a specific vaccine to view this table.")
    else:
        # Check if the required column exists
        rate_col = f"{selected_vaccine}_Utilization_Rate"
        if rate_col not in filtered_df.columns:
            st.warning(f"Utilization data for {selected_vaccine} is not available in the processed files.")
            st.stop()
        
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

    st.markdown("---")
    
    # --- Utilization Rate by Woreda ---
    st.markdown('<div class="section-header"><h3>📈 Utilization Rate by Woreda</h3></div>', unsafe_allow_html=True)
    
    if selected_vaccine == "All":
        st.info("Please select a specific vaccine to view utilization rate plots.")
    else:
        # Check if the required column exists
        rate_col = f"{selected_vaccine}_Utilization_Rate"
        if rate_col not in filtered_df.columns:
            st.warning(f"Utilization data for {selected_vaccine} is not available in the processed files.")
            st.stop()
        
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
                         annotation_text="High Threshold", annotation_position="bottom right")
            fig.add_hline(y=thresholds[selected_vaccine]["low"], line_dash="dash", line_color="orange", 
                         annotation_text="Low Threshold", annotation_position="top right")
        
        # Improve visibility of labels and legends
        fig.update_layout(
            xaxis_title="Woreda", 
            yaxis_title="Utilization Rate (%)", 
            xaxis_tickangle=45,
            plot_bgcolor='#ffffff',
            paper_bgcolor='#ffffff',
            font=dict(color='#2c3e50', size=14),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                font=dict(size=12, color='#2c3e50')
            ),
            hoverlabel=dict(
                bgcolor="white",
                font_size=12,
                font_family="Arial",
                font_color="#2c3e50"
            )
        )
        
        # Improve x-axis label visibility
        fig.update_xaxes(tickfont=dict(size=10, color='#2c3e50'), showgrid=False)
        fig.update_yaxes(tickfont=dict(color='#2c3e50'), showgrid=False)
        
        st.plotly_chart(fig, use_container_width=True)

    # --- Unmatched Records ---
    st.markdown('<div class="section-header"><h3>🔍 Unmatched Records</h3></div>', unsafe_allow_html=True)
    
    unmatched_col1, unmatched_col2 = st.columns(2)
    
    with unmatched_col1:
        st.markdown('<div class="unmatched-section">', unsafe_allow_html=True)
        if "unmatched_admin_df" in st.session_state and not st.session_state["unmatched_admin_df"].empty:
            st.write("**Unmatched Administered Records**")
            st.dataframe(st.session_state["unmatched_admin_df"], use_container_width=True)
        else:
            st.info("No unmatched administered records found.")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with unmatched_col2:
        st.markdown('<div class="unmatched-section">', unsafe_allow_html=True)
        if "unmatched_dist_df" in st.session_state and not st.session_state["unmatched_dist_df"].empty:
            st.write("**Unmatched Distributed Records**")
            st.dataframe(st.session_state["unmatched_dist_df"], use_container_width=True)
        else:
            st.info("No unmatched distributed records found.")
        st.markdown('</div>', unsafe_allow_html=True)
            
    st.markdown("---")
    
    # --- PPT Download Button ---
    def create_ppt(filtered_df, selected_vaccine):
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

    ppt_buffer = create_ppt(filtered_df, selected_vaccine)
    st.download_button(
        label="📊 Download Report as PPT",
        data=ppt_buffer,
        file_name="immunization_report.pptx",
        mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        use_container_width=True
    )
else:
    st.info("Please upload and process data on the Data Upload page to view this dashboard.")
