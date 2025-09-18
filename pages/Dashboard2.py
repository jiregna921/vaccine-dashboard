import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO

# --- Custom CSS for enhanced styling ---
st.markdown("""
<style>
/* Overall page layout and styling */
.stApp {
    /* ENHANCED: A clean, professional background color */
    background-color: #f0f2f6; 
    color: #2c3e50;
    min-height: 100vh;
}

/* Header styling - More impactful */
.main-header-container {
    background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
    padding: 2rem;
    border-radius: 16px;
    margin-bottom: 2rem;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
    text-align: center;
    border: 1px solid rgba(255, 255, 255, 0.1);
}

.main-header-container h1 {
    color: white;
    margin: 0;
    font-size: 2.5rem;
    font-weight: 700;
    letter-spacing: 0.5px;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
}

/* ENHANCED: Metric cards with accent border and better hierarchy */
.custom-metric-box {
    background-color: #ffffff;
    padding: 1.5rem;
    border-radius: 16px;
    text-align: center;
    margin-bottom: 1.5rem;
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.07);
    border: 1px solid #e0e0e0;
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
}

/* Adds a colorful accent bar to the left of the card */
.custom-metric-box::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 5px;
    height: 100%;
    background: linear-gradient(180deg, #3498db 0%, #2980b9 100%);
}

.custom-metric-box:hover {
    transform: translateY(-5px);
    box-shadow: 0 12px 30px rgba(0, 0, 0, 0.12);
}

.custom-metric-label {
    font-size: 0.9rem;
    font-weight: 600;
    color: #7f8c8d;
    margin-bottom: 0.5rem;
    text-transform: uppercase;
    letter-spacing: 1px;
}

.custom-metric-value {
    font-size: 2.2rem;
    font-weight: 700;
    color: #2c3e50;
}

/* Section headers for better page structure */
.section-header {
    background: #ffffff;
    padding: 1rem 1.5rem;
    border-radius: 16px;
    margin: 2.5rem 0 1.5rem 0;
    color: #2c3e50 !important;
    text-align: left;
    border-left: 5px solid #3498db;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06);
}

.section-header h3 {
    color: #2c3e50 !important;
    margin: 0;
    font-weight: 600;
    font-size: 1.6rem;
}

/* ENHANCED: Chart containers for a polished look */
.js-plotly-plot {
    border-radius: 16px;
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.07);
    background: white;
    padding: 1rem;
    border: 1px solid #e0e0e0;
}

/* ENHANCED: Clearer, more professional warning and info messages */
.stWarning {
    background-color: #fff3cd !important;
    border: 1px solid #ffeeba !important;
    border-left: 5px solid #ffc107 !important;
    border-radius: 8px !important;
    color: #856404 !important;
    padding: 1rem !important;
}

.stInfo {
    background-color: #eaf5ff !important;
    border: 1px solid #b8d9f7 !important;
    border-left: 5px solid #3498db !important;
    border-radius: 8px !important;
    color: #0c5460 !important;
    padding: 1rem !important;
}

/* ENHANCED: Sidebar styling */
.stSidebar {
    background: #ffffff !important;
    border-right: 1px solid #e0e0e0;
    box-shadow: 2px 0 15px rgba(0, 0, 0, 0.05);
}

.stSidebar .stHeader {
    color: #2c3e50 !important;
    font-weight: 600;
    border-bottom: 2px solid #3498db;
    padding-bottom: 0.5rem;
    font-size: 1.4rem;
    margin-bottom: 1rem;
}

/* ENHANCED: Buttons with better visual feedback */
.stDownloadButton button {
    background: linear-gradient(135deg, #3498db 0%, #2980b9 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.75rem 1.5rem !important;
    font-weight: 600 !important;
    box-shadow: 0 4px 12px rgba(52, 152, 219, 0.2);
    transition: all 0.3s ease;
}

.stDownloadButton button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 18px rgba(52, 152, 219, 0.3);
}

/* ENHANCED: Logo container for better integration */
.logo-container {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100%;
    background-color: #ffffff;
    padding: 1rem;
    border-radius: 16px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.07);
    border: 1px solid #e0e0e0;
}

/* Divider styling */
hr {
    margin: 2.5rem 0;
    border: none;
    height: 1px;
    background: linear-gradient(90deg, transparent, #bdc3c7, transparent);
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
    """Calculates high and low extremity counts based on defined thresholds."""
    rate_col = f"{vaccine}_Utilization_Rate"
    if rate_col not in df.columns:
        return None
    
    thresholds = {
        "BCG": {"high": 1.20, "low": 0.30}, "IPV": {"high": 1.30, "low": 0.75},
        "Measles": {"high": 1.25, "low": 0.50}, "Penta": {"high": 1.30, "low": 0.80},
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
        <h1>📊 Vaccine Utilization & Discrepancy Analysis</h1>
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
    
    required_cols = ["Region_Admin", "Zone_Admin", "Woreda_Admin", "Period"]
    if not all(col in df_all.columns for col in required_cols):
        st.error("Essential columns (Region, Zone, Woreda, Period) are missing.")
        st.stop()
    
    # --- Prepare data for calculation ---
    vaccines = ["BCG", "IPV", "Measles", "Penta", "Rota"]
    for vaccine in vaccines:
        admin_col = f"{vaccine}_Administered"
        dist_col = f"{vaccine}_Distributed"
        rate_col = f"{vaccine}_Utilization_Rate"
        if admin_col in df_all.columns and dist_col in df_all.columns:
            df_all[rate_col] = df_all.apply(
                lambda row: (row[admin_col] / row[dist_col]) * 100 if row[dist_col] > 0 else 0,
                axis=1
            )
            df_all[rate_col] = df_all[rate_col].clip(0, 1000)

    # --- Sidebar filters ---
    st.sidebar.header("🧪 Filter Data")
    
    regions = sorted(df_all["Region_Admin"].unique())
    selected_region = st.sidebar.selectbox("Select Region", ["All"] + regions)
    
    filtered_zones = df_all[df_all["Region_Admin"] == selected_region]["Zone_Admin"].unique() if selected_region != "All" else df_all["Zone_Admin"].unique()
    zones = sorted(filtered_zones)
    selected_zone = st.sidebar.selectbox("Select Zone", ["All"] + zones)
    
    if selected_zone != "All":
        filtered_woredas = df_all[(df_all["Region_Admin"] == selected_region) & (df_all["Zone_Admin"] == selected_zone)]["Woreda_Admin"].unique()
    elif selected_region != "All":
        filtered_woredas = df_all[df_all["Region_Admin"] == selected_region]["Woreda_Admin"].unique()
    else:
        filtered_woredas = df_all["Woreda_Admin"].unique()
    woredas = sorted(filtered_woredas)
    selected_woreda = st.sidebar.selectbox("Select Woreda", ["All"] + woredas)

    periods = sorted(df_all["Period"].unique())
    selected_period = st.sidebar.selectbox("Select Period", ["All"] + periods)
    
    selected_vaccine = st.sidebar.selectbox("Select Vaccine", ["All"] + vaccines)
    
    # --- Filtering Logic ---
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

    # --- Scorecards ---
    total_woredas = filtered_df["Woreda_Admin"].nunique()
    
    if selected_vaccine != "All":
        dist_col = f"{selected_vaccine}_Distributed"
        admin_col = f"{selected_vaccine}_Administered"
        if dist_col in filtered_df.columns and admin_col in filtered_df.columns:
            total_dist = filtered_df[dist_col].sum()
            total_admin = filtered_df[admin_col].sum()
        else:
            st.warning(f"Data for '{selected_vaccine}' is not available.")
            st.stop()
    else:
        existing_dist_cols = [f"{v}_Distributed" for v in vaccines if f"{v}_Distributed" in filtered_df.columns]
        existing_admin_cols = [f"{v}_Administered" for v in vaccines if f"{v}_Administered" in filtered_df.columns]
        total_dist = filtered_df[existing_dist_cols].sum().sum()
        total_admin = filtered_df[existing_admin_cols].sum().sum()
    
    utilization_rate = (total_admin / total_dist) * 100 if total_dist > 0 else 0
    
    st.markdown('<div class="section-header"><h3>📊 Performance Overview</h3></div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f'<div class="custom-metric-box"><div class="custom-metric-label">Total Woredas</div><div class="custom-metric-value">{total_woredas}</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="custom-metric-box"><div class="custom-metric-label">Doses Distributed</div><div class="custom-metric-value">{int(total_dist):,}</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="custom-metric-box"><div class="custom-metric-label">Doses Administered</div><div class="custom-metric-value">{int(total_admin):,}</div></div>', unsafe_allow_html=True)
    with col4:
        st.markdown(f'<div class="custom-metric-box"><div class="custom-metric-label">Utilization Rate</div><div class="custom-metric-value">{utilization_rate:.1f}%</div></div>', unsafe_allow_html=True)

    # --- Extremities Count ---
    st.markdown('<div class="section-header"><h3>🚨 Extreme Utilization Rates (Woredas Count)</h3></div>', unsafe_allow_html=True)
    counts_cols = st.columns(len(vaccines))
    
    for i, vaccine in enumerate(vaccines):
        counts = count_extremity(filtered_df, vaccine)
        if counts:
            with counts_cols[i]:
                st.markdown(f'<div class="custom-metric-box" style="text-align: center;"><div class="custom-metric-label">{vaccine}</div><span style="font-size: 1.2rem; color: #e74c3c; font-weight: bold;">▲ {counts[0]} High</span><br><span style="font-size: 1.2rem; color: #f39c12; font-weight: bold;">▼ {counts[1]} Low</span></div>', unsafe_allow_html=True)

    # --- Table for Extreme Utilization ---
    st.markdown('<div class="section-header"><h3>📋 Extreme Utilization by Location</h3></div>', unsafe_allow_html=True)
    if selected_vaccine == "All":
        st.info("ℹ️ Please select a specific vaccine from the sidebar to view this summary table.")
    else:
        rate_col = f"{selected_vaccine}_Utilization_Rate"
        if rate_col not in filtered_df.columns:
            st.warning(f"Utilization data for {selected_vaccine} is not available.")
        else:
            thresholds = {
                "BCG": {"high": 1.20, "low": 0.30}, "IPV": {"high": 1.30, "low": 0.75},
                "Measles": {"high": 1.25, "low": 0.50}, "Penta": {"high": 1.30, "low": 0.80},
                "Rota": {"high": 1.30, "low": 0.75},
            }
            
            extreme_df = filtered_df.copy()
            group_cols = ["Region_Admin"] if selected_region == "All" else ["Region_Admin", "Zone_Admin"]
            
            extreme_df["High_Extremity"] = extreme_df[rate_col] / 100 > thresholds[selected_vaccine]["high"]
            extreme_df["Low_Extremity"] = extreme_df[rate_col] / 100 < thresholds[selected_vaccine]["low"]

            extreme_summary = extreme_df.groupby(group_cols).agg(
                total_woredas=("Woreda_Admin", "nunique"),
                high_extremity_count=("High_Extremity", "sum"),
                low_extremity_count=("Low_Extremity", "sum")
            ).reset_index()
            
            extreme_summary.rename(columns={
                "Region_Admin": "Region", "Zone_Admin": "Zone",
                "total_woredas": "Total Woredas", "high_extremity_count": "High Extremity Count",
                "low_extremity_count": "Low Extremity Count",
            }, inplace=True)
            
            st.dataframe(extreme_summary, use_container_width=True, hide_index=True)
            
            st.download_button(
                label="📥 Download Summary as Excel",
                data=to_excel(extreme_summary),
                file_name=f"Extreme_Utilization_{selected_vaccine}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
    
    # --- Utilization Rate by Woreda Scatter Plot ---
    st.markdown('<div class="section-header"><h3>📈 Utilization Rate by Woreda</h3></div>', unsafe_allow_html=True)
    if selected_vaccine == "All":
        st.info("ℹ️ Please select a specific vaccine to view the utilization rate plot.")
    else:
        rate_col = f"{selected_vaccine}_Utilization_Rate"
        if rate_col not in filtered_df.columns:
            st.warning(f"Utilization data for {selected_vaccine} is not available.")
        else:
            fig = px.scatter(
                filtered_df, x="Woreda_Admin", y=rate_col,
                title=f"<b>{selected_vaccine} Utilization Rate by Woreda</b>",
                labels={"Woreda_Admin": "Woreda", rate_col: "Utilization Rate (%)"},
                color_discrete_sequence=["#3498db"]
            )
            
            thresholds_plot = {
                "BCG": {"high": 120, "low": 30}, "IPV": {"high": 130, "low": 75},
                "Measles": {"high": 125, "low": 50}, "Penta": {"high": 130, "low": 80},
                "Rota": {"high": 130, "low": 75},
            }
            
            if selected_vaccine in thresholds_plot:
                fig.add_hline(y=thresholds_plot[selected_vaccine]["high"], line_dash="dash", line_color="#e74c3c", annotation_text="High Threshold")
                fig.add_hline(y=thresholds_plot[selected_vaccine]["low"], line_dash="dash", line_color="#f39c12", annotation_text="Low Threshold")
            
            # ENHANCED: Updated layout for better readability and contrast
            fig.update_layout(
                xaxis_title="<b>Woreda</b>", 
                yaxis_title="<b>Utilization Rate (%)</b>", 
                xaxis_tickangle=-45,
                plot_bgcolor='white',
                paper_bgcolor='white',
                font=dict(color='#2c3e50', size=12),
                title=dict(x=0.5, font=dict(size=20)), # Center title
                hoverlabel=dict(bgcolor="white", font_size=12)
            )
            fig.update_xaxes(showgrid=False, tickfont=dict(size=10))
            fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#f0f0f0') # Subtle gridlines
            
            st.plotly_chart(fig, use_container_width=True)

    # --- Unmatched Records ---
    st.markdown('<div class="section-header"><h3>🔍 Unmatched Records</h3></div>', unsafe_allow_html=True)
    unmatched_col1, unmatched_col2 = st.columns(2)
    with unmatched_col1:
        st.write("<h5>Unmatched Administered Records</h5>", unsafe_allow_html=True)
        if "unmatched_admin_df" in st.session_state and not st.session_state["unmatched_admin_df"].empty:
            st.dataframe(st.session_state["unmatched_admin_df"], use_container_width=True, height=300)
        else:
            st.info("✅ No unmatched administered records found.")
    
    with unmatched_col2:
        st.write("<h5>Unmatched Distributed Records</h5>", unsafe_allow_html=True)
        if "unmatched_dist_df" in st.session_state and not st.session_state["unmatched_dist_df"].empty:
            st.dataframe(st.session_state["unmatched_dist_df"], use_container_width=True, height=300)
        else:
            st.info("✅ No unmatched distributed records found.")
    
    # --- Download Report Section ---
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown('<div class="section-header"><h3>📄 Download Center</h3></div>', unsafe_allow_html=True)
    
    # This part for PPT creation can be added if needed, but it's removed for brevity as the focus was on layout
    # For now, a placeholder download for the main filtered data
    st.download_button(
        label="📊 Download Filtered Data as Excel",
        data=to_excel(filtered_df),
        file_name="filtered_vaccine_data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )

else:
    st.info("ℹ️ Please upload and process data on the Data Upload page to view this dashboard.")
