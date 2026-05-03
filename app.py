"""
app.py  —  Agricultural Land (% of Land Area) Dashboard

HOW TO RUN:
    streamlit run app.py

REQUIRES:
    data/Agricultural_land_clean.csv 
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 0.  PAGE CONFIG  —  must be the VERY FIRST Streamlit call
st.set_page_config(
    page_title="Agricultural Land Dashboard",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)


# 1.  CUSTOM CSS
st.markdown("""
<style>
    .block-container { padding-top: 1.5rem; }

    /* KPI cards */
    .kpi-card {
        background: white;
        border-radius: 10px;
        padding: 18px 16px;
        text-align: center;
        border-left: 5px solid #2E86AB;
        box-shadow: 0 2px 8px rgba(0,0,0,0.07);
    }
    .kpi-label { font-size: 13px; color: #6B7280; font-weight: 600; margin-bottom: 6px; }
    .kpi-value { font-size: 30px; font-weight: 800; color: #1F2937; }
    .kpi-sub   { font-size: 12px; color: #9CA3AF; margin-top: 4px; }

    /* Section headers */
    .sec-head {
        font-size: 17px; font-weight: 700; color: #1F4E79;
        border-bottom: 2px solid #2E86AB;
        padding-bottom: 5px; margin: 28px 0 14px 0;
    }
</style>
""", unsafe_allow_html=True)


# 2.  LOAD DATA  (cached — only reads CSV once per session)
@st.cache_data
def load_data():
    df = pd.read_csv("data/Agricultural_land_clean.csv")
    df["Year"] = df["Year"].astype(int)
    return df

df = load_data()

# Convenience constants
ALL_REGIONS   = sorted([r for r in df["Region"].unique() if r != "Other"])
ALL_COUNTRIES = sorted(df["Country"].unique())
MIN_YEAR      = int(df["Year"].min())   # 1961
MAX_YEAR      = int(df["Year"].max())   # 2023

REGION_COLORS = {
    "Africa":        "#E07B39",
    "Asia":          "#3B82C4",
    "Europe":        "#5BAD6F",
    "North America": "#9B59B6",
    "South America": "#E84393",
    "Oceania":       "#E8B84B",
    "Other":         "#95A5A6",
}


# 3.  SIDEBAR — interactive filters
with st.sidebar:
    st.title("🌾 Filters")
    st.markdown("---")

    # Year range slider 
    st.subheader("📅 Year Range")
    year_range = st.slider(
        label="year_range",
        min_value=MIN_YEAR,
        max_value=MAX_YEAR,
        value=(1990, MAX_YEAR),
        step=1,
        label_visibility="collapsed",
    )

    st.markdown("---")

    # Region multiselect 
    st.subheader("🌍 Regions")
    selected_regions = st.multiselect(
        label="regions",
        options=ALL_REGIONS,
        default=ALL_REGIONS,
        label_visibility="collapsed",
    )
    if not selected_regions:          # guard: never allow empty selection
        st.warning("Select at least one region.")
        selected_regions = ALL_REGIONS

    st.markdown("---")

    # Top-N slider 
    st.subheader("🔢 Top / Bottom N")
    top_n = st.slider(
        label="top_n",
        min_value=5,
        max_value=20,
        value=10,
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.caption(
        "**Source:** World Bank WDI\n\n"
        "**Indicator:** AG.LND.AGRI.ZS\n\n"
        "220 countries · 1961–2023"
    )


# 4.  FILTERED DATASETS
df_filtered = df[
    df["Year"].between(year_range[0], year_range[1]) &
    df["Region"].isin(selected_regions)
].copy()

latest_year = int(df_filtered["Year"].max())
df_latest   = df_filtered[df_filtered["Year"] == latest_year].copy()

# Map always shows ALL countries (not filtered by region) for context
df_map = df[df["Year"] == latest_year].copy()


# 5.  PAGE HEADER
st.markdown(
    "<h1 style='color:#1F4E79; margin-bottom:2px;'>"
    "🌾 Global Agricultural Land Dashboard</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    f"<p style='color:#6B7280; font-size:15px; margin-top:0;'>"
    f"Agricultural Land (% of Land Area) &nbsp;·&nbsp; World Bank WDI &nbsp;·&nbsp; "
    f"<b>{year_range[0]}–{year_range[1]}</b> &nbsp;·&nbsp; "
    f"Regions: <b>{', '.join(selected_regions)}</b></p>",
    unsafe_allow_html=True,
)


# 6.  KPI CARDS
st.markdown('<div class="sec-head">📊 Key Metrics</div>', unsafe_allow_html=True)

avg_val     = df_latest["Agri_Land_Pct"].mean()
n_countries = df_latest["Country"].nunique()
high_row    = df_latest.nlargest(1, "Agri_Land_Pct").iloc[0]
low_row     = df_latest.nsmallest(1, "Agri_Land_Pct").iloc[0]

c1, c2, c3, c4 = st.columns(4)

c1.markdown(f"""
<div class="kpi-card">
  <div class="kpi-label">Average Agricultural Land</div>
  <div class="kpi-value">{avg_val:.1f}%</div>
  <div class="kpi-sub">Filtered mean · {latest_year}</div>
</div>""", unsafe_allow_html=True)

c2.markdown(f"""
<div class="kpi-card" style="border-left-color:#5BAD6F;">
  <div class="kpi-label">Countries in View</div>
  <div class="kpi-value">{n_countries}</div>
  <div class="kpi-sub">Matching current filters</div>
</div>""", unsafe_allow_html=True)

c3.markdown(f"""
<div class="kpi-card" style="border-left-color:#E07B39;">
  <div class="kpi-label">🔺 Highest · {latest_year}</div>
  <div class="kpi-value">{high_row['Agri_Land_Pct']:.1f}%</div>
  <div class="kpi-sub">{high_row['Country']}</div>
</div>""", unsafe_allow_html=True)

c4.markdown(f"""
<div class="kpi-card" style="border-left-color:#9B59B6;">
  <div class="kpi-label">🔻 Lowest · {latest_year}</div>
  <div class="kpi-value">{low_row['Agri_Land_Pct']:.1f}%</div>
  <div class="kpi-sub">{low_row['Country']}</div>
</div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


# 7.  CHART 1 — CHOROPLETH WORLD MAP
st.markdown('<div class="sec-head">🗺️ World Map — Agricultural Land % by Country</div>',
            unsafe_allow_html=True)

fig_map = px.choropleth(
    df_map,
    locations="Country_Code",
    color="Agri_Land_Pct",
    hover_name="Country",
    hover_data={"Agri_Land_Pct": ":.2f", "Country_Code": False, "Region": True},
    color_continuous_scale="YlGn",
    range_color=(0, 90),
    labels={"Agri_Land_Pct": "Agri Land (%)"},
    title=f"Agricultural Land % by Country ({latest_year})",
)
fig_map.update_layout(
    geo=dict(
        showframe=False,
        showcoastlines=True,
        coastlinecolor="lightgrey",
        bgcolor="rgba(0,0,0,0)",
    ),
    coloraxis_colorbar=dict(title="% of Land Area", ticksuffix="%"),
    margin=dict(l=0, r=0, t=40, b=0),
    height=430,
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
)
st.plotly_chart(fig_map, use_container_width=True)


# 8.  CHART 2 — GLOBAL TREND LINE
st.markdown('<div class="sec-head">📈 Global Average Trend Over Time</div>',
            unsafe_allow_html=True)

trend = (
    df_filtered
    .groupby("Year")["Agri_Land_Pct"]
    .mean()
    .reset_index()
    .rename(columns={"Agri_Land_Pct": "Average (%)"})
)

fig_trend = go.Figure()
fig_trend.add_trace(go.Scatter(
    x=trend["Year"],
    y=trend["Average (%)"],
    mode="lines",
    fill="tozeroy",
    fillcolor="rgba(46,134,171,0.10)",
    line=dict(color="#2E86AB", width=2.5),
    hovertemplate="<b>%{x}</b><br>Average: %{y:.2f}%<extra></extra>",
))
fig_trend.update_layout(
    title=f"Global Average Agricultural Land % ({year_range[0]}–{year_range[1]})",
    xaxis_title="Year",
    yaxis_title="Average Agricultural Land (%)",
    yaxis_ticksuffix="%",
    height=350,
    margin=dict(l=40, r=20, t=50, b=40),
    plot_bgcolor="white",
    paper_bgcolor="rgba(0,0,0,0)",
    hovermode="x unified",
)
fig_trend.update_xaxes(showgrid=False)
fig_trend.update_yaxes(showgrid=True, gridcolor="#F0F0F0")
st.plotly_chart(fig_trend, use_container_width=True)


# 9.  CHARTS 3 & 4 — TOP/BOTTOM  +  REGIONAL BOX PLOT  (side by side)
col_left, col_right = st.columns(2)

# Chart 3: Top N / Bottom N bar chart 
with col_left:
    st.markdown('<div class="sec-head">🏆 Top & Bottom Countries</div>',
                unsafe_allow_html=True)

    view = st.radio(
        "Show",
        options=["Top Countries", "Bottom Countries"],
        horizontal=True,
        key="top_bottom_radio",
    )

    if view == "Top Countries":
        bar_data = df_latest.nlargest(top_n, "Agri_Land_Pct").sort_values("Agri_Land_Pct")
        bar_color = "#E07B39"
        bar_title = f"Top {top_n} Countries — Highest Agricultural Land % ({latest_year})"
    else:
        bar_data = df_latest.nsmallest(top_n, "Agri_Land_Pct").sort_values("Agri_Land_Pct", ascending=False)
        bar_color = "#3B82C4"
        bar_title = f"Bottom {top_n} Countries — Lowest Agricultural Land % ({latest_year})"

    fig_bar = px.bar(
        bar_data,
        x="Agri_Land_Pct",
        y="Country",
        orientation="h",
        color="Agri_Land_Pct",
        color_continuous_scale=["#D6EAF8", bar_color],
        labels={"Agri_Land_Pct": "Agricultural Land (%)"},
        title=bar_title,
        text=bar_data["Agri_Land_Pct"].round(1).astype(str) + "%",
    )
    fig_bar.update_traces(textposition="outside")
    fig_bar.update_layout(
        height=420,
        showlegend=False,
        coloraxis_showscale=False,
        xaxis_ticksuffix="%",
        margin=dict(l=10, r=60, t=50, b=30),
        plot_bgcolor="white",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    fig_bar.update_xaxes(showgrid=True, gridcolor="#F0F0F0")
    fig_bar.update_yaxes(showgrid=False)
    st.plotly_chart(fig_bar, use_container_width=True)

# Chart 4: Regional box plot 
with col_right:
    st.markdown('<div class="sec-head">🌍 Regional Distribution</div>',
                unsafe_allow_html=True)

    df_box = df_filtered[df_filtered["Region"] != "Other"]
    fig_box = px.box(
        df_box,
        x="Region",
        y="Agri_Land_Pct",
        color="Region",
        color_discrete_map=REGION_COLORS,
        labels={"Agri_Land_Pct": "Agricultural Land (%)"},
        title=f"Distribution of Agricultural Land % by Region ({year_range[0]}–{year_range[1]})",
        points="outliers",
    )
    fig_box.update_layout(
        height=420,
        showlegend=False,
        yaxis_ticksuffix="%",
        xaxis_title="",
        margin=dict(l=10, r=10, t=50, b=30),
        plot_bgcolor="white",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    fig_box.update_yaxes(showgrid=True, gridcolor="#F0F0F0")
    st.plotly_chart(fig_box, use_container_width=True)


# 10. CHART 5 — COUNTRY DEEP DIVE
st.markdown('<div class="sec-head">🔍 Country Deep Dive</div>', unsafe_allow_html=True)

selected_country = st.selectbox(
    "Select a country to explore its full historical trend:",
    options=ALL_COUNTRIES,
    index=ALL_COUNTRIES.index("India"),   # default: India
)

df_country = df[df["Country"] == selected_country].sort_values("Year")

# Key stats for the selected country
latest_val  = df_country[df_country["Year"] == df_country["Year"].max()]["Agri_Land_Pct"].values[0]
earliest_val = df_country[df_country["Year"] == df_country["Year"].min()]["Agri_Land_Pct"].values[0]
change_total = latest_val - earliest_val
avg_yoy = df_country["YoY_Change"].mean()

m1, m2, m3, m4 = st.columns(4)
m1.metric("Latest Value",    f"{latest_val:.2f}%",  f"{change_total:+.2f}pp since {df_country['Year'].min()}")
m2.metric("Earliest Value",  f"{earliest_val:.2f}%", f"{df_country['Year'].min()}")
m3.metric("Total Change",    f"{change_total:+.2f}pp", "over full period")
m4.metric("Avg YoY Change",  f"{avg_yoy:+.3f}pp",   "per year average")

fig_country = go.Figure()
fig_country.add_trace(go.Scatter(
    x=df_country["Year"],
    y=df_country["Agri_Land_Pct"],
    mode="lines+markers",
    fill="tozeroy",
    fillcolor="rgba(46,134,171,0.10)",
    line=dict(color="#2E86AB", width=2.5),
    marker=dict(size=4, color="#2E86AB"),
    hovertemplate="<b>%{x}</b><br>%{y:.2f}%<extra></extra>",
    name=selected_country,
))
fig_country.update_layout(
    title=f"Agricultural Land % — {selected_country} (Full History)",
    xaxis_title="Year",
    yaxis_title="Agricultural Land (%)",
    yaxis_ticksuffix="%",
    height=360,
    margin=dict(l=40, r=20, t=50, b=40),
    plot_bgcolor="white",
    paper_bgcolor="rgba(0,0,0,0)",
    hovermode="x unified",
)
fig_country.update_xaxes(showgrid=False)
fig_country.update_yaxes(showgrid=True, gridcolor="#F0F0F0")
st.plotly_chart(fig_country, use_container_width=True)


# 11. CHART 6 — MULTI-COUNTRY COMPARISON
st.markdown('<div class="sec-head">⚖️ Compare Countries</div>', unsafe_allow_html=True)

default_compare = ["India", "China", "Brazil", "United Kingdom", "Australia"]
compare_countries = st.multiselect(
    "Select 2 or more countries to compare their trends:",
    options=ALL_COUNTRIES,
    default=default_compare,
)

if len(compare_countries) < 2:
    st.info("Please select at least 2 countries to compare.")
else:
    df_compare = df[df["Country"].isin(compare_countries)].sort_values("Year")
    fig_compare = px.line(
        df_compare,
        x="Year",
        y="Agri_Land_Pct",
        color="Country",
        labels={"Agri_Land_Pct": "Agricultural Land (%)", "Country": "Country"},
        title=f"Agricultural Land % Comparison ({MIN_YEAR}–{MAX_YEAR})",
        hover_data={"Agri_Land_Pct": ":.2f"},
    )
    fig_compare.update_layout(
        height=380,
        yaxis_ticksuffix="%",
        margin=dict(l=40, r=20, t=50, b=40),
        plot_bgcolor="white",
        paper_bgcolor="rgba(0,0,0,0)",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    fig_compare.update_xaxes(showgrid=False)
    fig_compare.update_yaxes(showgrid=True, gridcolor="#F0F0F0")
    st.plotly_chart(fig_compare, use_container_width=True)


# 12. DATA TABLE (expandable)
st.markdown('<div class="sec-head">📋 Raw Data Explorer</div>', unsafe_allow_html=True)

with st.expander(f"Click to view filtered data table ({len(df_filtered):,} rows)"):
    st.dataframe(
        df_filtered[["Country", "Country_Code", "Region", "Year", "Agri_Land_Pct", "YoY_Change"]]
        .sort_values(["Country", "Year"])
        .style.format({"Agri_Land_Pct": "{:.2f}%", "YoY_Change": "{:+.3f}"}),
        use_container_width=True,
        height=350,
    )
    st.download_button(
        label="⬇️ Download filtered data as CSV",
        data=df_filtered.to_csv(index=False).encode("utf-8"),
        file_name=f"agri_land_{year_range[0]}_{year_range[1]}.csv",
        mime="text/csv",
    )


# 13. FOOTER
st.markdown("---")
st.markdown(
    "<p style='text-align:center; color:#9CA3AF; font-size:13px;'>"
    "Data: World Bank World Development Indicators (WDI) · "
    "Indicator: AG.LND.AGRI.ZS · "
    "Agricultural land includes arable land, permanent crops, and permanent pastures."
    "</p>",
    unsafe_allow_html=True,
)
