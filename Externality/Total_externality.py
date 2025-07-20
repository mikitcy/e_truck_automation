
def get_total_externality(df):
    df['air_pollution'] = df["pm25"] + df["so2"] + df["nox"]
    df['total_externality'] = df['co2'] + df['air_pollution']
    return df

def get_total_externality_timeline(df):
    df['externality_2025'] = df['co2_2025'] + df['air_pollution']
    df['externality_2030'] = df['co2_2030'] + df['air_pollution']
    df['externality_2035'] = df['co2_2035'] + df['air_pollution']
    df['externality_2040'] = df['co2_2040'] + df['air_pollution']
    df['externality_2045'] = df['co2_2045'] + df['air_pollution']
    df['externality_2050'] = df['co2_2050'] + df['air_pollution']
    return df