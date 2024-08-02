import geopandas as gpd
import folium
from shapely.geometry import shape

gdf = gpd.read_file("ne_110m_populated_places/ne_110m_populated_places.shp")

switzerland_bounds = gdf.total_bounds
map_center = [(switzerland_bounds[1] + switzerland_bounds[3]) / 2,
              (switzerland_bounds[0] + switzerland_bounds[2]) / 2]

m = folium.Map(location=map_center, zoom_start=8)

folium.GeoJson(gdf).add_to(m)

m.save("switzerland_map.html")
