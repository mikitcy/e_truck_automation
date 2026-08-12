import pandas as pd
import os

from Externality.Grid_emissions import emissions_damage_waypoints, emissions_damage_entrance, grid_emissions_damage_total
from Externality.Emissions_weight import emissions_weight
from Externality.Vehicle_cycle_emissions import get_vehicle_emissions_electric
from Externality.Total_externality import get_total_externality
from Filepath.filepath import workspace_folder

os.chdir(workspace_folder)

### Location data
rt_leg_charge_45 = pd.read_csv('results/rt_leg_charge_45_location.csv')
rt_leg_charge_60 = pd.read_csv('results/rt_leg_charge_60_location.csv')
print(rt_leg_charge_60.columns)

battery_kwh = 500

#Damage factor data and inputs
md_df = pd.read_csv("emissions/MD_power_pivot.csv") #$/MWh
df_gea = pd.read_csv("shape/county_to_gea_mapping_cambium23.csv")
shapefile_path = "shape/cb_2018_us_county_500k.zip"

### EF damage calc - power emissions
df_60 = emissions_damage_waypoints(rt_leg_charge_60, shapefile_path, df_gea, md_df)
df_60 = emissions_damage_entrance(df_60, shapefile_path, df_gea, md_df)

df_45 = emissions_damage_waypoints(rt_leg_charge_45, shapefile_path, df_gea, md_df)
df_45 = emissions_damage_entrance(df_45, shapefile_path, df_gea, md_df)

### Cost calculate per route
df_60, df_results_60 = grid_emissions_damage_total(df_60, battery_kwh)
df_45, df_results_45 = grid_emissions_damage_total(df_45, battery_kwh)

df_60.to_csv("results/power_emission_60.csv", index=False)
df_45.to_csv("results/power_emission_45.csv", index=False)

### Add vehicle cycle emissions
df_results_60 = get_vehicle_emissions_electric(df_results_60, battery_kwh)
df_results_45 = get_vehicle_emissions_electric(df_results_45, battery_kwh)

### Get total cost
df_results_60 = get_total_externality(df_results_60)
df_results_45 = get_total_externality(df_results_45)

# Weight factor per shipped weight
df_weight = pd.read_csv("weight_factor_rev.csv")
df_results_60 = emissions_weight(df_results_60, df_weight)
df_results_45 = emissions_weight(df_results_45, df_weight)

df_results_60.to_csv('results/power_emission_60_per_route.csv')
df_results_45.to_csv('results/power_emission_45_per_route.csv')

