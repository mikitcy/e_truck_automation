import pandas as pd
import h3
import folium
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import branca.colormap as cm

def get_all_coordinates(df):
    first_idx = (df.groupby(['origin_code', 'destination_code']).head(1).index)
    df['charge_lat_0'] = np.nan
    df['charge_lon_0'] = np.nan
    df.loc[first_idx, 'charge_lat_0'] = df.loc[first_idx, 'lat']
    df.loc[first_idx, 'charge_lon_0'] = df.loc[first_idx, 'lon']

    coord_dfs = []
    for i in range(0, 6):
        temp = df[[f'charge_lat_{i}', f'charge_lon_{i}', 'w_factor']].copy()
        temp.columns = ['charge_lat', 'charge_lon', 'w_factor']
        coord_dfs.append(temp)

    melted = pd.concat(coord_dfs, ignore_index=True)
    melted = melted.dropna(subset=["charge_lat", "charge_lon", 'w_factor'])
    charge_loc_df = melted[['charge_lat', 'charge_lon', 'w_factor']].reset_index(drop=True)

    return charge_loc_df

def weight_routes(df, cum_pct=99, w_col="w_factor", ascending=False):
    ### Select routes that ship 99% of annual ton-mile
    routes = (
        df[["origin_code", "destination_code", w_col]]
        .drop_duplicates(["origin_code", "destination_code"])
        .sort_values(w_col, ascending=ascending)
        .copy()
    )
    routes["cum_pct"] = 100 * routes[w_col].cumsum() / routes[w_col].sum()
    n = (routes["cum_pct"] <= cum_pct).sum() + 1
    selected_routes = routes.iloc[:n][["origin_code", "destination_code"]]
    return df.merge(
        selected_routes,
        on=["origin_code", "destination_code"],
        how="inner"
    )

def h3_map(df, lon_col="charge_lon", lat_col="charge_lat", resolution=4):

    # Count location per H3 hexagon
    df["h3"] = df.apply(lambda row: h3.latlng_to_cell(row[lat_col], row[lon_col], resolution), axis=1)
    hex_counts = (df.groupby("h3").size().reset_index(name="count"))
    print("unique hexbins:", len(hex_counts))

    # Convert H3 hexagons to GeoJSON polygons
    features = []
    for _, row in hex_counts.iterrows():
        boundary = h3.cell_to_boundary(row["h3"])
        polygon = [[lon, lat] for lat, lon in boundary] # folium expects [lon, lat]
        features.append({
            "type": "Feature",
            "properties": {
                "h3": row["h3"],
                "count": int(row["count"])
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [polygon]
            }
        })
    geojson = {"type": "FeatureCollection", "features": features}

    # color map
    vmin = 1#hex_counts["count"].quantile(0.025)
    vmax = 80 #hex_counts["count"].quantile(0.975)
    colors = [mcolors.to_hex(plt.cm.inferno_r(i))
        for i in np.linspace(0, 1, 256)
    ]
    colormap = cm.LinearColormap(colors=colors,vmin=vmin,vmax=vmax)

    # map
    map = folium.Map(location=[df[lat_col].mean(), df[lon_col].mean()], zoom_start=5, tiles="cartodbpositron")
    folium.GeoJson(
        geojson,
        style_function=lambda feature: {"fillColor": colormap(min(max(feature["properties"]["count"], vmin), vmax)),
            "color": "black","weight": 0.2,"fillOpacity": 0.7},
    ).add_to(map)

    colormap.caption = "Number of points"
    colormap.add_to(map)

    return map

def h3_map_diff_pct(df,df2,lon_col="charge_lon",lat_col="charge_lat",resolution=4):

    df = df.copy()
    df2 = df2.copy()

    df["h3"] = df.apply(lambda row: h3.latlng_to_cell(row[lat_col], row[lon_col], resolution),axis=1)
    df2["h3"] = df2.apply(lambda row: h3.latlng_to_cell(row[lat_col], row[lon_col], resolution),axis=1)

    # Sum GWh per H3 cell
    hex1 = (df.groupby("h3").size().reset_index(name="count_1"))
    hex2 = (df2.groupby("h3").size().reset_index(name="count_2"))

    hex_diff = hex1.merge(hex2, on="h3", how="outer").fillna(0)

    hex_diff["diff_pct"] = (hex_diff["count_1"] - hex_diff["count_2"]) / hex_diff["count_2"] * 100
    hex_diff = hex_diff.replace([np.inf, -np.inf], np.nan)
    hex_diff = hex_diff.dropna(subset=["diff_pct"])

    # map
    features = []
    for _, row in hex_diff.iterrows():
        boundary = h3.cell_to_boundary(row["h3"])
        polygon = [[lon, lat] for lat, lon in boundary]

        features.append({
            "type": "Feature",
            "properties": {
                "h3": row["h3"],
                "diff_pct": float(row["diff_pct"])
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [polygon]
            }
        })
    geojson = {"type": "FeatureCollection", "features": features}

    # color map
    vmin = -100
    vmax = 100
    colors = [mcolors.to_hex(plt.cm.coolwarm(i))
        for i in np.linspace(0, 1, 256)
    ]
    colormap = cm.LinearColormap(colors=colors,vmin=vmin,vmax=vmax)

    # Map
    map = folium.Map(location=[df[lat_col].mean(), df[lon_col].mean()], zoom_start=5, tiles="cartodbpositron")
    folium.GeoJson(
        geojson,
        style_function=lambda feature: {
            "fillColor": colormap(
                min(max(feature["properties"]["diff_pct"], vmin), vmax)
            ),
            "color": "black",
            "weight": 0.2,
            "fillOpacity": 0.7
        },
    ).add_to(map)

    colormap.caption = "Difference (%) in number of location by slowing from 60 mph to 45 mph"
    colormap.add_to(map)

    return map
