import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt
from Filepath.filepath import workspace_folder

os.chdir(workspace_folder)

### Location data
df_results_60 = pd.read_csv('results/power_emission_60_per_route_co2timeline.csv')
df_results_55 = pd.read_csv('results/power_emission_55_per_route_co2timeline.csv')
df_results_50 = pd.read_csv('results/power_emission_50_per_route_co2timeline.csv')
df_results_45 = pd.read_csv('results/power_emission_45_per_route_co2timeline.csv')
df_results_diesel = pd.read_csv('results/diesel_damage_per_route.csv')

df_melted_60 = df_results_60.melt(
    id_vars=["origin_code", "destination_code", "w_factor"],
    value_vars=["externality_2025", "externality_2030", "externality_2035", "externality_2040", "externality_2045", "externality_2050"],
    var_name="timeline",
    value_name="value"
)
df_melted_60["speed"] = "60 mph"
df_melted_60['int_weight'] = np.round(df_melted_60['w_factor']).astype(int)

df_melted_45 = df_results_45.melt(
    id_vars=["origin_code", "destination_code", "w_factor"],
    value_vars=["externality_2025", "externality_2030", "externality_2035", "externality_2040", "externality_2045", "externality_2050"],
    var_name="timeline",
    value_name="value"
)
df_melted_45["speed"] = "45 mph"
df_melted_45['int_weight'] = np.round(df_melted_45['w_factor']).astype(int)

df_results_diesel['externality_2025'] = df_results_diesel['total_externality']
df_results_diesel['externality_2030'] = df_results_diesel['total_externality']
df_results_diesel['externality_2035'] = df_results_diesel['total_externality']
df_results_diesel['externality_2040'] = df_results_diesel['total_externality']
df_results_diesel['externality_2045'] = df_results_diesel['total_externality']
df_results_diesel['externality_2050'] = df_results_diesel['total_externality']
df_melted_diesel = df_results_diesel.melt(
    id_vars=["origin_code", "destination_code", "w_factor"],
    value_vars=["externality_2025", "externality_2030", "externality_2035", "externality_2040", "externality_2045", "externality_2050"],
    var_name="timeline",
    value_name="value"
)
df_melted_diesel["speed"] = "diesel"
df_melted_diesel['int_weight'] = np.round(df_melted_diesel['w_factor']).astype(int)

df_combined = pd.concat([df_melted_60, df_melted_45, df_melted_diesel], ignore_index=True)
df_combined['int_weight'] = np.round(df_combined['w_factor']).astype(int)

def repeat_rows(df, weight_col):
    return df.loc[df.index.repeat(df[weight_col])].reset_index(drop=True)
repeat_df = repeat_rows(df_combined, 'int_weight')
repeat_df_60 = repeat_rows(df_melted_60, 'int_weight')
repeat_df_45 = repeat_rows(df_melted_45, 'int_weight')
repeat_df_diesel = repeat_rows(df_melted_diesel, 'int_weight')


##############
# Print numbers
timeline_stats = repeat_df.groupby(["timeline", "speed"])["value"].agg(
    median="median",
    q1=lambda x: x.quantile(0.25),
    q3=lambda x: x.quantile(0.75)
).reset_index()
print(timeline_stats.sort_values(["timeline", "speed"]))
##############

## color
custom_palette = {
    "45 mph": "#00CD6C",
    "50 mph": "#009ADE",
    "55 mph": "#FFC61E",
    "60 mph": "#FF1F58",
    "diesel": "#F28522"
}

### Line to show timeline
# List of your dataframes
dfs = [repeat_df_60, repeat_df_45, repeat_df_diesel]
labels = ['60 mph', '45 mph', 'diesel']

plt.figure(figsize=(7, 5))
for df, label in zip(dfs, labels):
    median_values = df.groupby("timeline")["value"].median()
    years = median_values.index.str.extract(r'externality_(\d+)', expand=False).astype(int)
    plt.plot(years, median_values.values, marker='o', label=label, color=custom_palette[label])

plt.title('', fontsize=18, fontweight='bold')
plt.xlabel('', fontsize=18)
plt.ylabel('Median total externality ($/route)', fontsize=18)
plt.xticks(fontsize=18)
plt.yticks(fontsize=18)
plt.grid(False)
plt.gca().set_facecolor("white")
plt.gca().spines["top"].set_visible(False)
plt.gca().spines["right"].set_visible(False)
#plt.legend(title="Speed", fontsize=18, title_fontsize=18)
plt.savefig("results/SVG/emissions_timeline.svg", format='svg', transparent=True)
plt.tight_layout()
plt.show()
