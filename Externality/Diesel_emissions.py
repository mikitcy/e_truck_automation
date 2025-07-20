
def diesel_tailpipe_emissions(df, scc):
    # GREET input (g/km)
    ghg_per_km = 909
    pm25_per_km = 0.0103
    nox_per_km = 1.13
    so2_per_km = 0.00626

    # Get total damage (damage factor: $/ton)
    df["co2_tailpipe"] = df["km"] * ghg_per_km / 1000000 * scc
    df["pm25_tailpipe"] = df["km"] * pm25_per_km / 1000000 * df["PM25_weighted"]
    df["nox_tailpipe"] = df["km"] * nox_per_km / 1000000 * df["NOX_weighted"]
    df["so2_tailpipe"] = df["km"] * so2_per_km / 1000000 * df["SO2_weighted"]

    return df

def diesel_upstream_emissions(df, df_MD_diesel, scc):
    # GREET input (g/km)
    ghg_per_km = 183
    pm25_per_km = 0.0124
    nox_per_km = 0.2095
    so2_per_km = 0.0531

    # MD at the entrance (diesel upstream)
    df = df.merge(df_MD_diesel[["state", "nox_md", "so2_md", "pm25_md"]], on="state", how="left")

    # Get total damage (damage factor: $/ton)
    df["co2_upstream"] = df["km"] * ghg_per_km / 1000000 * scc
    df["pm25_upstream"] = df["km"] * pm25_per_km / 1000000 * df["pm25_md"]
    df["nox_upstream"] = df["km"] * nox_per_km / 1000000 * df["nox_md"]
    df["so2_upstream"] = df["km"] * so2_per_km / 1000000 * df["so2_md"]

    return df

def diesel_total_emissions(df):
    df["co2_fuel"] = df["co2_tailpipe"] + df["co2_upstream"]
    df["pm25_fuel"] = df["pm25_tailpipe"] + df["pm25_upstream"]
    df["nox_fuel"] = df["nox_tailpipe"] + df["nox_upstream"]
    df["so2_fuel"] = df["so2_tailpipe"] + df["so2_upstream"]

    return df