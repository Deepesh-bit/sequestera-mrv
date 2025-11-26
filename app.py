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

    tab_overview, tab_forest, tab_carbon, tab_data = st.tabs(
        ["🌍 Overview", "🌳 Forest Loss", "🔥 Carbon & CO₂", "📄 Raw Data"]
    )

    with tab_overview:
        st.subheader("Project Summary (Auto-Generated)")

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Forest Lost (ha)", f"{total_forest_loss:,.2f}")
        col2.metric("Total CO₂e Emitted (tCO₂e)", f"{total_co2_loss:,.2f}")
        col3.metric("Worst Year (tCO₂e)", f"{worst_year} ({worst_year_co2:,.2f})")

        st.write("""
        The Sequestera MRV engine analyzes deforestation and estimates carbon emissions to verify climate impact.
        Confidence scoring and satellite validation modules are coming soon.
        """)

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
