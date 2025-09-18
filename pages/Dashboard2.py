import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
from config.thresholds import VACCINE_THRESHOLDS

# =======================
# Page Config & Styling
# =======================
st.set_page_config(page_title="Immunization Data Dashboard", layout="wide")

st.markdown("""
    <style>
        body, .main, .block-container, .stApp {
            background-color: #ffffff !important;
            color: #000000 !important;
        }
        .css-1d391kg, .css-18e3th9, .css-1v0mbdj, .css-1lcbmhc { 
            background-color: #ffffff !important;
            color: #000000 !important;
        }
        .title-text { font-size: 36px; font-weight: bold; color: #000000; text-align: center; }
        .section-header { font-size: 24px; font-weight: bold; color: #000000; margin-top: 20px; }
        .highlight-box { background-color: #f2f2f2; padding: 15px; border-radius: 10px; margin-bottom: 10px; }
        .metric-title { font-size: 18px; font-weight: bold; color: #000000; }
        .metric-value { font-size: 22px; font-weight: bold; color: #000000; }
        .stDataFrame { background-color: #ffffff !important; color: #000000 !important; }
    </style>
""", unsafe_allow_html=True)

# =======================
# Helper Functions
# =======================
def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name="Sheet1")
    return output.getvalue()

def filter_data(df, region, zone, woreda, period):
    if region != "All":
        df = df[df['Region'] == region]
    if zone != "All":
        df = df[df['Zone'] == zone]
    if woreda != "All":
        df = df[df['Woreda'] == woreda]
    if period != "All":
        df = df[df['Period'] == period]
    return df

def count_extremes(df):
    results = {}
    for vac, thr in VACCINE_THRESHOLDS.items():
        col = f"{vac}_UsageRate"
        if col in df:
            over = df[df[col] > thr['high']].shape[0]
            under = df[df[col] < thr['low']].shape[0]
            results[vac] = {"Over-Utilization": over, "Under-Utilization": under}
    return results

def create_scatter(df, vac, thresholds):
    col = f"{vac}_UsageRate"
    if col not in df: return None

    fig = px.scatter(
        df, x="Distributed", y="Administered", color=col,
        hover_data=["Region", "Zone", "Woreda"],
        title=f"{vac} Usage Rate Distribution"
    )

    # Style improvements
    fig.update_layout(
        plot_bgcolor="#ffffff",
        paper_bgcolor="#ffffff",
        font=dict(color="#000000", size=14),
        title_font=dict(size=20, color="#000000"),
        xaxis=dict(gridcolor="lightgrey", color="#000000"),
        yaxis=dict(gridcolor="lightgrey", color="#000000"),
        legend=dict(bgcolor="#ffffff", bordercolor="lightgrey", borderwidth=1, font=dict(color="#000000"))
    )

    # Threshold lines
    x_max = df['Distributed'].max()
    fig.add_trace(go.Scatter(
        x=[0, x_max], y=[0, thresholds['high']*x_max],
        mode="lines", name="High Threshold",
        line=dict(color="red", dash="dash")
    ))
    fig.add_trace(go.Scatter(
        x=[0, x_max], y=[0, thresholds['low']*x_max],
        mode="lines", name="Low Threshold",
        line=dict(color="blue", dash="dash")
    ))
    return fig

# =======================
# Sidebar Filters
# =======================
st.sidebar.header("Filters")
df = pd.DataFrame({})  # Replace with actual loaded data

region = st.sidebar.selectbox("Select Region", ["All"] + df['Region'].unique().tolist()) if 'Region' in df else "All"
zone = st.sidebar.selectbox("Select Zone", ["All"] + df['Zone'].unique().tolist()) if 'Zone' in df else "All"
woreda = st.sidebar.selectbox("Select Woreda", ["All"] + df['Woreda'].unique().tolist()) if 'Woreda' in df else "All"
period = st.sidebar.selectbox("Select Period", ["All"] + df['Period'].unique().tolist()) if 'Period' in df else "All"

filtered_df = filter_data(df, region, zone, woreda, period)

# =======================
# Dashboard Layout
# =======================
st.markdown("<div class='title-text'>Immunization Data Dashboard</div>", unsafe_allow_html=True)

# KPI Section
if not filtered_df.empty:
    total_woredas = filtered_df["Woreda"].nunique()
    total_records = len(filtered_df)
    extremes = count_extremes(filtered_df)
    total_over = sum([v["Over-Utilization"] for v in extremes.values()])
    total_under = sum([v["Under-Utilization"] for v in extremes.values()])

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Woredas", total_woredas)
    col2.metric("Total Records", total_records)
    col3.metric("Over-Utilized", total_over)
    col4.metric("Under-Utilized", total_under)

# Tabs for sections
tab1, tab2, tab3, tab4 = st.tabs(["Performance", "Extremes", "Charts", "Unmatched Records"])

# --- Performance ---
with tab1:
    st.markdown("<div class='section-header'>Performance Metrics</div>", unsafe_allow_html=True)
    if not filtered_df.empty:
        st.dataframe(filtered_df.style.set_properties(**{'background-color': 'white','color': 'black'}))
        st.download_button("Download Performance Data", to_excel(filtered_df), "performance.xlsx")
    else:
        st.info("No data available for current filter.")

# --- Extremes ---
with tab2:
    st.markdown("<div class='section-header'>Utilization Extremes</div>", unsafe_allow_html=True)
    if extremes:
        extreme_df = pd.DataFrame.from_dict(extremes, orient='index')
        st.dataframe(extreme_df.style.set_properties(**{'background-color': 'white','color': 'black'}))
        st.download_button("Download Extremes", to_excel(extreme_df), "extremes.xlsx")
    else:
        st.info("No extremes data available.")

# --- Charts ---
with tab3:
    st.markdown("<div class='section-header'>Usage Charts</div>", unsafe_allow_html=True)
    for vac, thr in VACCINE_THRESHOLDS.items():
        fig = create_scatter(filtered_df, vac, thr)
        if fig: st.plotly_chart(fig, use_container_width=True)

# --- Unmatched Records ---
with tab4:
    st.markdown("<div class='section-header'>Unmatched Records</div>", unsafe_allow_html=True)
    if not filtered_df.empty:
        unmatched = filtered_df[(filtered_df['Distributed'] == 0) & (filtered_df['Administered'] > 0)]
        if not unmatched.empty:
            st.warning("⚠️ Some records have Distributed = 0 but Administered > 0")
            st.dataframe(unmatched.style.set_properties(**{'background-color': 'white','color': 'black'}))
            st.download_button("Download Unmatched Records", to_excel(unmatched), "unmatched_records.xlsx")
        else:
            st.info("No unmatched records found.")
    else:
        st.info("No data available for current filter.")
