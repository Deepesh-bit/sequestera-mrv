import rasterio
import geopandas as gpd
import numpy as np
from rasterio.mask import mask

# Input files
POLY = "project_area.geojson"
LOSS_TIF = "Hansen_GFC-2024-v1.12_lossyear_20N_070E.tif"

def process_loss_map():
    project = gpd.read_file(POLY)
    geom = project.geometry.values

    with rasterio.open(LOSS_TIF) as src:
        clipped, transform = mask(src, geom, crop=True)

    loss = clipped[0]
    loss[loss <= 0] = 0

    # Normalize to 0-1 for heatmap
    heat = loss / np.max(loss) if np.max(loss) > 0 else loss

    # Classification into severity
    classified = np.zeros_like(loss)
    classified[(loss > 0) & (loss <= 10)] = 1
    classified[(loss > 10) & (loss <= 20)] = 2
    classified[loss > 20] = 3

    return heat, classified, transform
