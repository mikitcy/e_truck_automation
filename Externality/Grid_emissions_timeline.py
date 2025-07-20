
def grid_emission_timeline(df, df_md_timeline, battery_kwh):
    df = df.copy()
    indices = sorted(set(
        int(col.split('_')[-1])
        for col in df.columns
        if col.startswith("GEA_") and col.split('_')[-1].isdigit()
        and f"co2_{col.split('_')[-1]}" in df.columns
    ))
    years = [2030, 2035, 2040, 2045, 2050]

    for i in indices:
        gea_col = f"GEA_{i}"
        co2_col = f"co2_{i}"
        df[gea_col] = df[gea_col].astype(str)
        for year in years:
            frac_col = f"{year}_frac"
            df = df.merge(
                df_md_timeline[["region", frac_col]].rename(columns={"region": gea_col,frac_col: f"{co2_col}_{year}"}),
                how="left", on=gea_col
            )
            df[f"{co2_col}_{year}"] = df[co2_col] * df[f"{co2_col}_{year}"]

    for year in years:
        year_cols = [f"co2_{i}_{year}" for i in indices if f"co2_{i}_{year}" in df.columns]
        df[f"co2_{year}"] = df[year_cols].sum(axis=1)

    ### Convert $/kWh factor to $
    # Constants
    consumable_power_portion = 0.85  # battery is charged from 10% to 95%
    charger_efficiency = 0.86 #FASTSim, 86%: Henning Lohse-Busch, M. Duoba, E. Rask, Advanced Powertrain Research facility AVTA Nissan Leaf Testing and Analysis, May 2nd, 2025

    df["co2_2025"] = df["co2_power"]
    for year in years:
        df[f"co2_{year}"] = (
                df[f"co2_{year}"]
                * battery_kwh
                * consumable_power_portion
                / 1000
                / charger_efficiency
        )

    ### Summary per route
    df_results = df.groupby(["origin_code", "destination_code"]).agg({
        "co2_2025": "sum",
        "co2_2030": "sum",
        "co2_2035": "sum",
        "co2_2040": "sum",
        "co2_2045": "sum",
        "co2_2050": "sum"
    }).reset_index()

    return df, df_results