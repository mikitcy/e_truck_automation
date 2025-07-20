import pandas as pd
import os
from Map.Map_route import create_osmr_map, get_route
from Filepath.filepath import workspace_folder

os.chdir(workspace_folder)

# City codes
Chicago = "17-176"
LA = "6-348"
NY = "36-408"

# Speed
df_60 = pd.read_csv('results/rt_leg_charge_60_location.csv')
df_45 = pd.read_csv('results/rt_leg_charge_45_location.csv')

df_filtered_60 = df_60[(df_60['origin_code'] == Chicago) & (df_60['destination_code'] == NY)]
df_filtered_45 = df_45[(df_45['origin_code'] == Chicago) & (df_45['destination_code'] == NY)]

create_osmr_map(df_filtered_60, plot_color="pink", save_path="results/CHI-NY_map_60.html")
create_osmr_map(df_filtered_45, plot_color="green", save_path="results/CHI-NY_map_45.html")

# Battery size
df_1000 = pd.read_csv('results/rt_leg_charge_60_1000_location.csv')
df_250 = pd.read_csv('results/rt_leg_charge_60_250_location.csv')

df_filtered_1000 = df_1000[(df_1000['origin_code'] == Chicago) & (df_1000['destination_code'] == NY)]
df_filtered_250 = df_250[(df_250['origin_code'] == Chicago) & (df_250['destination_code'] == NY)]

create_osmr_map(df_filtered_1000, plot_color="pink", save_path="results/CHI-NY_map_1000.html")
create_osmr_map(df_filtered_250, plot_color="green", save_path="results/CHI-NY_map_250.html")