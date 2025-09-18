import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from config.thresholds import VACCINE_THRESHOLDS
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

.main-header-container p {
    color: #bdc3c7;
    margin: 0.5rem 0 0 0;
    font-size: 1.1rem;
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

/* Pie chart enhancements */
.plotly .pie .slice path {
    stroke: white;
    stroke-width: 2px;
}

.plotly .pie .slice text {
    font-weight: 700 !important;
    font-size: 11px !important;
}

/* Stacked bar chart enhancements */
.plotly .bar path {
    stroke: white;
    stroke-width: 1px;
}

/* Warning and info message styling */
.stWarning, .stInfo {
    background-color: #fff3cd !important;
    border: 1px solid #ffeaa7 !important;
    border-radius: 12px !important;
    color: #856404 !important;
    padding: 1.25rem !important;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.stWarning p, .stInfo p {
    color: #856404 !important;
    font-weight: 600;
}

.stWarning code, .stInfo code {
    color: #856404 !important;
    background-color: rgba(255, 255, 255, 0.5) !important;
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

/* Sidebar text colors */
.stSidebar p, .stSidebar div, .stSidebar span {
    color: #2c3e50 !important;
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

/* Drag and drop area styling */
.stFileUploader {
    background-color: #1a1a1a !important;
    border-radius: 12px;
    padding: 1.25rem;
    border: 2px dashed #666666;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.stFileUploader label {
    color: white !important;
    font-weight: 700;
}

.stFileUploader p {
    color: #cccccc !important;
}

.stFileUploader .file-info {
    color: #ffffff !important;
    background-color: #333333 !important;
    border-radius: 8px;
    padding: 0.75rem;
    margin-top: 0.75rem;
}

/* Uploaded file info */
.uploadedFile {
    background-color: #333333 !important;
    color: white !important;
    border-radius: 8px;
    padding: 0.75rem;
    margin: 0.5rem 0;
}

.uploadedFile name {
    color: white !important;
}

/* Responsive adjustments */
@media (max-width: 768px) {
    .main-header-container h1 {
        font-size: 1.8rem;
    }
    
    .main-header-container p {
        font-size: 1rem;
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

/* Legend enhancements */
.js-plotly-plot .plotly .legend {
    background: rgba(255, 255, 255, 0.95) !important;
    border: 1px solid #e9ecef !important;
    border-radius: 8px !important;
    padding: 10px !important;
}

/* Grid line enhancements */
.js-plotly-plot .plotly .gridlayer .grid {
    stroke: #e9ecef !important;
    stroke-width: 1px !important;
}

/* Hover effects for charts */
.js-plotly-plot .plotly .hoverlayer path {
    fill: rgba(52, 152, 219, 0.1) !important;
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

/* Fix for all text elements in sidebar */
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

# --- Helper Function to Categorize Utilization ---
def categorize_utilization(row, vaccine_name):
    rate = row[f"{vaccine_name}_Utilization_Rate"] / 100
    thresholds = VACCINE_THRESHOLDS.get(vaccine_name)
    
    if not thresholds:
        return "Not Applicable"

    if rate > thresholds["unacceptable"]:
        return "Unacceptable"
    elif thresholds["acceptable"] <= rate <= thresholds["unacceptable"]:
        return "Acceptable"
    else:
        return "Low Utilization"

# --- Header with Title Only ---
st.markdown("""
<div class="main-header-container">
    <h1>📊 Vaccine Utilization Analytics Dashboard</h1>
    <p>Comprehensive Vaccine Distribution & Utilization Analysis</p>
</div>
""", unsafe_allow_html=True)

if not st.session_state.get("authenticated", False):
    st.warning("Please log in on the main page to view this dashboard.")
    st.stop()

# --- Main Dashboard Logic ---
if st.session_state.get("matched_df") is not None:
    df_all = st.session_state["matched_df"]
    
    # --- Prepare data for calculation ---
    vaccines = ["BCG", "IPV", "Measles", "Penta", "Rota"]
    for vaccine in vaccines:
        admin_col = f"{vaccine}_Administered"
        dist_col = f"{vaccine}_Distributed"
        rate_col = f"{vaccine}_Utilization_Rate"
        if admin_col in df_all.columns and dist_col in df_all.columns:
            df_all[rate_col] = df_all[admin_col] / df_all[dist_col].replace(0, 1) * 100
            df_all[rate_col] = df_all[rate_col].clip(0, 1000) # Clip high values for visualization

    # --- Sidebar filters ---
    st.sidebar.header("🧪 Filter Data")
    
    # Check for required columns
    required_cols = ["Region_Admin", "Zone_Admin", "Woreda_Admin", "Period"]
    if not all(col in df_all.columns for col in required_cols):
        st.error("Essential columns (Region, Zone, Woreda, Period) are missing from the processed data.")
        st.stop()

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

    # --- Summary metrics (Robust against missing vaccine columns) ---
    dist_cols = [f"{v}_Distributed" for v in vaccines]
    admin_cols = [f"{v}_Administered" for v in vaccines]

    if selected_vaccine != "All":
        dist_col = f"{selected_vaccine}_Distributed"
        admin_col = f"{selected_vaccine}_Administered"
        
        if dist_col in filtered_df.columns and admin_col in filtered_df.columns:
            total_distributed = filtered_df[dist_col].sum()
            total_administered = filtered_df[admin_col].sum()
        else:
            st.warning(f"Data for '{selected_vaccine}' is not available in the processed files.")
            st.stop()
    else:
        existing_dist_cols = [col for col in dist_cols if col in filtered_df.columns]
        existing_admin_cols = [col for col in admin_cols if col in filtered_df.columns]
        
        total_distributed = filtered_df[existing_dist_cols].sum().sum()
        total_administered = filtered_df[existing_admin_cols].sum().sum()

    overall_utilization_rate = (total_administered / total_distributed * 100) if total_distributed > 0 else 0
    total_woredas = filtered_df["Woreda_Admin"].nunique()

    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f'<div class="custom-metric-box"><div class="custom-metric-label">Total Woredas</div><div class="custom-metric-value">{total_woredas}</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="custom-metric-box"><div class="custom-metric-label">Total Doses Distributed</div><div class="custom-metric-value">{total_distributed:,.0f}</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="custom-metric-box"><div class="custom-metric-label">Total Doses Administered</div><div class="custom-metric-value">{total_administered:,.0f}</div></div>', unsafe_allow_html=True)
    with col4:
        st.markdown(f'<div class="custom-metric-box"><div class="custom-metric-label">Overall Utilization Rate</div><div class="custom-metric-value">{overall_utilization_rate:.2f}%</div></div>', unsafe_allow_html=True)
    st.markdown("---")

    # --- Woreda Counts by Category (Based on selected vaccine) ---
    st.subheader("Woreda Counts by Utilization Category")
    
    if selected_vaccine == "All":
        st.info("Select a specific vaccine to view Woreda-level categories.")
        st.stop()

    if f"{selected_vaccine}_Utilization_Rate" not in filtered_df.columns:
        st.warning(f"Utilization data for {selected_vaccine} is not available in the processed files.")
        st.stop()
        
    filtered_df[f"{selected_vaccine}_Utilization_Category"] = filtered_df.apply(lambda row: categorize_utilization(row, selected_vaccine), axis=1)
    category_counts = filtered_df[f"{selected_vaccine}_Utilization_Category"].value_counts()
    
    col_w1, col_w2, col_w3, col_w4 = st.columns(4)
    with col_w1:
        st.markdown(f'<div class="custom-metric-box"><div class="custom-metric-label">Total Woredas</div><div class="custom-metric-value">{total_woredas}</div></div>', unsafe_allow_html=True)
    with col_w2:
        st.markdown(f'<div class="custom-metric-box"><div class="custom-metric-label">Acceptable</div><div class="custom-metric-value">{category_counts.get("Acceptable", 0)}</div></div>', unsafe_allow_html=True)
    with col_w3:
        st.markdown(f'<div class="custom-metric-box"><div class="custom-metric-label">Unacceptable</div><div class="custom-metric-value">{category_counts.get("Unacceptable", 0)}</div></div>', unsafe_allow_html=True)
    with col_w4:
        st.markdown(f'<div class="custom-metric-box"><div class="custom-metric-label">Low Utilization</div><div class="custom-metric-value">{category_counts.get("Low Utilization", 0)}</div></div>', unsafe_allow_html=True)
    st.markdown("---")

    # --- Pie chart + Woreda category table ---
    st.subheader(f"Overall Utilization Breakdown ({selected_vaccine})")
    
    # Pie chart data preparation
    category_counts_pie = category_counts.reset_index()
    category_counts_pie.columns = ["Category", "Count"]
    category_counts_pie["Percentage"] = (category_counts_pie["Count"] / category_counts_pie["Count"].sum() * 100).round(2)
    
    color_map = {"Acceptable": "#28a745", "Unacceptable": "#007bff", "Low Utilization": "#dc3545"}
    pie_fig = px.pie(category_counts_pie, values="Percentage", names="Category", hole=0.0, color="Category", color_discrete_map=color_map,
                     title=f"Utilization Category for {selected_vaccine}")
    
    pie_fig.update_traces(
        textinfo='percent+label',
        textfont=dict(color="white", size=12, weight='bold'),
        textposition='inside',
        insidetextorientation='horizontal'
    )
    pie_fig.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(color='#2c3e50', size=12),
        height=450,
        showlegend=True,
        legend=dict(
            bgcolor='rgba(255,255,255,0.95)',
            font=dict(color='#2c3e50', size=11),
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5
        ),
        title=dict(
            font=dict(size=18, color='#2c3e50', weight='bold'),
            x=0.5,
            xanchor='center'
        )
    )
    
    st.plotly_chart(pie_fig, use_container_width=True)

    st.markdown("---")
    
    # --- Bar chart (100% Stacked) ---
    st.subheader(f"Utilization by Geographic Area - {selected_vaccine} ({selected_period})")

    # Dynamic grouping logic
    groupby_col = "Region_Admin"
    if selected_zone != "All":
        groupby_col = "Woreda_Admin"
    elif selected_region != "All":
        groupby_col = "Zone_Admin"
    
    stacked_bar_data = filtered_df.groupby([groupby_col, f"{selected_vaccine}_Utilization_Category"]).size().reset_index(name='Count')
    total_by_group = stacked_bar_data.groupby(groupby_col)["Count"].sum().reset_index(name='Total')
    stacked_bar_data = stacked_bar_data.merge(total_by_group, on=groupby_col)
    stacked_bar_data["Percentage"] = (stacked_bar_data["Count"] / stacked_bar_data["Total"] * 100).round(2)
    
    bar_fig = go.Figure()
    for category in ["Acceptable", "Low Utilization", "Unacceptable"]:
        f_data = stacked_bar_data[stacked_bar_data[f"{selected_vaccine}_Utilization_Category"] == category]
        bar_fig.add_trace(go.Bar(x=f_data[groupby_col], y=f_data["Percentage"], name=category, marker_color=color_map.get(category),
                                 text=f_data["Percentage"].apply(lambda x: f"{x:.0f}%"),
                                 textposition='inside',
                                 textfont=dict(color='white', size=10, weight='bold'),
                                 hovertemplate=f"<b>%{{x}}</b><br>{category}: %{{y:.2f}}%<br>Woreda Count: %{{customdata}}<extra></extra>",
                                 customdata=f_data['Count']))
    
    bar_fig.update_layout(
        barmode="stack", 
        yaxis=dict(
            title="Percentage (%)", 
            range=[0, 100], 
            tickformat=".0f",
            title_font=dict(size=14, color='#2c3e50', weight='bold'),
            tickfont=dict(size=12, color='#2c3e50')
        ),
        xaxis=dict(
            title=groupby_col.split('_')[0], 
            tickangle=-45,
            title_font=dict(size=14, color='#2c3e50', weight='bold'),
            tickfont=dict(size=11, color='#2c3e50')
        ),
        legend_title_text="Utilization Category", 
        bargap=0.2,
        legend=dict(
            orientation="h", 
            yanchor="bottom", 
            y=1.02, 
            xanchor="right", 
            x=1,
            font=dict(size=12, color='#2c3e50'),
            title_font=dict(size=12, color='#2c3e50', weight='bold')
        ),
        height=650,
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(color='#2c3e50', size=12),
        title=dict(
            text=f"Utilization by {groupby_col.split('_')[0]} - {selected_vaccine}",
            font=dict(size=16, color='#2c3e50', weight='bold'),
            x=0.5,
            xanchor='center'
        )
    )
    st.plotly_chart(bar_fig, use_container_width=True)

    st.markdown("---")
    
    with st.expander("📋 Show Woreda-Level Data"):
        display_df = filtered_df[["Region_Admin", "Zone_Admin", "Woreda_Admin", "Period", f"{selected_vaccine}_Administered", f"{selected_vaccine}_Distributed", f"{selected_vaccine}_Utilization_Rate"]].copy()
        display_df.rename(columns={
            "Region_Admin": "Region",
            "Zone_Admin": "Zone",
            "Woreda_Admin": "Woreda",
            f"{selected_vaccine}_Administered": "Administered",
            f"{selected_vaccine}_Distributed": "Distributed",
            f"{selected_vaccine}_Utilization_Rate": "Utilization Rate"
        }, inplace=True)
        st.dataframe(display_df.sort_values(by="Utilization Rate", ascending=False).reset_index(drop=True))
        
        st.download_button(
            label="📥 Download Woreda Data as Excel",
            data=to_excel(display_df),
            file_name=f"Woreda_Utilization_Data_{selected_vaccine}_{selected_period}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
else:
    st.info("Please upload and process datasets in the main app to view this dashboard.")
