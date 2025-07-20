import pandas as pd
import numpy as np
import os
from datetime import datetime

from Map.Highway_distance import get_charge_distance
from Map.Highway_point_api import get_unique_charge_points_df, get_charge_coordinates, merge_charge_coordinates, get_resume_subset
from Filepath.filepath import workspace_folder

os.chdir(workspace_folder)

rt_leg_charge_45 = pd.read_csv('results/rt_leg_charge_45.csv')
rt_leg_charge_50 = pd.read_csv('results/rt_leg_charge_50.csv')
rt_leg_charge_55 = pd.read_csv('results/rt_leg_charge_55.csv')
rt_leg_charge_60 = pd.read_csv('results/rt_leg_charge_60.csv')

#print(rt_leg_charge_55.dtypes)
print(datetime.now())
rt_leg_charge_60 = get_charge_distance(rt_leg_charge_60)
rt_leg_charge_60.to_csv('results/rt_leg_charge_60_distance.csv', index=False)
rt_leg_charge_45 = get_charge_distance(rt_leg_charge_45)
rt_leg_charge_45.to_csv('results/rt_leg_charge_45_distance.csv', index=False)
rt_leg_charge_55 = get_charge_distance(rt_leg_charge_55)
rt_leg_charge_55.to_csv('results/rt_leg_charge_55_distance.csv', index=False)
rt_leg_charge_50 = get_charge_distance(rt_leg_charge_50)
rt_leg_charge_50.to_csv('results/rt_leg_charge_50_distance.csv', index=False)

# Ensure charge_mile_5 exists in rt_leg_charge_45
if 'charge_mile_5' not in rt_leg_charge_45.columns:
    rt_leg_charge_45['charge_mile_5'] = np.nan
if 'charge_mile_5' not in rt_leg_charge_50.columns:
    rt_leg_charge_50['charge_mile_5'] = np.nan

# merge all speeds dfs to get only unique charge locations
cols_to_keep = ['lat', 'lon', 'lat2', 'lon2','charge_mile_1', 'charge_mile_2', 'charge_mile_3', 'charge_mile_4', 'charge_mile_5']
df_60 = rt_leg_charge_60[cols_to_keep]
df_45 = rt_leg_charge_45[cols_to_keep]
df_50 = rt_leg_charge_50[cols_to_keep]
df_55 = rt_leg_charge_55[cols_to_keep]
rt_leg_charge_combined = pd.concat([df_60, df_55, df_50, df_45], ignore_index=True)

# get unique charge points and get coordinates
print(datetime.now())
unique_charge_points = get_unique_charge_points_df(rt_leg_charge_combined)
unique_charge_points.to_csv('results/unique_charge_points.csv', index=False)
unique_charge_coordinates = get_charge_coordinates(unique_charge_points, 'results/unique_charge_points_coordinates.csv')
print(datetime.now())

# In case interrupted:
#unique_charge_points= pd.read_csv('results/unique_charge_points.csv')
#unique_charge_coordinates = pd.read_csv('results/unique_charge_points_coordinates.csv')
#charge_df_resume = get_resume_subset(unique_charge_points, unique_charge_coordinates)
#charge_df_resume.to_csv("results/unique_charge_points_not_processed.csv", index=False)
#unique_charge_coordinates_resume = get_charge_coordinates(charge_df_resume, output_file="results/unique_charge_points_coordinates_resumed.csv")
#charge_df_full = pd.concat([unique_charge_coordinates, unique_charge_coordinates_resume], ignore_index=True)
#charge_df_full.to_csv("results/unique_charge_points_coordinates_concat.csv", index=False)
#unique_charge_coordinates = charge_df_full

#unique_charge_coordinates = pd.read_csv('results/unique_charge_points_coordinates.csv')
#rt_leg_charge_45 = pd.read_csv('results/rt_leg_charge_45_distance.csv')
#rt_leg_charge_50 = pd.read_csv('results/rt_leg_charge_50_distance.csv')
#rt_leg_charge_55 = pd.read_csv('results/rt_leg_charge_55_distance.csv')
#rt_leg_charge_60 = pd.read_csv('results/rt_leg_charge_60_distance.csv')

# Apply to routes
rt_leg_charge_45 = merge_charge_coordinates(rt_leg_charge_45, unique_charge_coordinates)
rt_leg_charge_45.to_csv('results/rt_leg_charge_45_location.csv', index=False)
rt_leg_charge_50 = merge_charge_coordinates(rt_leg_charge_50, unique_charge_coordinates)
rt_leg_charge_50.to_csv('results/rt_leg_charge_50_location.csv', index=False)
rt_leg_charge_60 = merge_charge_coordinates(rt_leg_charge_60, unique_charge_coordinates)
rt_leg_charge_60.to_csv('results/rt_leg_charge_60_location.csv', index=False)
rt_leg_charge_55 = merge_charge_coordinates(rt_leg_charge_55, unique_charge_coordinates)
rt_leg_charge_55.to_csv('results/rt_leg_charge_55_location.csv', index=False)