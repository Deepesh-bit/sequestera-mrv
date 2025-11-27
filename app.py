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

        # ---- SUMMARY METRICS FOR SIDEBAR ----
    total_forest_loss = df["Forest Loss (ha)"].sum()
    total_co2_loss = df["CO2e Lost (tCO2e)"].sum()
    total_carbon_loss = df["Carbon Lost (tC)"].sum()

    worst_row = df.loc[df["CO2e Lost (tCO2e)"].idxmax()]
    worst_year = int(worst_row["Year"])
    worst_year_co2 = worst_row["CO2e Lost (tCO2e)"]

    # Read Sequestera Confidence Score if available
    scs = None
    try:
        with open("score.txt", "r") as f:
            scs = float(f.read().strip())
    except:
        scs = None

            # ---- SIDEBAR INSIGHTS ----
    with st.sidebar:
        st.title("Sequestera Insights")

        st.subheader("Deforestation Impact")
        st.metric("Total Forest Loss (ha)", f"{total_forest_loss:,.2f}")
        st.metric("Total CO₂e Emitted (tCO₂e)", f"{total_co2_loss:,.2f}")

        st.subheader("Worst Year")
        st.metric("Year", worst_year, help=f"{worst_year_co2:,.2f} tCO₂e emitted")

        if scs is not None:
            st.subheader("Confidence Score")
            st.metric("Sequestera Score", f"{scs:.2f} / 100")
        else:
            st.info("Run baseline_forest.py to generate the Sequestera Confidence Score.")



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
    import folium
    import geopandas as gpd
    from streamlit_folium import st_folium

    st.subheader("Sequestera MRV Map")

    # Load Project Boundary
    gdf = gpd.read_file("project_area.geojson")

    # Create Map centered on Tamil Nadu
    m = folium.Map(location=[11.1271, 78.6569], zoom_start=7)

    # Add Satellite Basemap
    folium.TileLayer(
    tiles="https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png",
    name="Topographic Map",
    attr="© OpenTopoMap contributors"
).add_to(m)


    # Add ESA Land Cover WMS
    folium.raster_layers.WmsTileLayer(
        url="https://services.sentinel-hub.com/ogc/wms/0312b59b-e5bb-4cff-8bda-d5e63d12f9a0",
        layers="LULC_SENTINEL2",
        fmt="image/png",
        transparent=True,
        name="Land Cover (ESA)"
    ).add_to(m)

    # Add Forest Loss WMS
    folium.raster_layers.WmsTileLayer(
        url="https://global-forest-watch-raster.s3.amazonaws.com/forest_loss_year_wms",
        layers="forest_loss_year",
        fmt="image/png",
        transparent=True,
        name="Forest Loss (Hansen)"
    ).add_to(m)

    # Add Project Boundary layer
    folium.GeoJson(
        gdf,
        name="Project Boundary",
        style_function=lambda x: {
            "fillOpacity": 0.1,
            "color": "#8E44AD",
            "weight": 3
        }
    ).add_to(m)

    # Enable Layer Control
    folium.LayerControl().add_to(m)

    # Render map
    st_data = st_folium(m, width=1000, height=600)

# ---- Pixel Analysis on Click ----
if st_data and st_data.get("last_clicked"):
    lat = st_data["last_clicked"]["lat"]
    lon = st_data["last_clicked"]["lng"]

    # Display clicked location
    st.success(f"📍 Clicked: {lat:.4f}, {lon:.4f}")

    st.write("🔍 Analyzing satellite data... (this may take a few seconds)")

    # Here we will add:
    # - Landcover API fetch
    # - Biomass API fetch
    # - Forest loss year fetch
    # - Carbon estimation logic

    import requests

# Helper function for WMS GetFeatureInfo
def get_pixel_value(lat, lon, url, layers):
    delta = 0.0005  # small bounding box around click
    bbox = f"{lon-delta},{lat-delta},{lon+delta},{lat+delta}"

    wms_url = (
        f"{url}"
        f"?SERVICE=WMS&VERSION=1.3.0&REQUEST=GetFeatureInfo"
        f"&CRS=EPSG:4326&INFO_FORMAT=application/json"
        f"&LAYERS={layers}&QUERY_LAYERS={layers}"
        f"&WIDTH=10&HEIGHT=10"
        f"&I=5&J=5"
        f"&BBOX={bbox}"
    )

    r = requests.get(wms_url)
    try:
        return r.json()
    except:
        return None


# Landcover info
lc_data = get_pixel_value(
    lat,
    lon,
    "https://services.sentinel-hub.com/ogc/wms/0312b59b-e5bb-4cff-8bda-d5e63d12f9a0",
    "LULC_SENTINEL2"
)

# Simplified class lookup (expand soon)
landcover_class = {
    10: "Tree Cover",
    20: "Shrubland",
    30: "Grassland",
    40: "Cropland",
    50: "Built Area",
    60: "Bare Land",
    70: "Snow/Ice",
    80: "Water"
}

st.subheader("🌎 MRV Pixel Intelligence")

# Show Landcover
if lc_data:
    try:
        code = int(lc_data["features"][0]["properties"]["VALUE"])
        st.write("🟩 Landcover:", landcover_class.get(code, f"Unknown ({code})"))
    except:
        st.write("🌐 Landcover: Not Available")
else:
    st.write("🌐 Landcover: No Data")


