import geopandas as gpd
import zipfile

def emissions_damage_waypoints(df, shapefile_path, df_gea, df_md):
    indices = [
        int(col.split('_')[-1]) for col in df.columns
        if col.startswith("charge_lat_") and col.split('_')[-1].isdigit()
    ]
    indices = sorted(set(indices))

    # Read county shapefile and create FIPS code
    extract_path = "shape/county_shapefile"
    with zipfile.ZipFile(shapefile_path, 'r') as zip_ref:
        zip_ref.extractall(extract_path)
    counties = gpd.read_file(extract_path).to_crs("EPSG:4326")
    counties["fips"] = counties["STATEFP"].str.zfill(2) + counties["COUNTYFP"].str.zfill(3)

    # Get FIPS codes from charger coordinates
    for i in indices:
        lat_col = f"charge_lat_{i}"
        lon_col = f"charge_lon_{i}"
        fips_col = f"fips_{i}"

        points = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df[lon_col], df[lat_col]), crs="EPSG:4326")
        joined = gpd.sjoin(points, counties[['fips', 'geometry']], how='left', predicate='within')
        df[fips_col] = joined['fips']

    # Merge GEA info
    df_gea["fips"] = df_gea["State FIPS"].astype(str).str.zfill(2) + df_gea["County FIPS"].astype(str).str.zfill(3)
    for i in indices:
        fips_col = f"fips_{i}"
        gea_col = f"GEA_{i}"
        df = df.merge(df_gea[["fips", "Cambium GEA"]].rename(columns={"Cambium GEA": gea_col}),
                      how="left", left_on=fips_col, right_on="fips").drop(columns=["fips"])

    # Merge emissions data
    for i in indices:
        gea_col = f"GEA_{i}"
        df = df.merge(df_md.rename(columns={
            "region": gea_col,
            "co2": f"co2_{i}",
            "nox": f"nox_{i}",
            "pm25": f"pm25_{i}",
            "so2": f"so2_{i}"
        }), how="left", on=gea_col)

    df = df.drop(columns="geometry", errors='ignore')

    return df

def emissions_damage_entrance(df, shapefile_path, df_gea, df_md):
    # Read county shapefile and create FIPS code
    extract_path = "shape/county_shapefile"
    with zipfile.ZipFile(shapefile_path, 'r') as zip_ref:
        zip_ref.extractall(extract_path)
    counties = gpd.read_file(extract_path).to_crs("EPSG:4326")
    counties["fips"] = counties["STATEFP"].str.zfill(2) + counties["COUNTYFP"].str.zfill(3)

    # Get fips for the (lat, lon) of first rows per origin-destination id
    df['row_id'] = df.index
    first_rows = df.sort_values('row_id').groupby(['origin_code', 'destination_code'], as_index=False).first()

    gdf = gpd.GeoDataFrame(
        first_rows,
        geometry=gpd.points_from_xy(first_rows['lon'], first_rows['lat']),
        crs="EPSG:4326"
    )
    joined = gpd.sjoin(gdf, counties[['fips', 'geometry']], how='left', predicate='within')
    joined = joined[['origin_code', 'destination_code', 'fips']]

    # Join with df_gea to get GEA
    df_gea["fips"] = df_gea["State FIPS"].astype(str).str.zfill(2) + df_gea["County FIPS"].astype(str).str.zfill(3)
    joined = joined.merge(df_gea[['fips', 'Cambium GEA']], on='fips', how='left').rename(columns={"Cambium GEA": "GEA_0"})

    # Add emissions from df_md
    emissions = df_md.rename(columns={
        "region": "GEA_0",
        "co2": "co2_0",
        "nox": "nox_0",
        "pm25": "pm25_0",
        "so2": "so2_0"
    })
    joined = joined.merge(emissions, on="GEA_0", how="left")

    # Fill in df with values for only first rows
    df = df.merge(joined, on=['origin_code', 'destination_code'], how='left')

    # Set values only on first row per origin-destination pair, zero elsewhere
    mask = df.sort_values('row_id').duplicated(['origin_code', 'destination_code'])
    for col in ['GEA_0', 'co2_0', 'nox_0', 'pm25_0', 'so2_0']:
        df.loc[mask, col] = None

    df = df.drop(columns=['row_id'])

    return df

def grid_emissions_damage_total(df, battery_kwh):
    indices = [
        int(col.split('_')[-1]) for col in df.columns
        if col.startswith("charge_lat_") and col.split('_')[-1].isdigit()
    ]
    indices = sorted(set(indices))
    all_indices = [0] + indices #include _0 for sum

    # Constants
    consumable_power_portion = 0.85  # battery is charged from 10% to 95%
    charger_efficiency = 0.86 #FASTSim, 86%: Henning Lohse-Busch, M. Duoba, E. Rask, Advanced Powertrain Research facility AVTA Nissan Leaf Testing and Analysis, May 2nd, 2025

    # Get emissions from power use
    pollutants = ["co2", "pm25", "so2", "nox"]
    for pollutant in pollutants:
        # Sum the emissions from all charging waypoints and origin
        cols = [f"{pollutant}_{i}" for i in all_indices]
        df[f"{pollutant}_power"] = (
                df[cols].sum(axis=1)
                * battery_kwh
                * consumable_power_portion
                / 1000
                / charger_efficiency
        )

    # Aggregate to df_results
    df_results = df.groupby(["origin_code", "destination_code"]).agg({
        "miles": "sum",
        "co2_power": "sum",
        "pm25_power": "sum",
        "so2_power": "sum",
        "nox_power": "sum"
    }).reset_index()

    return df, df_results