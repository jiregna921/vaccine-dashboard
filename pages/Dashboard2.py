# immunization_dashboard.py
import streamlit as st
import pandas as pd
import plotly.express as px
from pptx import Presentation
from io import BytesIO

# ---------------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------------
st.set_page_config(
    page_title="Vaccine Utilization Analytics Dashboard",
    layout="wide",
    page_icon="💉"
)

# ---------------------------------------------------------------------
# Helper functions (modularized)
# ---------------------------------------------------------------------
def to_excel(df: pd.DataFrame) -> bytes:
    out = BytesIO()
    with pd.ExcelWriter(out, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Sheet1")
    return out.getvalue()


def compute_utilization_rates(df: pd.DataFrame, vaccines):
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
    return selected_region, selected_zone, selected_woreda, selected_period, selected_vaccine


def apply_filters(df: pd.DataFrame, selected_region, selected_zone, selected_woreda, selected_period):
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
    total_woredas = filtered_df["Woreda_Admin"].nunique()

    dist_cols = [f"{v}_Distributed" for v in vaccines]
    admin_cols = [f"{v}_Administered" for v in vaccines]

    if selected_vaccine != "All":
        dist_col = f"{selected_vaccine}_Distributed"
        admin_col = f"{selected_vaccine}_Administered"
        total_admin = filtered_df[admin_col].sum()
        total_dist = filtered_df[dist_col].sum()
    else:
        total_dist = filtered_df[dist_cols].sum().sum()
        total_admin = filtered_df[admin_cols].sum().sum()

    utilization_rate = (total_admin / total_dist) * 100 if total_dist > 0 else 0

    st.markdown("---")
    st.markdown("### 📊 Performance Overview")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Woredas", total_woredas)
    col2.metric("Total Doses Distributed", f"{int(total_dist):,}")
    col3.metric("Total Doses Administered", f"{int(total_admin):,}")
    col4.metric("Utilization Rate", f"{utilization_rate:.2f}%")


def render_extremities_counts(filtered_df: pd.DataFrame, vaccines):
    st.markdown("### 🚨 Extreme Utilization Rates")
    counts_cols = st.columns(len(vaccines))
    for i, vaccine in enumerate(vaccines):
        counts = count_extremity(filtered_df, vaccine)
        if counts:
            counts_cols[i].metric(f"{vaccine}", f"{counts[0]}↑ | {counts[1]}↓")
    st.markdown("---")


def render_extremes_table(filtered_df: pd.DataFrame, selected_vaccine, selected_region):
    st.markdown("### 📋 Extreme Utilization by Region and Zone")
    if selected_vaccine == "All":
        st.info("Please select a specific vaccine to view this table.")
        return

    rate_col = f"{selected_vaccine}_Utilization_Rate"
    thresholds = {
        "BCG": {"high": 1.20, "low": 0.30},
        "IPV": {"high": 1.30, "low": 0.75},
        "Measles": {"high": 1.25, "low": 0.50},
        "Penta": {"high": 1.30, "low": 0.80},
        "Rota": {"high": 1.30, "low": 0.75},
    }

    extreme_df = filtered_df.copy()
    extreme_df["High_Extremity"] = extreme_df[rate_col] / 100 > thresholds[selected_vaccine]["high"]
    extreme_df["Low_Extremity"] = extreme_df[rate_col] / 100 < thresholds[selected_vaccine]["low"]

    group_cols = ["Region_Admin"] if selected_region == "All" else ["Region_Admin", "Zone_Admin"]
    extreme_summary = extreme_df.groupby(group_cols).agg(
        total_woredas=("Woreda_Admin", "nunique"),
        high_extremity_count=("High_Extremity", "sum"),
        low_extremity_count=("Low_Extremity", "sum")
    ).reset_index()

    extreme_summary.rename(columns={"Region_Admin": "Region", "Zone_Admin": "Zone"}, inplace=True)
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
    st.markdown("### 📈 Utilization Rate by Woreda")
    if selected_vaccine == "All":
        st.info("Please select a specific vaccine to view utilization rate plots.")
        return

    rate_col = f"{selected_vaccine}_Utilization_Rate"
    fig = px.scatter(filtered_df, x="Woreda_Admin", y=rate_col, title=f"{selected_vaccine} Utilization Rate by Woreda")
    st.plotly_chart(fig, use_container_width=True)


def render_unmatched_sections():
    st.markdown("### 🔍 Unmatched Records")
    unmatched_col1, unmatched_col2 = st.columns(2)
    with unmatched_col1:
        st.write("**Unmatched Administered Records**")
        if "unmatched_admin_df" in st.session_state:
            st.dataframe(st.session_state["unmatched_admin_df"])
    with unmatched_col2:
        st.write("**Unmatched Distributed Records**")
        if "unmatched_dist_df" in st.session_state:
            st.dataframe(st.session_state["unmatched_dist_df"])
    st.markdown("---")


def create_ppt(filtered_df: pd.DataFrame, selected_vaccine: str) -> BytesIO:
    prs = Presentation()
    slide = prs.slides.add_slide(prs.slide_layouts[0])
    slide.shapes.title.text = "Immunization Triangulation Report"
    slide.placeholders[1].text = f"Report generated for {selected_vaccine}."
    buf = BytesIO()
    prs.save(buf)
    buf.seek(0)
    return buf


# ---------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------
def main():
    st.markdown("## 📊 Vaccine Discrepancies and Utilization Analysis")

    if st.session_state.get("matched_df") is None:
        st.info("Please upload and process data to view this dashboard.")
        st.stop()

    df_all = st.session_state["matched_df"].copy()
    vaccines = ["BCG", "IPV", "Measles", "Penta", "Rota"]

    df_all = compute_utilization_rates(df_all, vaccines)

    selected_region, selected_zone, selected_woreda, selected_period, selected_vaccine = render_sidebar_filters(df_all, vaccines)
    filtered_df = apply_filters(df_all, selected_region, selected_zone, selected_woreda, selected_period)

    if filtered_df.empty:
        st.warning("⚠️ No data found for the selected filters.")
        st.stop()

    render_scorecards(filtered_df, vaccines, selected_vaccine)
    render_extremities_counts(filtered_df, vaccines)
    render_extremes_table(filtered_df, selected_vaccine, selected_region)
    render_utilization_scatter(filtered_df, selected_vaccine)
    render_unmatched_sections()

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
