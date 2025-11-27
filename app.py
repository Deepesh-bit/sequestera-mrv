import streamlit as st
import pandas as pd
import os

st.set_page_config(
    page_title="Sequestera MRV Dashboard",
    layout="wide"
)

st.title("Sequestera MRV")
st.caption("AI that verifies the world's climate promises.")

CSV_FILE = "climate_impact_report.csv"

if not os.path.exists(CSV_FILE):
    st.error("Run baseline_forest.py to generate climate_impact_report.csv.")
else:
    df = pd.read_csv(CSV_FILE)

    total_forest_loss = df["Forest Loss (ha)"].sum()
    total_co2_loss = df["CO2e Lost (tCO2e)"].sum()
    total_carbon_loss = df["Carbon Lost (tC)"].sum()

    worst_row = df.loc[df["CO2e Lost (tCO2e)"].idxmax()]
    worst_year = int(worst_row["Year"])
    worst_year_co2 = worst_row["CO2e Lost (tCO2e)"]

    tab_overview, tab_forest, tab_carbon, tab_map, tab_data = st.tabs(
    ["🌍 Overview", "🌳 Forest Loss", "🔥 Carbon & CO₂", "🗺 Map", "📄 Raw Data"]
)


    with tab_overview:
        with tab_overview:
         st.subheader("Project Summary")

    col1, col2 = st.columns([1, 2])

    # Read Sequestera Confidence Score
    try:
        with open("score.txt", "r") as f:
            scs = float(f.read().strip())
    except:
        scs = None

    if scs is not None:
        if scs >= 70:
            color = "green"
            rating = "High Confidence"
        elif scs >= 50:
            color = "orange"
            rating = "Moderate Confidence"
        else:
            color = "red"
            rating = "Low Confidence"

        col1.markdown(f"""
        <div style="padding:20px; border-radius:15px; background-color:{color}; color:white; text-align:center;">
            <h2>Sequestera Confidence Score</h2>
            <h1>{scs:.2f} / 100</h1>
            <p>{rating}</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        col1.error("No score data available.")

    total_forest_loss = df["Forest Loss (ha)"].sum()
    total_co2_loss = df["CO2e Lost (tCO2e)"].sum()
    worst_row = df.loc[df["CO2e Lost (tCO2e)"].idxmax()]
    worst_year = int(worst_row["Year"])
    worst_year_co2 = worst_row["CO2e Lost (tCO2e)"]

    col2.metric("Total Forest Lost (ha)", f"{total_forest_loss:,.2f}")
    col2.metric("Total CO₂e Emitted (tCO₂e)", f"{total_co2_loss:,.2f}")
    col2.metric("Worst Year", worst_year)


    with tab_forest:
        st.subheader("Annual Forest Loss (ha)")
        st.bar_chart(df.set_index("Year")["Forest Loss (ha)"])

    with tab_carbon:
        st.subheader("Carbon & CO₂e Emissions Over Time")
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**CO₂e Emissions (tCO₂e)**")
            st.line_chart(df.set_index("Year")["CO2e Lost (tCO2e)"])

        with col2:
            st.markdown("**Carbon Loss (tC)**")
            st.line_chart(df.set_index("Year")["Carbon Lost (tC)"])

    with tab_data:
        st.subheader("Underlying Climate Impact Data")
        st.dataframe(df, use_container_width=True)
with tab_map:
    import leafmap.foliumap as leafmap
    import geopandas as gpd

    st.subheader("Sequestera Project MRV Map")

    m = leafmap.Map(center=[11.1271, 78.6569], zoom=7)

    # Add global Hansen forest loss
    m.add_basemap("Satellite")
    m.add_tile_layer(
        url="https://earthengine.googleapis.com/map/520bdaa1f76afab902ecc053a583151b/{z}/{x}/{y}?token=0790e7a11069a6e78373f3e3d6cfb779",
        name="Forest Loss",
        attribution="Hansen/UMD/Google/USGS/NASA"
    )

    # Add project boundary
    gdf = gpd.read_file("project_area.geojson")
    m.add_gdf(gdf, layer_name="Project Boundary", zoom_to_layer=True)

    m.add_layer_control()
    m.to_streamlit()

