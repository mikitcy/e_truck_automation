import pandas as pd
import os
import numpy as np
from datetime import datetime

from Drive_profile.Drive_profile import process_drive_cycle
from Energy_analysis.Electric_nocharge import calculate_battery_capacity
from Energy_analysis.Time import calculate_duration_nocharge, add_break_time
from Filepath.filepath import workspace_folder

os.chdir(workspace_folder)

### Route data
rt = pd.read_csv("rt_final.csv")
rt_lengths = rt[["origin_code", "destination_code", "miles"]]
rt_lengths = rt_lengths.groupby(["origin_code", "destination_code"], as_index=False).agg({"miles": "sum"}).rename(columns={"miles": "length"})
rt = rt.merge(rt_lengths, on=["origin_code", "destination_code"], how="left")

# Create 'over_150' column
rt["over_150"] = (rt["length"] >= 150).astype(int)
rt = rt[rt["over_150"] == 1]

rt_all = rt.groupby(["origin_code", "destination_code"], as_index=False).agg({"miles": "sum"})
rt_all["meters"] = rt_all["miles"] * 1609.34
rt_all_depot = pd.DataFrame(np.zeros((1, 23)))
rt_highway = rt[rt["urban"] == 0]
print(rt_all)

### Driving profile
file_path = "heavytruck_cruise_drivecycle.csv"
(hw_ramping_up_60, hw_cruise_60, hw_ramping_down_60, hw_ramping_60,
 ordist_cruise_60, ordist_ramping_60, ordist_ramping_up_60, ordist_ramping_down_60) = process_drive_cycle(file_path, 60)
(hw_ramping_up_45, hw_cruise_45, hw_ramping_down_45, hw_ramping_45,
 ordist_cruise_45, ordist_ramping_45, ordist_ramping_up_45, ordist_ramping_down_45) = process_drive_cycle(file_path, 45)

### Electric power usage and battery size analysis
print(datetime.now())
rt_all_60 = calculate_battery_capacity(rt_all, rt_highway, hw_ramping_60, hw_cruise_60, ordist_ramping_60, ordist_cruise_60)
rt_all_60.to_csv('results/rt_all_60.csv', index=False)
rt_all_45 = calculate_battery_capacity(rt_all, rt_highway, hw_ramping_45, hw_cruise_45, ordist_ramping_45, ordist_cruise_45)
rt_all_45.to_csv('results/rt_all_45.csv', index=False)
print(datetime.now())

print("60mph cruise",np.percentile(rt_all_60["hp_99_cruise"], 99))
print("60mph ramp",np.percentile(rt_all_60["hp_99_ramping"], 99))
print("45mph cruise",np.percentile(rt_all_45["hp_99_cruise"], 99))
print("45mph ramp",np.percentile(rt_all_45["hp_99_ramping"], 99))

rt_all_60_time = calculate_duration_nocharge(rt_all, rt_highway, hw_ramping_60, hw_cruise_60, ordist_ramping_60, ordist_cruise_60)
rt_all_60_time.to_csv('results/rt_all_60_time.csv', index=False)
rt_all_45_time = calculate_duration_nocharge(rt_all, rt_highway, hw_ramping_45, hw_cruise_45, ordist_ramping_45, ordist_cruise_45)
rt_all_45_time.to_csv('results/rt_all_45_time.csv', index=False)

rt_all_60_time_with_break = add_break_time(rt_all_60_time)
rt_all_60_time_with_urban = add_urban_time(rt_all_60_time_with_break, rt)
rt_all_55_time_with_urban.to_csv('results/rt_all_60_time_with_break_urban.csv', index=False)