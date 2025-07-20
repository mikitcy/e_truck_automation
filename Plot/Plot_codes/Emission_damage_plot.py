import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from Filepath.filepath import workspace_folder

os.chdir(workspace_folder)

### Location data
df_results_60 = pd.read_csv('results/power_emission_60_per_route.csv')
df_results_55 = pd.read_csv('results/power_emission_55_per_route.csv')
df_results_50 = pd.read_csv('results/power_emission_50_per_route.csv')
df_results_45 = pd.read_csv('results/power_emission_45_per_route.csv')
df_results_diesel = pd.read_csv('results/diesel_damage_per_route.csv')
print(df_results_diesel.columns)

df_melted_60 = df_results_60.melt(
    id_vars=["origin_code", "destination_code", "w_factor"],
    value_vars=["co2", "air_pollution", "total_externality"],
    var_name="cost",
    value_name="value"
)
df_melted_60["speed"] = "60 mph"

df_melted_45 = df_results_45.melt(
    id_vars=["origin_code", "destination_code", "w_factor"],
    value_vars=["co2", "air_pollution", "total_externality"],
    var_name="cost",
    value_name="value"
)
df_melted_45["speed"] = "45 mph"

df_melted_diesel = df_results_diesel.melt(
    id_vars=["origin_code", "destination_code", "w_factor"],
    value_vars=["co2", "air_pollution", "total_externality"],
    var_name="cost",
    value_name="value"
)
df_melted_diesel["speed"] = "diesel"

df_combined = pd.concat([df_melted_60, df_melted_45, df_melted_diesel], ignore_index=True)
df_combined['int_weight'] = np.round(df_combined['w_factor']).astype(int)

def repeat_rows(df, weight_col):
    return df.loc[df.index.repeat(df[weight_col])].reset_index(drop=True)
repeat_df = repeat_rows(df_combined, 'int_weight')

## color
custom_palette = {
    "45 mph": "#00CD6C",
    "50 mph": "#009ADE",
    "55 mph": "#FFC61E",
    "60 mph": "#FF1F58",
    "diesel": "#F28522"
}

##############
# Print numbers
cost_stats = repeat_df.groupby(["cost", "speed"])["value"].agg(
    median="median",
    q1=lambda x: x.quantile(0.25),
    q3=lambda x: x.quantile(0.75)).reset_index()
print(cost_stats)

##############
## plot in 3 separate charts
cost_vars = ["co2", "air_pollution", "total_externality"]
titles = ["GHG (2025 marginal emissions)", "Air pollution", "Total externality"]

fig, axes = plt.subplots(1, 3, figsize=(15, 5), sharey=True)

for i, cost in enumerate(cost_vars):
    sns.boxplot(
        x="speed",
        y="value",
        data=repeat_df[repeat_df["cost"] == cost],
        ax=axes[i],
        palette=custom_palette,
        showfliers=False
    )
    axes[i].set_title("")
    axes[i].set_xlabel(titles[i], fontsize=18)
    axes[i].set_ylabel("Externality ($ per route)" if i == 0 else "", fontsize=18)
    axes[i].tick_params(axis='x', labelsize=18)
    axes[i].tick_params(axis='y', labelsize=18)
    axes[i].grid(False)
    axes[i].set_facecolor("white")
    axes[i].spines["top"].set_visible(False)
    axes[i].spines["right"].set_visible(False)

fig.tight_layout()
plt.savefig("results/SVG/emissions_split_2025.svg", format='svg', transparent=True)
plt.show()
