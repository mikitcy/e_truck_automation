import pandas as pd
import os

from Externality.Emissions_weight import emissions_weight
from Externality.Grid_emissions_timeline import grid_emission_timeline
from Externality.Vehicle_cycle_emissions import get_vehicle_emissions_electric_timeline
from Externality.Total_externality import get_total_externality_timeline
from Filepath.filepath import workspace_folder

os.chdir(workspace_folder)

### Emission data per leg
df_60 = pd.read_csv("results/power_emission_60.csv")
df_55 = pd.read_csv("results/power_emission_55.csv")
df_50 = pd.read_csv("results/power_emission_50.csv")
df_45 = pd.read_csv("results/power_emission_45.csv")

#Damage factor data
md_df = pd.read_csv("emissions/MD_power_pivot.csv")
md_df_timeline = pd.read_csv("emissions/MD_power_pivot_timeline.csv")

# Add emission timeline, using the fraction change over 2025-2050
battery_kwh = 500
df_60, df_results_60 = grid_emission_timeline(df_60, md_df_timeline, battery_kwh)
df_55, df_results_55 = grid_emission_timeline(df_55, md_df_timeline, battery_kwh)
df_50, df_results_50 = grid_emission_timeline(df_50, md_df_timeline, battery_kwh)
df_45, df_results_45 = grid_emission_timeline(df_45, md_df_timeline, battery_kwh)
print(df_results_45.columns)

# Weight factor per shipped weight
df_weight = pd.read_csv("weight_factor_rev.csv")
df_results_60 = emissions_weight(df_results_60, df_weight)
df_results_55 = emissions_weight(df_results_55, df_weight)
df_results_50 = emissions_weight(df_results_50, df_weight)
df_results_45 = emissions_weight(df_results_45, df_weight)

# Add vehicle cycle emissions
battery_kwh = 500
df_60_notimeline = pd.read_csv('results/power_emission_60_per_route.csv') #rejoin mile and air_pollutant column
df_60_notimeline = df_60_notimeline[['origin_code', 'destination_code', 'miles', 'air_pollution']]
df_55_notimeline = pd.read_csv('results/power_emission_55_per_route.csv') #rejoin mile and air_pollutant column
df_55_notimeline = df_55_notimeline[['origin_code', 'destination_code', 'miles', 'air_pollution']]
df_50_notimeline = pd.read_csv('results/power_emission_50_per_route.csv') #rejoin mile and air_pollutant column
df_50_notimeline = df_50_notimeline[['origin_code', 'destination_code', 'miles', 'air_pollution']]
df_45_notimeline = pd.read_csv('results/power_emission_45_per_route.csv') #rejoin mile and air_pollutant column
df_45_notimeline = df_45_notimeline[['origin_code', 'destination_code', 'miles', 'air_pollution']]
df_results_60 = df_results_60.merge(df_60_notimeline, on=["origin_code", "destination_code"], how="left")
df_results_55 = df_results_55.merge(df_55_notimeline, on=["origin_code", "destination_code"], how="left")
df_results_50 = df_results_50.merge(df_50_notimeline, on=["origin_code", "destination_code"], how="left")
df_results_45 = df_results_45.merge(df_45_notimeline, on=["origin_code", "destination_code"], how="left")

df_results_60 = get_vehicle_emissions_electric_timeline(df_results_60, battery_kwh)
df_results_55 = get_vehicle_emissions_electric_timeline(df_results_55, battery_kwh)
df_results_50 = get_vehicle_emissions_electric_timeline(df_results_50, battery_kwh)
df_results_45 = get_vehicle_emissions_electric_timeline(df_results_45, battery_kwh)

df_results_60 = get_total_externality_timeline(df_results_60)
df_results_55 = get_total_externality_timeline(df_results_55)
df_results_50 = get_total_externality_timeline(df_results_50)
df_results_45 = get_total_externality_timeline(df_results_45)

df_60.to_csv("results/power_emission_60_co2timeline.csv", index=False)
df_55.to_csv("results/power_emission_55_co2timeline.csv", index=False)
df_50.to_csv("results/power_emission_50_co2timeline.csv", index=False)
df_45.to_csv("results/power_emission_45_co2timeline.csv", index=False)
df_results_60.to_csv('results/power_emission_60_per_route_co2timeline.csv')
df_results_55.to_csv('results/power_emission_55_per_route_co2timeline.csv')
df_results_50.to_csv('results/power_emission_50_per_route_co2timeline.csv')
df_results_45.to_csv('results/power_emission_45_per_route_co2timeline.csv')

