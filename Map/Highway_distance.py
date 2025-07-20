import osmnx as ox
import networkx as nx
from geopy.distance import geodesic
import numpy as np

def get_charge_distance(df):
    for index, row in df.iterrows():
        charge_break = int(row['charge_break'])
        remain_kwh = row['remain_kwh']
        needed_energy = row['needed_energy_kwh'] if row['needed_energy_kwh'] > 0 else 1
        miles = row['miles']
        remain_kwh_prev = df.loc[index - 1, 'remain_kwh'] if index > 0 else 0

        if charge_break == 0:
            continue

        charge_points = []

        # First charge points
        first_charger = (remain_kwh_prev/needed_energy) * miles
        charge_points.append(first_charger)

        if charge_break >= 2:
            portion = (needed_energy - remain_kwh - remain_kwh_prev) / (charge_break - 1)
            additional_mile = portion / needed_energy * miles

            for i in range(1, charge_break):
                charge_points.append(charge_points[-1] + additional_mile)

        for j, charge_point in enumerate(charge_points):
            df.at[index, f'charge_mile_{j + 1}'] = charge_point

    return df