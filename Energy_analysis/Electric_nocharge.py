import numpy as np
import pandas as pd
from scipy.integrate import trapz

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

def calculate_battery_capacity(rt_route, rt_leg, hw_ramping, hw_cruise, ordist_ramping, ordist_cruise):
    """Calculate necessary battery capacity for given highway routes."""
    rt_route_results = rt_route.copy()

    # Constants
    capacity = 20000  # Initial estimate of capacity needed in kWh
    packing_f = 0.48  # Battery packing factor
    energy_d = 0.243  # Cell energy density in kWh/kg
    Crr = 0.0063  # Rolling friction coefficient
    Area_f = 7.2  # Average frontal area of truck (m²)
    Cd = 0.63  # Drag coefficient for truck
    empty_vehicle_weight = 7000  # kg (empty truck weight)
    payload_weight = 16000  # kg (payload weight)
    battery_roundtrip_efficiency = 0.95
    drivetrain_efficiency = 0.97  #FastSim Transmission efficiency
    hp_nameplate = 500  #eCascadia:395hp(470peak),BYD:483hp, Kentworth:536hp(670 peak) Lion8:670hp, Nikola:645hp(1069peak), Peterbilt:670hp, VolvoVNR:455hp

    # Compute initial battery weight
    battery_weight = (capacity / energy_d) / packing_f

    # split t and v
    ramping_v = hw_ramping['velocity'] / 2.237
    ramping_t = hw_ramping['time']
    cruise_v = hw_cruise['velocity'] / 2.237
    cruise_t = hw_cruise['time']

    # Iterate over each route
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

        # Create time dataframes
        pUDDS_ramping = pd.DataFrame({"time": ramping_t})
        pUDDS_cruise = pd.DataFrame({"time": cruise_t})

        max_iterations = 1000
        iteration = 0

        while True:  # Infinite loop, breaks when battery weight stabilizes
            iteration += 1
            if iteration > max_iterations:
                print(f"Loop did not converge for route {origin} -> {dest}. Exiting after {max_iterations} iterations.")
                break

            # Calculate total vehicle mass
            mass = empty_vehicle_weight + battery_weight + payload_weight

            # **Energy calculations for ramping segments**
            a = np.diff(ramping_v) / np.diff(ramping_t)  # Acceleration
            dvdt = np.concatenate(([0], (a[:-1] + a[1:]) / 2, [0]))  # Adjust acceleration values

            # Compute power requirements
            P_Cd = 0.5 * 1.225 * Cd * Area_f * ramping_v ** 3  #Calculate power to overcome drag
            P_friction = Crr * mass * 9.81 * ramping_v  #Calculate power to overcome rolling friction
            P_ma = mass * ramping_v * dvdt  #Calculate power to overcome inertial force
            total_power_ramping = P_Cd + P_friction + P_ma
            #pUDDS_ramping["power"] = total_power / (0.9 * 0.95)  #Divide total power by battery and drivetrain efficiency

            # **Energy calculations for cruise segments**
            a = np.diff(cruise_v) / np.diff(cruise_t)  # Acceleration
            dvdt = np.concatenate(([0], (a[:-1] + a[1:]) / 2, [0]))

            P_Cd = 0.5 * 1.225 * Cd * Area_f * cruise_v ** 3
            P_friction = Crr * mass * 9.81 * cruise_v
            P_ma = mass * cruise_v * dvdt
            total_power_cruise = P_Cd + P_friction + P_ma
            #pUDDS_cruise["power"] = total_power / (0.9 * 0.95)

            #####
            # **Energy calculations for gradient effect**
            E_gradient = 0
            for _, row in rt_temp_hw.iterrows():
                gradient = np.arctan(row["elevation_change"] / row["m"]) if row["m"] > 0 else 0
                gradient = np.nan_to_num(gradient, nan=0)
                gradient = np.clip(gradient, -np.pi / 2, np.pi / 2)
                speed_mps = max(row["speed_mph"] / 2.237, 1e6)  # Prevent division by zero

                e_grad_temp = (Crr * mass * 9.81 * np.cos(gradient) - mass * 9.81 * np.sin(gradient)) * speed_mps
                e_grad_temp = np.clip(np.nan_to_num(e_grad_temp, nan=0.0), -1e6, 1e6) # Prevent overflow

                if e_grad_temp < 0:  # Regenerative braking
                    e_grad_temp *= 0.2

                E_gradient += e_grad_temp
                E_gradient = np.nan_to_num(E_gradient, nan=0.0, posinf=0.0, neginf=0.0)

            # Convert energy to kWh
            E_gradient = E_gradient/(battery_roundtrip_efficiency * drivetrain_efficiency * 1000 * 3600)

            # Convert to power
            trip_time_sec = len(cruise_t) * hw_dist_cruise / ordist_cruise + len(ramping_t)
            P_gradient = (E_gradient * 1000 * 3600) / trip_time_sec #in watts
            pUDDS_ramping["P_gradient"] = P_gradient
            pUDDS_cruise["P_gradient"] = P_gradient

            ##############
            # Power to energy
            # ramping load factor and motor efficiency
            total_power_ramping = total_power_ramping + P_gradient
            hp_ramping = total_power_ramping / 745.7
            load_factors_ramping = hp_ramping / hp_nameplate
            motor_eff_ramping = get_motor_eff(load_factors_ramping)
            pUDDS_ramping["hp_ramping"] = hp_ramping
            pUDDS_ramping["load_factor_ramping"] = load_factors_ramping
            pUDDS_ramping["motor_eff_ramping"] = motor_eff_ramping
            # Final power calculation
            pUDDS_ramping["power"] = (total_power_ramping /
                                      (battery_roundtrip_efficiency * drivetrain_efficiency * motor_eff_ramping)) #Divide total power by battery, drivetrain and motor efficiency
            # Apply regenerative braking correction
            pUDDS_ramping.loc[pUDDS_ramping["power"] < 0, "power"] *= 0.2
            # Integrate to find energy (kWh)
            E_forces_ramping = trapz(pUDDS_ramping["power"], pUDDS_ramping["time"]) * 2.778e-7

            # Power to energy
            # cruise load factor and motor efficiency
            total_power_cruise = total_power_cruise + P_gradient
            hp_cruise = total_power_cruise / 745.7
            load_factors_cruise = hp_cruise / hp_nameplate
            motor_eff_cruise = get_motor_eff(load_factors_cruise)
            pUDDS_cruise["hp_cruise"] = hp_cruise
            pUDDS_cruise["load_factor_cruise"] = load_factors_cruise
            pUDDS_cruise["motor_eff_cruise"] = motor_eff_cruise
            # Final power calculation
            pUDDS_cruise["power"] = (total_power_cruise /
                                     (battery_roundtrip_efficiency * drivetrain_efficiency * motor_eff_cruise)) #Divide total power by battery, drivetrain and motor efficiency
            # Apply regenerative braking
            pUDDS_cruise.loc[pUDDS_cruise["power"] < 0, "power"] *= 0.2
            # Integrate power to find energy (kWh)
            E_forces_cruise = trapz(pUDDS_cruise["power"], pUDDS_cruise["time"]) * 2.778e-7
            E_forces_cruise = E_forces_cruise * hw_dist_cruise / ordist_cruise

            ########
            # **Total energy needed**
            needed_energy_hw = E_forces_ramping + E_forces_cruise + E_gradient

            # Compute required battery weight
            needed_battery_weight_hw = (needed_energy_hw / energy_d) / packing_f

            # battery size buffer (10% power needs to be remaining at the end)
            needed_energy_hw = needed_energy_hw / 0.9

            # Compute percentage difference in battery weight
            dbattery_weight = abs(needed_battery_weight_hw - battery_weight) / needed_battery_weight_hw * 100
            dbattery_weight = round(dbattery_weight, 6)
            #dbattery_weight = abs(battery_weight - needed_battery_weight_hw) < 0.1
            # If battery weight is within 1% tolerance, save results and break loop
            if dbattery_weight < 1:
                row_index = rt_route_results.index[i]
                rt_route_results.at[row_index, "needed_battery_capacity"] = needed_energy_hw
                rt_route_results.at[row_index, "energy"] = needed_energy_hw
                rt_route_results.at[row_index, "hw_miles"] = hw_dist / 1609  # Convert meters to miles
                rt_route_results.at[row_index, "efficiency_Wh_per_mile"] = (needed_energy_hw * 1000) / (hw_dist / 1609)
                rt_route_results.at[row_index, "hp_99_ramping"] = np.percentile(pUDDS_ramping["hp_ramping"],99)
                rt_route_results.at[row_index, "hp_99_cruise"] = np.percentile(pUDDS_cruise["hp_cruise"], 99)
                rt_route_results.at[row_index, "load_factor_ramping"] = np.percentile(pUDDS_ramping["load_factor_ramping"],50)
                rt_route_results.at[row_index, "load_factor_cruise"] = np.percentile(pUDDS_cruise["load_factor_cruise"], 50)
                rt_route_results.at[row_index, "motor_eff_ramping"] = np.percentile(pUDDS_ramping["motor_eff_ramping"],50)
                rt_route_results.at[row_index, "motor_eff_cruise"] = np.percentile(pUDDS_cruise["motor_eff_cruise"], 50)
                print(f"Route {origin} -> {dest}: Exiting after {iteration} iterations.")
                #pUDDS_cruise.to_csv(f"results/pUDDS_cruise_{origin}_{dest}.csv", index=False)
                break
            else:
                battery_weight = needed_battery_weight_hw  # Update battery weight and iterate
        #print("results:", rt_route_results['needed_battery_capacity'])

    return rt_route_results