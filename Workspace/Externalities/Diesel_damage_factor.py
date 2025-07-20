import pandas as pd
import geopandas as gpd
import zipfile
import os
from datetime import datetime
from shapely.geometry import LineString

from Map.Map_route import get_route
from Filepath.filepath import workspace_folder

os.chdir(workspace_folder)

def get_route_linestring(lat_A, lon_A, lat_B, lon_B):
    route_coords = get_route(lat_A, lon_A, lat_B, lon_B)
    if route_coords:
        return LineString([(lon, lat) for lat, lon in route_coords])
    else:
        return LineString()

print(datetime.now())
df = pd.read_csv("rt_final.csv")

#  origin_code, destination_code
origin_col = 'origin_code'
destination_col = 'destination_code'
df_sorted = df.sort_values(by=[origin_col, destination_col])
df_sorted["lon2"] = df_sorted.groupby([origin_col, destination_col])["lon"].shift(-1)
df_sorted["lat2"] = df_sorted.groupby([origin_col, destination_col])["lat"].shift(-1)
df_sorted = df_sorted.dropna(subset=["lon2", "lat2"])
print(datetime.now())

# Get combination of orig/dest coordinates per row
df_sorted["coord_pair"] = list(zip(df_sorted["lat"], df_sorted["lon"], df_sorted["lat2"], df_sorted["lon2"]))
unique_coords = df_sorted["coord_pair"].drop_duplicates()

# Add OSMR linestring as GeoDataFrame
coord_to_linestring = {
    coords: get_route_linestring(*coords)
    for coords in unique_coords
}

# Map the geometry to route segments
df_sorted["geometry"] = df_sorted["coord_pair"].map(coord_to_linestring)
gdf_lines = gpd.GeoDataFrame(df_sorted, geometry='geometry', crs='EPSG:4326')
gdf_lines.to_file(r'results/truck_trajectories_osrm.geojson', driver='GeoJSON')
#print(gdf_lines.columns)
print(datetime.now())

# Read county shape file
shapefile_path = "shape/cb_2018_us_county_500k.zip"
extract_path = "shape/county_shapefile"
with zipfile.ZipFile(shapefile_path, 'r') as zip_ref:
    zip_ref.extractall(extract_path)
counties = gpd.read_file(extract_path).to_crs("EPSG:4326")
counties = counties.drop(columns=[col for col in ['origin_code', 'destination_code'] if col in counties.columns])

# Get intersection FIPs of route and county
intersections = gpd.overlay(gdf_lines, counties, how='intersection') #intersect geometries
intersections["segment_length_km"] = intersections.geometry.length * 111
intersections["fips"] = (
    intersections["STATEFP"].astype(str).str.zfill(2) +
    intersections["COUNTYFP"].astype(str).str.zfill(3)
)
print(intersections.columns)

# Get length-weight per fips
results = intersections[["origin_code", "destination_code", "fips", "segment_length_km"]]
df_county = results.groupby(["origin_code", "destination_code", "fips"]).agg({
    "segment_length_km": "sum"
}).reset_index()
total_lengths = df_county.groupby(["origin_code", "destination_code"])["segment_length_km"].transform("sum")
df_county["weight"] = df_county["segment_length_km"] / total_lengths
df_county["weight"] = df_county["weight"].fillna(1)
df_county.to_csv("results/diesel_md_by_county_osrm.csv", index=False)

# Add AP2 emission factor to df
ap_df = pd.read_csv("emissions/AP2_MD.csv")
ap_df["fips"] = ap_df["fips"].astype(str).str.zfill(5)
#adjust statistical value of life, 2000$/ton -> 2024$/ton
ap_df["PM25"] = ap_df["PM25_2011"].astype(float) * 13.7 / 6 #* 1.82 (double count)
ap_df["NOX"] = ap_df["NOX_2011"].astype(float) * 13.7 / 6 #* 1.82
ap_df["SO2"] = ap_df["SO2_2011"].astype(float) * 13.7 / 6 #* 1.82

df_county["fips"] = df_county["fips"].astype(str).str.zfill(5)
ap_df["fips"] = ap_df["fips"].astype(str).str.zfill(5)
df_county = df_county.merge(ap_df[["fips", "PM25", "NOX", "SO2"]], on="fips", how="left")

# Add state for fips (use for upstream MD)
df_county["state_fips"] = df_county["fips"].str[:2]
df_county["state_fips"] = df_county["state_fips"].astype(str).str.zfill(2)

# Get weighted marginal damage factor
df_county["PM25_weighted"] = df_county["PM25"] * df_county["weight"]
df_county["NOX_weighted"] = df_county["NOX"] * df_county["weight"]
df_county["SO2_weighted"] = df_county["SO2"] * df_county["weight"]
df_county.to_csv("results/diesel_md_by_county_osrm.csv", index=False)

# Get MD factor per route
df_results = df_county.groupby(["origin_code", "destination_code"]).agg({
    "PM25_weighted": "sum",
    "NOX_weighted": "sum",
    "SO2_weighted": "sum"
}).reset_index()
# Get route length from the original datasets
route_lengths = df_sorted.groupby(["origin_code", "destination_code"])["km"].sum().reset_index()
df_results = df_results.merge(route_lengths, on=["origin_code", "destination_code"], how="left")
# Take first state for each route (use if for upstream diesel emissions)
state_fips_by_route = df_county.groupby(["origin_code", "destination_code"])["state_fips"].first().reset_index()
df_results = df_results.merge(state_fips_by_route, on=["origin_code", "destination_code"], how="left")

df_fips = pd.read_csv("shape/fips_State.csv")
df_fips["state_fips"] = df_fips["state_fips"].astype(str).str.zfill(2)
df_results = df_results.merge(df_fips[["state_fips", "state"]], how="left")

df_results.to_csv("results/diesel_md_weighted_osrm.csv", index=False)
print(datetime.now())