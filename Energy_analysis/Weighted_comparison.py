import numpy as np

def weighted_columns_comparison(df1, df2, column="needed_energy_kwh", weight_col="w_factor", label=""):
    """
    Compare percent change in `column` between df1 and df2, weighted by `weight_col` from df1.
    Both DataFrames must have: origin_code, destination_code, column, weight_col.
    """

    # Merge DataFrames on origin and destination
    merged = df1.merge(df2, on=["origin_code", "destination_code"], suffixes=("_1", "_2"))

    # Calculate percent change
    merged["change_percent"] = ((merged[f"{column}_2"] - merged[f"{column}_1"]) /
                                merged[f"{column}_1"]) * 100

    # Drop rows with missing or zero base values
    merged = merged.dropna(subset=["change_percent", f"{weight_col}_1"])
    merged = merged[merged[f"{column}_1"] != 0]

    values = merged["change_percent"].values
    weights = merged[f"{weight_col}_1"].values
    weights = weights / weights.sum()

    # Weighted mean and std
    weighted_mean = np.sum(values * weights)
    weighted_var = np.sum(weights * (values - weighted_mean) ** 2)
    weighted_std = np.sqrt(weighted_var)

    # Weighted percentiles
    def weighted_percentile(data, weights, percentiles):
        sorter = np.argsort(data)
        data_sorted = data[sorter]
        weights_sorted = weights[sorter]
        cumsum = np.cumsum(weights_sorted)
        cumsum /= cumsum[-1]
        return np.interp(percentiles, cumsum, data_sorted)

    percentiles = [0, 0.25, 0.5, 0.75, 1.0]
    perc_vals = weighted_percentile(values, weights, percentiles)

    # Print the results
    print(f"Weighted describe for {column} percent change{f' ({label})' if label else ''}:")
    #print(f"Min:    {perc_vals[0]:.2f}%")
    print(f"25%:    {perc_vals[1]:.2f}%")
    print(f"Median: {perc_vals[2]:.2f}%")
    print(f"75%:    {perc_vals[3]:.2f}%")
    #print(f"Max:    {perc_vals[4]:.2f}%")
    print(f"Mean:   {weighted_mean:.2f}%")
    #print(f"Std:    {weighted_std:.2f}%")