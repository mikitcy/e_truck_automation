import pandas as pd
import os
from Filepath.filepath import workspace_folder
from Map.H3_map import h3_map, h3_map_diff_pct, get_all_coordinates, weight_routes

os.chdir(workspace_folder)

rt_leg_charge_45 = pd.read_csv('results/power_emission_45.csv')
rt_leg_charge_60 = pd.read_csv('results/power_emission_60.csv')
rt_leg_charge_45["w_factor"] = rt_leg_charge_45["miles"] * rt_leg_charge_45["w_factor"]
rt_leg_charge_60["w_factor"] = rt_leg_charge_60["miles"] * rt_leg_charge_60["w_factor"]

rt_leg_charge_45 = weight_routes(rt_leg_charge_45, cum_pct=99)
rt_leg_charge_60 = weight_routes(rt_leg_charge_60, cum_pct=99)

df45 = get_all_coordinates(rt_leg_charge_45)
df60 = get_all_coordinates(rt_leg_charge_60)

lon_col = "charge_lon"
lat_col = "charge_lat"

map45 = h3_map(df45, lon_col, lat_col, 4)
map45.save("results/h3_hex_map_45.html")

map60 = h3_map(df60, lon_col, lat_col, 4)
map60.save("results/h3_hex_map_60.html")

map_delta = h3_map_diff_pct(df45, df60, resolution=4)
map_delta.save("results/h3_hex_map_delta.html")