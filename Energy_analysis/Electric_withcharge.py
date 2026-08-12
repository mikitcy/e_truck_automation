import numpy as np
import pandas as pd

def get_motor_eff(load_factors):
    # NREL FastSim Nissan Leaf 30kWh (80kW max)
    conditions = [
        load_factors <= 0, #1
        (load_factors > 0) & (load_factors <= 0.02), #0.84
        (load_factors > 0.02) & (load_factors <= 0.04), #0.86
        (load_factors > 0.04) & (load_factors <= 0.08), #0.88
        (load_factors > 0.08) & (load_factors <= 0.1), #0.91
        (load_factors > 0.1) & (load_factors <= 0.2), #0.92
        (load_factors > 0.2) & (load_factors <= 0.4), #0.94
        (load_factors > 0.4) & (load_factors <= 0.8), #0.95
        (load_factors > 0.8) & (load_factors <= 0.1), #0.94
        load_factors > 1  #0.93
    ]
    choices = [1, 0.84, 0.86, 0.88, 0.91, 0.92, 0.94, 0.95, 0.94, 0.93]
    return np.select(conditions, choices, default=0.95)

def get_charge_scenarios(rt_route, rt_leg, battery_kwh, hw_ramping, hw_ramping_up, hw_ramping_down,
                         hw_cruise, ordist_ramping, ordist_ramping_up, ordist_ramping_down, ordist_cruise):
    """Calculate necessary battery capacity for given highway routes."""
    rt_route_results = rt_route.copy()

    # Constants
    capacity = battery_kwh  # Initial estimate of capacity needed in kWh
    packing_f = 0.48  # Battery packing factor
    energy_d = 0.243  # Cell energy density in kWh/kg
    Crr = 0.0063  # Rolling friction coefficient
    Area_f = 7.2  # Average frontal area of truck (m²)
    Cd = 0.63  # Drag coefficient for truck
    empty_vehicle_weight = 7000  # kg (empty truck weight)
    payload_weight = 16000  # kg (payload weight)
    battery_roundtrip_efficiency = 0.95
    drivetrain_efficiency = 0.97 #FastSim Transmission efficiency
    consumable_power_portion = 0.85 # battery is charged from 10% to 95%
    charger_efficiency = 0.86 #FASTSim, 86%: Henning Lohse-Busch, M. Duoba, E. Rask, Advanced Powertrain Research facility AVTA Nissan Leaf Testing and Analysis, May 2nd, 2025
    hp_nameplate = 500  # Commercially available hp (VolvoVNR:455hp, BYD:483hp, Kentworth:536hp)

    # Compute initial battery weight
    battery_weight = (capacity / energy_d) / packing_f
    mass = empty_vehicle_weight + battery_weight + payload_weight

    # split t and v
    ramping_v = hw_ramping['velocity'] / 2.237
    ramping_t = hw_ramping['time']
    ramping_v_up = hw_ramping_up['velocity'] / 2.237
    ramping_t_up = hw_ramping_up['time']
    ramping_v_down = hw_ramping_down['velocity'] / 2.237
    ramping_t_down = hw_ramping_down['time']
    cruise_v = hw_cruise['velocity'] / 2.237
    cruise_t = hw_cruise['time']

    # Create time dataframes
    pUDDS_ramping = pd.DataFrame({"time": ramping_t})
    pUDDS_ramping_up = pd.DataFrame({"time": ramping_t_up})
    pUDDS_ramping_down = pd.DataFrame({"time": ramping_t_down})
    pUDDS_cruise = pd.DataFrame({"time": cruise_t})

    ### **Energy calculations for ramping segments**
    a = np.diff(ramping_v) / np.diff(ramping_t)  # Acceleration
    dvdt = np.concatenate(([0], (a[:-1] + a[1:]) / 2, [0]))  # Adjust acceleration values

    # Compute power requirements
    P_Cd = 0.5 * 1.225 * Cd * Area_f * ramping_v ** 3  # Drag power
    P_friction = Crr * mass * 9.81 * ramping_v  # Rolling resistance power
    P_ma = mass * ramping_v * dvdt  # Inertial force power
    total_power_ramping = P_Cd + P_friction + P_ma
    #pUDDS_ramping["power"] = total_power / (0.9 * 0.95)  # Adjust for efficiency

    ### **Energy calculations for ramping UP segments**
    a = np.diff(ramping_v_up) / np.diff(ramping_t_up)  # Acceleration
    dvdt = np.concatenate(([0], (a[:-1] + a[1:]) / 2, [0]))  # Adjust acceleration values

    # Compute power requirements
    P_Cd = 0.5 * 1.225 * Cd * Area_f * ramping_v_up ** 3  # Drag power
    P_friction = Crr * mass * 9.81 * ramping_v_up  # Rolling resistance power
    P_ma = mass * ramping_v_up * dvdt  # Inertial force power
    total_power_ramping_up = P_Cd + P_friction + P_ma
    #pUDDS_ramping_up["power"] = total_power / (0.9 * 0.95)  # Adjust for efficiency

    ### **Energy calculations for ramping DOWN segments**
    a = np.diff(ramping_v_down) / np.diff(ramping_t_down)  # Acceleration
    dvdt = np.concatenate(([0], (a[:-1] + a[1:]) / 2, [0]))  # Adjust acceleration values

    # Compute power requirements
    P_Cd = 0.5 * 1.225 * Cd * Area_f * ramping_v_down ** 3  # Drag power
    P_friction = Crr * mass * 9.81 * ramping_v_down  # Rolling resistance power
    P_ma = mass * ramping_v_down * dvdt  # Inertial force power
    total_power_ramping_down = P_Cd + P_friction + P_ma
    #pUDDS_ramping_down["power"] = total_power / (0.9 * 0.95)  # Adjust for efficiency

    ### **Energy calculations for cruise segments**
    a = np.diff(cruise_v) / np.diff(cruise_t)  # Acceleration
    dvdt = np.concatenate(([0], (a[:-1] + a[1:]) / 2, [0]))

    P_Cd = 0.5 * 1.225 * Cd * Area_f * cruise_v ** 3
    P_friction = Crr * mass * 9.81 * cruise_v
    P_ma = mass * cruise_v * dvdt
    total_power_cruise = P_Cd + P_friction + P_ma
    #pUDDS_cruise["power"] = total_power / (0.9 * 0.95)

    combined_rt_temp_hw = []

    # Iterate over each route
    for k in range(len(rt_route_results)):
        # Extract origin and destination
        origin = str(rt_route_results.iloc[k]["origin_code"])
        dest = str(rt_route_results.iloc[k]["destination_code"])

        # Filter relevant route data
        rt_temp = rt_leg[(rt_leg["origin_code"] == origin) & (rt_leg["destination_code"] == dest)]
        rt_temp_hw = rt_temp[rt_temp["urban"] == 0].reset_index(drop=True)

        for i, row in rt_temp_hw.iterrows():

            remain_kwh = 0
            charge_break = 0

            # **Energy calculations for gradient effect**
            gradient = np.arctan(row["elevation_change"] / row["m"]) if row["m"] > 0 else 0
            gradient = np.nan_to_num(gradient, nan=0)
            gradient = np.clip(gradient, -np.pi / 2, np.pi / 2)
            speed_mps = max(row["speed_mph"] / 2.237, 1e6)  # Prevent division by zero
            E_gradient = (Crr * mass * 9.81 * np.cos(gradient) - mass * 9.81 * np.sin(gradient)) * speed_mps
            E_gradient = np.clip(np.nan_to_num(E_gradient, nan=0.0), -1e6, 1e6)  # Prevent overflow
            if E_gradient < 0:  # Regenerative braking
                E_gradient *= 0.2
            E_gradient = np.nan_to_num(E_gradient, nan=0.0, posinf=0.0, neginf=0.0)
            E_gradient = E_gradient / (battery_roundtrip_efficiency * drivetrain_efficiency * 1000 * 3600) # Convert energy to kWh

            # in P (W)
            hw_dist = rt_temp_hw["m"].sum()
            hw_dist_cruise = hw_dist - ordist_ramping
            trip_time_sec = len(cruise_t) * hw_dist_cruise / ordist_cruise + len(ramping_t)
            P_gradient = (E_gradient * 1000 * 3600) / trip_time_sec  # in Watts

            ##### Ramping and cruising energy (with motor eff)
            # ramping load factor and motor efficiency
            total_power_ramping_with_gradient = total_power_ramping + P_gradient
            hp_ramping = total_power_ramping_with_gradient / 745.7
            load_factors_ramping = hp_ramping / hp_nameplate
            motor_eff_ramping = get_motor_eff(load_factors_ramping)
            # Final power calculation
            pUDDS_ramping["power"] = (total_power_ramping /
                                      (battery_roundtrip_efficiency * drivetrain_efficiency * motor_eff_ramping))  # Divide total power by battery, drivetrain and motor efficiency
            # Apply regenerative braking correction
            pUDDS_ramping.loc[pUDDS_ramping["power"] < 0, "power"] *= 0.2
            # Integrate to find energy (kWh)
            E_forces_ramping = trapz(pUDDS_ramping["power"], pUDDS_ramping["time"]) * 2.778e-7

            # ramping load factor and motor efficiency
            total_power_ramping_up_with_gradient = total_power_ramping_up + P_gradient
            hp_ramping_up = total_power_ramping_up_with_gradient / 745.7
            load_factors_ramping_up = hp_ramping_up / hp_nameplate
            motor_eff_ramping_up = get_motor_eff(load_factors_ramping_up)
            # Final power calculation
            pUDDS_ramping_up["power"] = (total_power_ramping_up /
                                         (battery_roundtrip_efficiency * drivetrain_efficiency * motor_eff_ramping_up))  # Divide total power by battery, drivetrain and motor efficiency
            # Apply regenerative braking correction
            pUDDS_ramping_up.loc[pUDDS_ramping_up["power"] < 0, "power"] *= 0.2
            # Integrate to find energy (kWh)
            E_forces_ramping_up = trapz(pUDDS_ramping_up["power"], pUDDS_ramping_up["time"]) * 2.778e-7

            # ramping load factor and motor efficiency
            total_power_ramping_down_with_gradient = total_power_ramping_down + P_gradient
            hp_ramping_down = total_power_ramping_down_with_gradient / 745.7
            load_factors_ramping_down = hp_ramping_down / hp_nameplate
            motor_eff_ramping_down = get_motor_eff(load_factors_ramping_down)
            # Final power calculation
            pUDDS_ramping_down["power"] = (total_power_ramping_down /
                                           (battery_roundtrip_efficiency * drivetrain_efficiency * motor_eff_ramping_down))  # Divide total power by battery, drivetrain and motor efficiency
            # Apply regenerative braking correction
            pUDDS_ramping_down.loc[pUDDS_ramping_down["power"] < 0, "power"] *= 0.2
            # Integrate to find energy (kWh)
            E_forces_ramping_down = trapz(pUDDS_ramping_down["power"], pUDDS_ramping_down["time"]) * 2.778e-7

            # cruise load factor and motor efficiency
            total_power_cruise_with_gradient = total_power_cruise + P_gradient
            hp_cruise = total_power_cruise_with_gradient / 745.7
            load_factors_cruise = hp_cruise / hp_nameplate
            motor_eff_cruise = get_motor_eff(load_factors_cruise)
            pUDDS_cruise["hp_cruise"] = hp_cruise
            pUDDS_cruise["load_factor_cruise"] = load_factors_cruise
            pUDDS_cruise["motor_eff_cruise"] = motor_eff_cruise
            # Final power calculation
            pUDDS_cruise["power"] = (total_power_cruise /
                                     (battery_roundtrip_efficiency * drivetrain_efficiency * motor_eff_cruise))  # Divide total power by battery, drivetrain and motor efficiency
            # Apply regenerative braking
            pUDDS_cruise.loc[pUDDS_cruise["power"] < 0, "power"] *= 0.2
            # Integrate power to find energy (kWh)
            E_forces_cruise = trapz(pUDDS_cruise["power"], pUDDS_cruise["time"]) * 2.778e-7
            E_forces_cruise_per_m = E_forces_cruise / ordist_cruise

            # Apply motor eff to E_gradient
            E_gradient = E_gradient * np.mean(motor_eff_cruise)

            if i == 0:
                for j in range(0, 100): #first leg
                    E_forces_cruise = E_forces_cruise_per_m * (row['m'] - ordist_ramping_up - j * ordist_ramping)
                    E_forces_ramping_total = E_forces_ramping_up + j * E_forces_ramping
                    needed_energy_kwh = E_forces_ramping_total + E_forces_cruise + E_gradient

                    if needed_energy_kwh < ((battery_kwh * consumable_power_portion) * (j + 1)): # Charge at 10% energy remaining; battery use: 95->10%
                        remain_kwh = max((battery_kwh * consumable_power_portion) * (j + 1) - needed_energy_kwh, 0)
                        charge_break = j
                        break

            elif i == len(rt_temp_hw) - 1: #last leg
                remain_kwh = rt_temp_hw.at[i - 1, "remain_kwh"]
                for j in range(0, 100):
                    E_forces_cruise = E_forces_cruise_per_m * (row['m'] - ordist_ramping_down - j * ordist_ramping)
                    E_forces_ramping_total = E_forces_ramping_down + j * E_forces_ramping
                    needed_energy_kwh = E_forces_ramping_total + E_forces_cruise + E_gradient

                    adjusted_needed_energy_kwh = needed_energy_kwh + (battery_kwh * consumable_power_portion - remain_kwh) #battery use: 95->10%

                    if adjusted_needed_energy_kwh < ((battery_kwh * consumable_power_portion) * (j + 1)): # Charge at 10% energy remaining
                        remain_kwh = max((battery_kwh * consumable_power_portion) * (j + 1) - adjusted_needed_energy_kwh, 0)
                        charge_break = j
                        break

            else: #middle legs
                remain_kwh = rt_temp_hw.at[i - 1, "remain_kwh"]
                for j in range(0, 100):
                    E_forces_cruise = E_forces_cruise_per_m * (row['m'] - j * ordist_ramping)
                    E_forces_ramping_total = j * E_forces_ramping
                    needed_energy_kwh = E_forces_ramping_total + E_forces_cruise + E_gradient

                    adjusted_needed_energy_kwh = needed_energy_kwh + (battery_kwh * consumable_power_portion - remain_kwh)

                    if adjusted_needed_energy_kwh < ((battery_kwh * consumable_power_portion) * (j + 1)):  # Charge at 10% energy remaining
                        remain_kwh = max((battery_kwh * consumable_power_portion) * (j + 1) - adjusted_needed_energy_kwh, 0)
                        charge_break = j
                        break

            rt_temp_hw.at[i, "remain_kwh"] = remain_kwh
            rt_temp_hw.at[i, "needed_energy_kwh"] = needed_energy_kwh
            rt_temp_hw.at[i, "E_forces_cruise"] = E_forces_cruise
            rt_temp_hw.at[i, "E_forces_ramping_total"] = E_forces_ramping_total
            rt_temp_hw.at[i, "E_gradient"] = E_gradient
            rt_temp_hw.at[i, "charge_break"] = charge_break
            rt_temp_hw.at[i, "hp_99_ramping"] = np.percentile(hp_ramping,99)
            rt_temp_hw.at[i, "hp_99_cruise"] = np.percentile(hp_cruise, 99)
            rt_temp_hw.at[i, "motor_eff_50_cruise"] = np.percentile(motor_eff_cruise, 50)
            rt_temp_hw.at[i, "motor_eff_50_ramping"] = np.percentile(motor_eff_ramping, 50)
            rt_temp_hw.at[i, "motor_eff_mean_cruise"] = motor_eff_cruise.mean()
            rt_temp_hw.at[i, "motor_eff_mean_ramping"] = motor_eff_ramping.mean()
            #pUDDS_cruise.to_csv(f"results/pUDDS_cruise_{origin}_{dest}.csv", index=False)
            print(f"Route {origin} -> {dest}: Charge break {charge_break}, needed_energy_kwh: {needed_energy_kwh}")

        combined_rt_temp_hw.append(rt_temp_hw)

    final_rt_temp_hw = pd.concat(combined_rt_temp_hw, ignore_index=True)

    needed_energy_summary = final_rt_temp_hw.groupby(["origin_code", "destination_code"])[
        "needed_energy_kwh"].sum().reset_index()
    rt_route_results_merge = rt_route_results.merge(needed_energy_summary, on=["origin_code", "destination_code"], how="left")
    rt_route_results_merge["needed_energy_kwh"] = rt_route_results_merge["needed_energy_kwh"].fillna(0)

    charge_break_summary = final_rt_temp_hw.groupby(["origin_code", "destination_code"])[
        "charge_break"].sum().reset_index()
    rt_route_results_merge2 = rt_route_results_merge.merge(charge_break_summary, on=["origin_code", "destination_code"], how="left")
    rt_route_results_merge2["charge_break"] = rt_route_results_merge2["charge_break"].fillna(0)

    return rt_route_results_merge2, final_rt_temp_hw
