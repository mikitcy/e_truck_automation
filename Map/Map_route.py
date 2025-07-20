import polyline
import pandas as pd
import folium
import geopandas as gpd
import requests
from shapely.geometry import LineString

def get_route(lat_A, lon_A, lat_B, lon_B):
    """
    Fetches the route from OSRM API and returns the polyline coordinates.
    """
    osrm_url = f"http://router.project-osrm.org/route/v1/driving/{lon_A},{lat_A};{lon_B},{lat_B}?overview=full&geometries=polyline"
    response = requests.get(osrm_url)
    response.raise_for_status()
    data = response.json()

    if "routes" in data and data["routes"]:
        route_polyline = data['routes'][0]['geometry']
        route_coords = polyline.decode(route_polyline)  # Decode polyline to lat/lon coordinates
        return route_coords
    return []


def get_route_linestring(lat_A, lon_A, lat_B, lon_B):
    route_coords = get_route(lat_A, lon_A, lat_B, lon_B)  # Assumes it returns [(lat, lon), ...]
    if route_coords:
        return LineString([(lon, lat) for lat, lon in route_coords])
    else:
        return LineString()

def create_osmr_map(df, plot_color, save_path):

    # Create route LineStrings
    unique_coords = set(tuple(x) for x in df[['lat', 'lon', 'lat2', 'lon2']].dropna().values)
    coord_to_linestring = {
        coords: get_route_linestring(*coords)
        for coords in unique_coords
    }

    route_gdf = gpd.GeoDataFrame(
        geometry=list(coord_to_linestring.values()),
        crs="EPSG:4326"
    )
    # Create a map
    usa_center = [39.8283, -98.5795]
    m = folium.Map(location=usa_center, zoom_start=6)

    for line in route_gdf.geometry:
        folium.GeoJson(data=line, style_function=lambda x: {
            'color': 'black',
            'weight': 4,
            'opacity': 0.9
        }).add_to(m)

    for _, row in df.iterrows():
        for i in range(1, 6):
            lat = row.get(f'charge_lat_{i}')
            lon = row.get(f'charge_lon_{i}')
            if pd.notnull(lat) and pd.notnull(lon):
                folium.Marker(
                    location=[lat, lon],
                    popup=f"Charge {i}",
                    icon=folium.Icon(color=plot_color, icon='bolt', fill_color=plot_color,fill_opacity=0.9,prefix='fa')
                ).add_to(m)

    # Save map
    m.save(save_path)