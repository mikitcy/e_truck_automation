import numpy as np

def calculate_duration_nocharge(rt_route, rt_leg, hw_ramping, hw_cruise, ordist_ramping, ordist_cruise):
    rt_route_results = rt_route.copy()
    ramping_v = hw_ramping['velocity'] / 2.237
    ramping_t = hw_ramping['time']
    cruise_v = hw_cruise['velocity'] / 2.237
    cruise_t = hw_cruise['time']

    for i in range(len(rt_route_results)):
        # Extract origin and destination
        origin = str(rt_route_results.iloc[i]["origin_code"])
        dest = str(rt_route_results.iloc[i]["destination_code"])

        # Filter relevant route data
        rt_temp = rt_leg[(rt_leg["origin_code"] == origin) & (rt_leg["destination_code"] == dest)]
        rt_temp_hw = rt_temp[rt_temp["urban"] == 0]

        # Compute highway distance
        hw_dist = rt_temp_hw["m"].sum()
        hw_dist_cruise = hw_dist - ordist_ramping

        # calculate time for hw segment
        time_ramp = ((238 - 20) + (2083 - 1571)) / 60  #initial ramp + final ramp, in minutes
        cumulative_cruise_v = np.cumsum(cruise_v)
        total_cruise_distance = np.max(cumulative_cruise_v)
        total_cruise_time = np.max(cruise_t)

        N = np.floor(hw_dist_cruise / total_cruise_distance)
        remaining_distance = hw_dist_cruise % total_cruise_distance

        time_cruise_remaining = np.where(cumulative_cruise_v >= remaining_distance)[0][0] + 1  # +1 for correct indexing

        time_cruise = (N * total_cruise_time + time_cruise_remaining) / 60
        time_hw = time_ramp + time_cruise # in minutes

        row_index = rt_route_results.index[i]
        rt_route_results.at[row_index, 'time_hw'] = time_hw

    return rt_route_results

def calculate_duration_with_charge(rt_route_charge, rt_leg, battery_kwh, charger_kw, hw_ramping, hw_cruise, ordist_ramping, ordist_cruise):
    rt_route_results = rt_route_charge.copy()
    ramping_v = hw_ramping['velocity'] / 2.237
    ramping_t = hw_ramping['time']
    cruise_v = hw_cruise['velocity'] / 2.237
    cruise_t = hw_cruise['time']

    for i in range(len(rt_route_results)):
        # Extract origin and destination
        origin = str(rt_route_results.iloc[i]["origin_code"])
        dest = str(rt_route_results.iloc[i]["destination_code"])

        # Filter relevant route data
        rt_temp = rt_leg[(rt_leg["origin_code"] == origin) & (rt_leg["destination_code"] == dest)]
        rt_temp_hw = rt_temp[rt_temp["urban"] == 0]

        # Compute highway distance
        hw_dist = rt_temp_hw["m"].sum()
        charge_break = rt_route_charge.iloc[i]["charge_break"]
        hw_dist_cruise = hw_dist - ordist_ramping * (charge_break + 1)

        # calculate time for hw segment
        time_ramp = ((238 - 20) + (2083 - 1571)) / 60  #initial ramp + final ramp, in minutes
        cumulative_cruise_v = np.cumsum(cruise_v)
        total_cruise_distance = np.max(cumulative_cruise_v)
        total_cruise_time = np.max(cruise_t)

        N = np.floor(hw_dist_cruise / total_cruise_distance)
        remaining_distance = hw_dist_cruise % total_cruise_distance
        time_cruise_remaining = np.where(cumulative_cruise_v >= remaining_distance)[0][0] + 1  # +1 for correct indexing
        time_cruise = (N * total_cruise_time + time_cruise_remaining) / 60

        consumable_power_portion = 0.85  # battery is charged from 10% to 95%
        charger_efficiency = 0.86  # FASTSim, 86%: Henning Lohse-Busch, M. Duoba, E. Rask, Advanced Powertrain Research facility AVTA Nissan Leaf Testing and Analysis, May 2nd, 2025
        time_charge = (battery_kwh * consumable_power_portion / charger_efficiency / charger_kw * 60) * charge_break #Charge from 10% till 95% full

        time_total = time_ramp + time_cruise + time_charge # in minutes

        rt_route_results.at[i, 'time_total'] = time_total
        rt_route_results.at[i, 'time_charge'] = time_charge

    return rt_route_results

def add_break_time(df):
    drive_time = df['time_hw']
    break_after_shift = 630 # 10H rest after 14H shift or 11H driving + 30mins rest after 8H consecutive drive
    shift_max = 660 # 11H driving limit (with 30min rest after 8H, then 3H drive)

    shift_count = np.floor(drive_time / shift_max)
    remaining = drive_time - shift_count * shift_max
    final_short_break = np.where(remaining > 480, 30, 0) # 30min rest after 8H
    total_break = shift_count * break_after_shift + final_short_break

    df['time_break'] = total_break
    df['time_total'] = drive_time + total_break

    return df

