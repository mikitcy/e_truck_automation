import pandas as pd
import os

from Externality.Diesel_emissions import diesel_tailpipe_emissions, diesel_upstream_emissions, diesel_total_emissions
from Externality.Emissions_weight import emissions_weight
from Externality.Vehicle_cycle_emissions import get_vehicle_emissions_diesel
from Externality.Total_externality import get_total_externality
from Filepath.filepath import workspace_folder

os.chdir(workspace_folder)

df_results = pd.read_csv("results/diesel_md_weighted_osrm.csv")

# Get total damage per route
# Upstream md prep
df_MD_diesel = pd.read_csv("emissions/MD_diesel.csv") #USD/ton
#adjust statistical value of life, 2000$/ton -> 2024$/ton
df_MD_diesel["pm25_md"] = df_MD_diesel["pm25_md"].astype(float) * 13.7 / 6
df_MD_diesel["nox_md"] = df_MD_diesel["nox_md"].astype(float) * 13.7 / 6
df_MD_diesel["so2_md"] = df_MD_diesel["so2_md"].astype(float) * 13.7 / 6

# total emission calc
df_results = diesel_tailpipe_emissions(df_results, 190)
df_results = diesel_upstream_emissions(df_results, df_MD_diesel,190)
df_results = diesel_total_emissions(df_results)

# Weight factor per shipped weight
df_weight = pd.read_csv("weight_factor_rev.csv")
df_results = emissions_weight(df_results, df_weight)

# Get vehicle cycle emissions
df_results = get_vehicle_emissions_diesel(df_results)

# Get total costs
df_results = get_total_externality(df_results)

df_results.to_csv("results/diesel_damage_per_route.csv", index=False)
