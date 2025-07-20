import pandas as pd
import os
import numpy as np
from datetime import datetime

from Drive_profile.Drive_profile import process_drive_cycle
from Energy_analysis.Electric_withcharge import get_charge_scenarios
from Energy_analysis.Time import calculate_duration_with_charge
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
rt['lon2'] = rt['lon'].shift(-1)
rt['lat2'] = rt['lat'].shift(-1)

rt_all = rt.groupby(["origin_code", "destination_code"], as_index=False).agg({"miles": "sum"})
rt_all["meters"] = rt_all["miles"] * 1609.34
rt_all_depot = pd.DataFrame(np.zeros((1, 23)))
rt_highway = rt[rt["urban"] == 0]
print(rt_all)

### Driving profile
file_path = "heavytruck_cruise_drivecycle.csv"
(hw_ramping_up_60, hw_cruise_60, hw_ramping_down_60, hw_ramping_60,
 ordist_cruise_60, ordist_ramping_60, ordist_ramping_up_60, ordist_ramping_down_60) = process_drive_cycle(file_path, 60)
(hw_ramping_up_55, hw_cruise_55, hw_ramping_down_55, hw_ramping_55,
 ordist_cruise_55, ordist_ramping_55, ordist_ramping_up_55, ordist_ramping_down_55) = process_drive_cycle(file_path, 55)
(hw_ramping_up_50, hw_cruise_50, hw_ramping_down_50, hw_ramping_50,
 ordist_cruise_50, ordist_ramping_50, ordist_ramping_up_50, ordist_ramping_down_50) = process_drive_cycle(file_path, 50)
(hw_ramping_up_45, hw_cruise_45, hw_ramping_down_45, hw_ramping_45,
 ordist_cruise_45, ordist_ramping_45, ordist_ramping_up_45, ordist_ramping_down_45) = process_drive_cycle(file_path, 45)

### Electric power usage and battery size analysis
print(datetime.now())
battery_kwh = 500
(rt_all_45, rt_leg_charge_45) = get_charge_scenarios(rt_all, rt_highway, battery_kwh, hw_ramping_45, hw_ramping_up_45,
                                                     hw_ramping_down_45,hw_cruise_45, ordist_ramping_45, ordist_ramping_up_45, ordist_ramping_down_45, ordist_cruise_45)
rt_all_45.to_csv('results/rt_all_45_charge.csv', index=False)
rt_leg_charge_45.to_csv('results/rt_leg_charge_45.csv', index=False)

(rt_all_60, rt_leg_charge_60) = get_charge_scenarios(rt_all, rt_highway, battery_kwh, hw_ramping_60, hw_ramping_up_60, hw_ramping_down_60,
                                 hw_cruise_60, ordist_ramping_60, ordist_ramping_up_60, ordist_ramping_down_60, ordist_cruise_60)
rt_all_60.to_csv('results/rt_all_60_charge.csv', index=False)
rt_leg_charge_60.to_csv('results/rt_leg_charge_60.csv', index=False)

(rt_all_55, rt_leg_charge_55) = get_charge_scenarios(rt_all, rt_highway, battery_kwh, hw_ramping_55, hw_ramping_up_55, hw_ramping_down_55,
                                 hw_cruise_55, ordist_ramping_55, ordist_ramping_up_55, ordist_ramping_down_55, ordist_cruise_55)
rt_all_55.to_csv('results/rt_all_55_charge.csv', index=False)
rt_leg_charge_55.to_csv('results/rt_leg_charge_55.csv', index=False)

(rt_all_50, rt_leg_charge_50) = get_charge_scenarios(rt_all, rt_highway, battery_kwh, hw_ramping_50, hw_ramping_up_50, hw_ramping_down_50,
                                 hw_cruise_50, ordist_ramping_50, ordist_ramping_up_50, ordist_ramping_down_50, ordist_cruise_50)
rt_all_50.to_csv('results/rt_all_50_charge.csv', index=False)
rt_leg_charge_50.to_csv('results/rt_leg_charge_50.csv', index=False)
print(datetime.now())


### Travel duration analysis
charger_kw = 350
rt_all_45_time = calculate_duration_with_charge(rt_all_45, rt_highway, battery_kwh, charger_kw, hw_ramping_45, hw_cruise_45, ordist_ramping_45, ordist_cruise_45)
rt_all_45_time.to_csv('results/rt_all_45_time_charge.csv', index=False)
rt_all_60_time = calculate_duration_with_charge(rt_all_60, rt_highway, battery_kwh, charger_kw, hw_ramping_60, hw_cruise_60, ordist_ramping_60, ordist_cruise_60)
rt_all_60_time.to_csv('results/rt_all_60_time_charge.csv', index=False)
rt_all_55_time = calculate_duration_with_charge(rt_all_55, rt_highway, battery_kwh, charger_kw, hw_ramping_55, hw_cruise_55, ordist_ramping_55, ordist_cruise_55)
rt_all_55_time.to_csv('results/rt_all_55_time_charge.csv', index=False)
rt_all_50_time = calculate_duration_with_charge(rt_all_50, rt_highway, battery_kwh, charger_kw, hw_ramping_50, hw_cruise_50, ordist_ramping_50, ordist_cruise_50)
rt_all_50_time.to_csv('results/rt_all_50_time_charge.csv', index=False)
print(datetime.now())