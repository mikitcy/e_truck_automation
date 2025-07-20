
def get_vehicle_emissions_diesel(df):
    # input $ per vehicle
    lifetime_vmt = 1000000  # GREET

    diesel_co2_lifecycle = 13235
    diesel_nox_lifecycle = 541
    diesel_pm_lifecycle = 1358
    diesel_so2_lifecycle = 11985

    # Get vehicle cycle emissions
    route_miles = df['km'] * 0.621371

    df['co2_vehicle'] = route_miles / lifetime_vmt * diesel_co2_lifecycle
    df['nox_vehicle'] = route_miles / lifetime_vmt * diesel_nox_lifecycle
    df['pm25_vehicle'] = route_miles / lifetime_vmt * diesel_pm_lifecycle
    df['so2_vehicle'] = route_miles / lifetime_vmt * diesel_so2_lifecycle

    df['co2'] = df['co2_fuel'] + df['co2_vehicle']
    df['nox'] = df['nox_fuel'] + df['nox_vehicle']
    df['pm25'] = df['pm25_fuel'] + df['pm25_vehicle']
    df['so2'] = df['so2_fuel'] + df['so2_vehicle']

    return df

def get_vehicle_emissions_electric(df, battery_kwh):
    # input $ per vehicle
    lifetime_vmt = 1000000  # GREET

    ev_vehicle_co2_lifecycle = 12448
    ev_vehicle_nox_lifecycle = 504
    ev_vehicle_pm_lifecycle = 1273
    ev_vehicle_so2_lifecycle = 10987

    battery_per_kwh_co2_lifecycle = 23.5
    battery_per_kwh_nox_lifecycle = 1.2
    battery_per_kwh_pm_lifecycle = 1.5
    battery_per_kwh_so2_lifecycle = 68.7

    # Get vehicle cycle emissions
    route_miles = df['miles']

    vehicle_cycle_co2 = route_miles / lifetime_vmt * ev_vehicle_co2_lifecycle
    vehicle_cycle_nox = route_miles / lifetime_vmt * ev_vehicle_nox_lifecycle
    vehicle_cycle_pm = route_miles / lifetime_vmt * ev_vehicle_pm_lifecycle
    vehicle_cycle_so2 = route_miles / lifetime_vmt * ev_vehicle_so2_lifecycle

    battery_co2 = battery_per_kwh_co2_lifecycle * battery_kwh * route_miles / lifetime_vmt
    battery_nox = battery_per_kwh_nox_lifecycle * battery_kwh * route_miles / lifetime_vmt
    battery_pm = battery_per_kwh_pm_lifecycle * battery_kwh * route_miles / lifetime_vmt
    battery_so2 = battery_per_kwh_so2_lifecycle * battery_kwh * route_miles / lifetime_vmt

    df['co2_vehicle'] = vehicle_cycle_co2 + battery_co2
    df['nox_vehicle'] = vehicle_cycle_nox + battery_nox
    df['pm25_vehicle'] = vehicle_cycle_pm + battery_pm
    df['so2_vehicle'] = vehicle_cycle_so2 + battery_so2

    df['co2'] = df['co2_power'] + df['co2_vehicle']
    df['nox'] = df['nox_power'] + df['nox_vehicle']
    df['pm25'] = df['pm25_power'] + df['pm25_vehicle']
    df['so2'] = df['so2_power'] + df['so2_vehicle']

    return df

def get_vehicle_emissions_electric_timeline(df, battery_kwh):
    # input $ per vehicle
    lifetime_vmt = 1000000  # GREET
    ev_vehicle_co2_lifecycle = 12448
    battery_per_kwh_co2_lifecycle = 23.5

    # Get vehicle cycle emissions
    route_miles = df['miles']
    vehicle_cycle_co2 = route_miles / lifetime_vmt * ev_vehicle_co2_lifecycle
    battery_co2 = battery_per_kwh_co2_lifecycle * battery_kwh * route_miles / lifetime_vmt

    df['co2_vehicle'] = vehicle_cycle_co2 + battery_co2

    df['co2_2025'] = df['co2_2025'] + df['co2_vehicle']
    df['co2_2030'] = df['co2_2030'] + df['co2_vehicle']
    df['co2_2035'] = df['co2_2035'] + df['co2_vehicle']
    df['co2_2040'] = df['co2_2040'] + df['co2_vehicle']
    df['co2_2045'] = df['co2_2045'] + df['co2_vehicle']
    df['co2_2050'] = df['co2_2050'] + df['co2_vehicle']

    return df
