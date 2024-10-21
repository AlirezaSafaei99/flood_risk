import pandas as pd
import folium
from folium.plugins import HeatMap
from branca.element import MacroElement, Template
import branca.colormap as cm
from folium.plugins import FloatImage

# Import the data
flood_df = pd.read_csv(r"D:\GIS & Geospatial Analysis with Python Geopandas and Folium\Projects\Flood Risk Analysis\AEGISDataset.csv")
flood_df.head(10)

# Using 3 elements that we have: flood_heig, elevation and precipitat we will calculate the flood risk
# We will do the data pre-processing
numeric_col = ["lat", "lon", "flood_heig", "elevation", "precipitat"]
flood_df[numeric_col] = flood_df[numeric_col].apply(pd.to_numeric, errors = "coerce")
flood_data_cl = flood_df.dropna()
#print(f"Nan after cleaning:\n{flood_data_cl.isnull().sum()}")

# Normalize the data
flood_data_cl["Normalized_Flood_Heig"] = (flood_data_cl["flood_heig"] - flood_data_cl["flood_heig"].min()) / (flood_data_cl["flood_heig"].max() - flood_data_cl["flood_heig"].min())
flood_data_cl["Normalized_elevation"] = (flood_data_cl["elevation"] - flood_data_cl["elevation"].min()) / (flood_data_cl["elevation"].max() - flood_data_cl["elevation"].min())
flood_data_cl["Normalized_precipitat"] = (flood_data_cl["precipitat"] - flood_data_cl["precipitat"].min()) / (flood_data_cl["precipitat"].max() - flood_data_cl["precipitat"].min())
flood_data_cl["Normalized_elevation"] = 1 - flood_data_cl["Normalized_elevation"]
flood_data_cl.head()


# Calculating the risk score base on the 3 elements that we have
flood_data_cl["risk_score"] = (flood_data_cl["Normalized_Flood_Heig"] * 0.4 + flood_data_cl["Normalized_elevation"] * 0.3 + flood_data_cl["Normalized_precipitat"])
flood_data_cl.head()

# Visualizing the risk_score
# Create the color for each zone of the flood risk score
flood_data_cl["risk_color"] = flood_data_cl["risk_score"].apply(
    lambda x: "green" if x < 0.2 else ("yellow" if 0.2 <= x < 0.4 else
                                       ("orange" if 0.4 <= x < 0.6 else ("red" if 0.6 <= x < 0.8 else "darkred"))))
"""def get_color(risk_score):
    if risk_score < 0.2:
        return "green"
    elif 0.2 <= risk_score < 0.4:
        return "yellow"
    elif 0.4 <= risk_score < 0.6:
        return "orange"
    elif 0.6 <= risk_score < 0.8:
        return "red"
    else:
        return "darkred"
flood_data_cl["risk_color"] = flood_data_cl["risk_score"].apply(get_color
"""

# Create the basemap and flood risk heatmap and add it to the basemap
manila_coor = [14.5995, 120.9842]
base_map = folium.Map(locations = manila_coor, zoom_start=5)
heat_map = flood_data_cl[["lat", "lon", "risk_score"]].values.tolist()
HeatMap(heat_map, radius=15, max_zoom=5).add_to(base_map)

# Create different tile layer to be able to switch the basemap tile layer
folium.TileLayer("CartoDB dark_matter", name="Dark").add_to(base_map)
folium.TileLayer("CartoDB positron", name="Light").add_to(base_map)

# Define a custom legend using MacroElement
color_map = cm.LinearColormap(
    colors=["green", "yellow", "orange", "red", "darkred"], 
    vmin=0, 
    vmax=1,
    caption="Flood Risk Level"
)

# Adding the legend and layer control to the basemap
folium.LayerControl().add_to(base_map)
color_map.add_to(base_map)

# Save the base map and display the map
base_map.save("Manila_Flood_Risk.html")
base_map