import os
import requests
import pandas as pd
from math import radians, sin, cos, sqrt, atan2

def get_segment_length(lat1, lon1, lat2, lon2):
    """
    Calculate the great-circle distance between two points
    on the Earth's surface given their latitude and longitude.
    """
    # Radius of the Earth in meters
    R = 6371000

    # Convert latitude and longitude from degrees to radians
    lat1 = radians(lat1)
    lon1 = radians(lon1)
    lat2 = radians(lat2)
    lon2 = radians(lon2)

    # Differences in coordinates
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    # Haversine formula
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c

    return distance

def get_highway_point(lat_A, lon_A, lat_B, lon_B, dist_ac):
    # OSRM API endpoint
    osrm_url = "http://router.project-osrm.org/route/v1/driving/{},{};{},{}?overview=full&geometries=geojson".format(
        lon_A, lat_A, lon_B, lat_B)

    # Send request to OSRM
    response = requests.get(osrm_url)
    data = response.json()

    # Extract the route geometry
    route = data['routes'][0]['geometry']['coordinates']

    # Convert dist_ac from miles to meters
    dist_ac_meters = dist_ac * 1609.34

    # Traverse the route to find the location of point C
    cumulative_dist = 0
    prev_point = None

    for point in route:
        if prev_point is None:
            prev_point = point
            continue

        # Calculate distance between consecutive points
        lon1, lat1 = prev_point
        lon2, lat2 = point
        segment_length = get_segment_length(lat1, lon1, lat2, lon2)
        cumulative_dist += segment_length

        if cumulative_dist >= dist_ac_meters:
            remaining_dist = dist_ac_meters - (cumulative_dist - segment_length)

            # Interpolate the position
            ratio = 1 if segment_length == 0 else remaining_dist / segment_length
            lat_C = lat1 + (lat2 - lat1) * ratio
            lon_C = lon1 + (lon2 - lon1) * ratio

            return lat_C, lon_C

        prev_point = point

    return None, None

def round_miles(x):
    try:
        x = float(x)
        return int(round(x / 1.0)) * 1 if x > 0 else None
    except:
        return None

# Generate unique OD-charge point combinations
def get_unique_charge_points_df(df):
    """
    Extracts a DataFrame of all unique (lat, lon, lat2, lon2, charge_mile) combinations.
    """
    mile_cols = [f'charge_mile_{i}' for i in range(1, 6)]

    melted = df.melt(
        id_vars=['lat', 'lon', 'lat2', 'lon2'],
        value_vars=mile_cols,
        var_name='mile_source',
        value_name='charge_mile'
    )
    melted = melted.dropna(subset=['charge_mile'])
    melted['charge_mile'] = melted['charge_mile'].apply(round_miles)
    melted['charge_mile'] = melted['charge_mile'].astype(float)
    unique_charge_df = melted[['lat', 'lon', 'lat2', 'lon2', 'charge_mile']].drop_duplicates().reset_index(drop=True)
    return unique_charge_df

# Get coordinates
def get_charge_coordinates(unique_charge_df, output_file=None):
    """
    Adds charge_lat, charge_lon by computing highway points.
    """
    charge_df = unique_charge_df.copy()
    results = []

    if output_file and os.path.exists(output_file):
        os.remove(output_file)

    for idx, row in charge_df.iterrows():
        lat_C, lon_C = get_highway_point(row['lat'], row['lon'], row['lat2'], row['lon2'], row['charge_mile'])
        results.append((lat_C, lon_C))

        if output_file:
            interim_df = pd.DataFrame([{
                'lat': row['lat'],
                'lon': row['lon'],
                'lat2': row['lat2'],
                'lon2': row['lon2'],
                'charge_mile': row['charge_mile'],
                'charge_lat': lat_C,
                'charge_lon': lon_C
            }])
            interim_df.to_csv(output_file, mode='a', header=not os.path.exists(output_file), index=False)

    charge_df[['charge_lat', 'charge_lon']] = pd.DataFrame(results, index=charge_df.index)
    return charge_df

# in case the attempt above is interrupted
def get_resume_subset(unique_charge_df, charge_df_interim):

    key_cols = ['lat', 'lon', 'lat2', 'lon2', 'charge_mile']
    df_keys = unique_charge_df[key_cols].drop_duplicates()
    interim_keys = charge_df_interim[key_cols].drop_duplicates()
    # Get only rows not yet in interim
    charge_df_resume = df_keys.merge(interim_keys, on=key_cols, how='left', indicator=True)
    charge_df_resume = charge_df_resume[charge_df_resume['_merge'] == 'left_only'].drop(columns=['_merge'])

    return charge_df_resume

# merge into routes
def merge_charge_coordinates(rt_leg_charge, charge_df):
    rt_leg_charge = rt_leg_charge.copy()
    #print(rt_leg_charge.columns)

    indices = [
        i for i in range(1, 6)
        if f'charge_mile_{i}' in rt_leg_charge.columns
    ]

    for i in indices:
        mile_col = f'charge_mile_{i}'
        lat_col = f'charge_lat_{i}'
        lon_col = f'charge_lon_{i}'

        # Create temp with keys and preserve index
        temp = rt_leg_charge[['lat', 'lon', 'lat2', 'lon2', mile_col]].copy()
        temp = temp.rename(columns={mile_col: 'charge_mile'})
        temp['charge_mile'] = temp['charge_mile'].apply(round_miles)
        temp['charge_mile'] = pd.to_numeric(temp['charge_mile'], errors='coerce')
        temp['index'] = rt_leg_charge.index
        charge_df['charge_mile'] = pd.to_numeric(charge_df['charge_mile'], errors='coerce')

        # Merge with df2
        merged = temp.merge(
            charge_df[['lat', 'lon', 'lat2', 'lon2', 'charge_mile', 'charge_lat', 'charge_lon']],
            on=['lat', 'lon', 'lat2', 'lon2', 'charge_mile'],
            how='left'
        )

        # Assign new columns back using index
        rt_leg_charge[lat_col] = merged.set_index('index')['charge_lat']
        rt_leg_charge[lon_col] = merged.set_index('index')['charge_lon']

    return rt_leg_charge

