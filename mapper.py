import os
import osmnx as ox
import matplotlib.pyplot as plt
import contextily as cx

from dotenv import load_dotenv

load_dotenv()

CARTO_KEY = os.getenv("CARTO_KEY")

def test_place(place: str):
    area = ox.geocode_to_gdf(place)
    area = area.to_crs(epsg = 3857)
    fig, ax = plt.subplots(figsize = (12, 12))
    
    area.plot(
        ax = ax,
        facecolor = "none",
        edgecolor = "red",
        linewidth = 2
    )
    
    cx.add_basemap(
        ax,
        source = "https://basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}.png?key=" + CARTO_KEY
    )
    
    ax.set_axis_off()
    plt.show()