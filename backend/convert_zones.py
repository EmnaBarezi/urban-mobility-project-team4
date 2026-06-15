import geopandas as gpd
import os

DATA_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'data')

# Read the shapefile, this has the zone shapes
shapefile_path = os.path.join(DATA_FOLDER, 'taxi_zones', 'taxi_zones.shp')
zones = gpd.read_file(shapefile_path)

print("Number of zones:", len(zones))
print("Columns:", zones.columns.tolist())

# Convert coordinates so the map can read them
zones = zones.to_crs(epsg=4326)

# Save as geojson for the map
output_path = os.path.join(DATA_FOLDER, 'taxi_zones.geojson')
zones.to_file(output_path, driver='GeoJSON')

print("Saved geojson to:", output_path)