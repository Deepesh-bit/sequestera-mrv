import geopandas as gpd
import rasterio
from rasterio.mask import mask
import numpy as np
import matplotlib.pyplot as plt
import csv

# ---------- CONFIG ----------
PROJECT_GEOJSON = "project_area.geojson"
TREECOVER_TIF = "Hansen_GFC-2024-v1.12_treecover2000_20N_070E.tif"
LOSSYEAR_TIF = "Hansen_GFC-2024-v1.12_lossyear_20N_070E.tif"
TREECOVER_THRESHOLD = 30
START_YEAR = 2001
END_YEAR = 2023

# Climate conversion factors (IPCC-like)
DEFAULT_BIOMASS_PER_HA = 120  # tonnes per hectare (adjust later)
CARBON_FRACTION = 0.47        # Carbon in biomass
CO2_CONVERSION = 44 / 12      # C to CO₂e
# ----------------------------


def calculate_pixel_area(src):
    pixel_width, pixel_height = src.res
    meter_per_degree = 111320
    pixel_area_m2 = (pixel_width * meter_per_degree) * (pixel_height * meter_per_degree)
    return pixel_area_m2 / 10000


def main():
    project = gpd.read_file(PROJECT_GEOJSON)

    with rasterio.open(TREECOVER_TIF) as src:
        project = project.to_crs(src.crs)
        out_image, _ = mask(src, project.geometry, crop=True)
        treecover = out_image[0]
        pixel_area_ha = calculate_pixel_area(src)

        forest_mask = treecover > TREECOVER_THRESHOLD
        forest_area_ha = np.sum(forest_mask) * pixel_area_ha
        total_area_ha = treecover.size * pixel_area_ha
        forest_percentage = (forest_area_ha / total_area_ha) * 100

        print("\n--- BASELINE FOREST METRICS ---")
        print(f"Project Area (ha): {total_area_ha:.2f}")
        print(f"Forest Area (ha): {forest_area_ha:.2f}")
        print(f"Forest Cover (%): {forest_percentage:.2f}%")

    with rasterio.open(LOSSYEAR_TIF) as src:
        out_loss, _ = mask(src, project.geometry, crop=True)
        lossyear = out_loss[0]

        years = list(range(START_YEAR, END_YEAR + 1))
        loss_by_year = []

        for y in years:
            pixels_lost = np.sum(lossyear == (y - 2000))
            ha_lost = pixels_lost * pixel_area_ha
            loss_by_year.append(ha_lost)

        print("\n--- FOREST LOSS OVER TIME ---")
        for y, loss in zip(years, loss_by_year):
            print(f"{y}: {loss:.2f} ha")

        biomass_loss = [ha * DEFAULT_BIOMASS_PER_HA for ha in loss_by_year]
        carbon_loss = [b * CARBON_FRACTION for b in biomass_loss]
        co2_loss = [c * CO2_CONVERSION for c in carbon_loss]

        with open("climate_impact_report.csv", "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Year", "Forest Loss (ha)", "Biomass Lost (t)", "Carbon Lost (tC)", "CO2e Lost (tCO2e)"])
            writer.writerows(zip(years, loss_by_year, biomass_loss, carbon_loss, co2_loss))

        print("\nClimate impact report saved → climate_impact_report.csv")

        # ---- SUMMARY INSIGHTS ----
        total_forest_loss = sum(loss_by_year)
        total_co2_loss = sum(co2_loss)
        total_carbon_loss = sum(carbon_loss)

        if len(co2_loss) > 0:
            max_co2 = max(co2_loss)
            idx = co2_loss.index(max_co2)
            worst_year = years[idx]
        else:
            max_co2 = 0
            worst_year = None

        print("\n--- SUMMARY INSIGHTS ---")
        print(f"Total forest lost (2001–{END_YEAR}): {total_forest_loss:.2f} ha")
        print(f"Total carbon lost: {total_carbon_loss:.2f} tC")
        print(f"Total CO2e emitted from deforestation: {total_co2_loss:.2f} tCO2e")
        if worst_year is not None:
            print(f"Worst year: {worst_year} with {max_co2:.2f} tCO2e emitted")

        with open("summary_report.txt", "w") as f:
            f.write("SEQUESTERA MRV – Climate Impact Summary\n")
            f.write("--------------------------------------\n")
            f.write(f"Project area (approx): {total_area_ha:.2f} ha\n")
            f.write(f"Forest area baseline: {forest_area_ha:.2f} ha ({forest_percentage:.2f}% cover)\n\n")
            f.write(f"Total forest lost (2001–{END_YEAR}): {total_forest_loss:.2f} ha\n")
            f.write(f"Total carbon lost: {total_carbon_loss:.2f} tC\n")
            f.write(f"Total CO2e emitted: {total_co2_loss:.2f} tCO2e\n")
            if worst_year is not None:
                f.write(f"Worst year: {worst_year} with {max_co2:.2f} tCO2e emitted\n")

        print("\nSummary saved → summary_report.txt")

                # ---- SEQUESTERA CONFIDENCE SCORE ----
        # Permanence score based on recent deforestation trend
        recent_loss = sum(loss_by_year[-5:])  # last 5 years
        avg_annual_loss = total_forest_loss / len(years)
        
        if avg_annual_loss == 0:
            permanence_score = 40
        else:
            ratio = recent_loss / (avg_annual_loss * 5)
            permanence_score = max(0, 40 - (ratio - 1) * 20)
            permanence_score = min(permanence_score, 40)

        # Performance score from retained forest cover
        performance_score = (forest_percentage / 100) * 35
        performance_score = min(performance_score, 35)

        # Leakage score (temporary auto 100%)
        leakage_score = 25

        total_score = permanence_score + performance_score + leakage_score

        print("\n--- SEQUESTERA CONFIDENCE SCORE ---")
        print(f"Permanence: {permanence_score:.2f} / 40")
        print(f"Performance: {performance_score:.2f} / 35")
        print(f"Leakage: {leakage_score:.2f} / 25")
        print(f"TOTAL SCS: {total_score:.2f} / 100")

        with open("summary_report.txt", "a") as f:
            f.write("\nSequestera Confidence Score\n")
            f.write(f"{total_score:.2f} / 100\n")



        # ---- CHARTS ----
        plt.figure(figsize=(14, 6))


        plt.subplot(1, 2, 1)
        plt.bar(years, co2_loss)
        plt.title("CO₂e Emissions from Forest Loss")
        plt.xlabel("Year")
        plt.ylabel("tCO₂e Released")

        plt.subplot(1, 2, 2)
        plt.plot(years, carbon_loss, marker="o")
        plt.title("Carbon Loss from Deforestation")
        plt.xlabel("Year")
        plt.ylabel("tC Lost")

        plt.tight_layout()
        plt.show()


if __name__ == "__main__":
    main()
