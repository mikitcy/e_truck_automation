import pandas as pd
import os
import numpy as np

from Energy_analysis.Weighted_comparison import weighted_columns_comparison
from Filepath.filepath import workspace_folder

os.chdir(workspace_folder)

# weight the datasets
df_weight = pd.read_csv("weight_factor_rev.csv")

df_weight_copy = df_weight.copy()
df_weight_copy['ORIG_CFS_AREA'] = df_weight['DEST_CFS_AREA'].copy()
df_weight_copy['DEST_CFS_AREA'] = df_weight['ORIG_CFS_AREA'].copy()
df_weight = pd.concat([df_weight, df_weight_copy], ignore_index=True)

df_weight['ORIG_CFS_AREA'] = df_weight['ORIG_CFS_AREA'].str.replace(r'^0+(\d+)', r'\1', regex=True)
df_weight['DEST_CFS_AREA'] = df_weight['DEST_CFS_AREA'].str.replace(r'^0+(\d+)', r'\1', regex=True)

# Add weight to df
df_weight = df_weight.rename(columns={'ORIG_CFS_AREA': 'origin_code'})
df_weight = df_weight.rename(columns={'DEST_CFS_AREA': 'destination_code'})

def weighted_mean(x):
    return np.average(x['WGT_FACTOR'], weights=x['SHIPMT_WGHT'])

weight_factor = df_weight.groupby(['origin_code', 'destination_code']).apply(weighted_mean).reset_index(name='w_factor')
weight_factor.to_csv('results/weight_factor_calc.csv')

#########################
# apply weight factor to output files
rt_all_45_charge = pd.read_csv('results/rt_all_45_charge.csv')
rt_all_50_charge = pd.read_csv('results/rt_all_50_charge.csv')
rt_all_55_charge = pd.read_csv('results/rt_all_55_charge.csv')
rt_all_60_charge = pd.read_csv('results/rt_all_60_charge.csv')

rt_all_55_charge = rt_all_55_charge.merge(weight_factor[['origin_code', 'destination_code', 'w_factor']],on=['origin_code', 'destination_code'], how='left')
rt_all_55_charge = rt_all_55_charge.dropna(subset=['w_factor'])
rt_all_55_charge = rt_all_55_charge.reset_index(drop=True)
rt_all_60_charge = rt_all_60_charge.merge(weight_factor[['origin_code', 'destination_code', 'w_factor']],on=['origin_code', 'destination_code'], how='left')
rt_all_60_charge = rt_all_60_charge.dropna(subset=['w_factor'])
rt_all_60_charge = rt_all_60_charge.reset_index(drop=True)
rt_all_50_charge = rt_all_50_charge.merge(weight_factor[['origin_code', 'destination_code', 'w_factor']],on=['origin_code', 'destination_code'], how='left')
rt_all_50_charge = rt_all_50_charge.dropna(subset=['w_factor'])
rt_all_50_charge = rt_all_50_charge.reset_index(drop=True)
rt_all_45_charge = rt_all_45_charge.merge(weight_factor[['origin_code', 'destination_code', 'w_factor']],on=['origin_code', 'destination_code'], how='left')
rt_all_45_charge = rt_all_45_charge.dropna(subset=['w_factor'])
rt_all_45_charge = rt_all_45_charge.reset_index(drop=True)

rt_all_45_charge.to_csv('results/rt_all_45_charge_weight.csv')
rt_all_50_charge.to_csv('results/rt_all_50_charge_weight.csv')
rt_all_55_charge.to_csv('results/rt_all_55_charge_weight.csv')
rt_all_60_charge.to_csv('results/rt_all_60_charge_weight.csv')

# Calculate percent change in needed_energy_kwh
weighted_columns_comparison(
    rt_all_60_charge,
    rt_all_45_charge,
    column="needed_energy_kwh",
    label="60 mph → 45 mph (charge)"
)

#########################
## charge with different battery capacities
rt_all_55_500 = rt_all_55_charge
rt_all_55_250 = pd.read_csv('results/rt_all_55_charge_250.csv')
rt_all_55_750 = pd.read_csv('results/rt_all_55_charge_750.csv')
rt_all_55_1000 = pd.read_csv('results/rt_all_55_charge_1000.csv')

rt_all_55_250 = rt_all_55_250.merge(weight_factor[['origin_code', 'destination_code', 'w_factor']],on=['origin_code', 'destination_code'], how='left')
rt_all_55_250 = rt_all_55_250.dropna(subset=['w_factor'])
rt_all_55_250 = rt_all_55_250.reset_index(drop=True)
rt_all_55_750 = rt_all_55_750.merge(weight_factor[['origin_code', 'destination_code', 'w_factor']],on=['origin_code', 'destination_code'], how='left')
rt_all_55_750 = rt_all_55_750.dropna(subset=['w_factor'])
rt_all_55_750 = rt_all_55_750.reset_index(drop=True)
rt_all_55_1000 = rt_all_55_1000.merge(weight_factor[['origin_code', 'destination_code', 'w_factor']],on=['origin_code', 'destination_code'], how='left')
rt_all_55_1000 = rt_all_55_1000.dropna(subset=['w_factor'])
rt_all_55_1000 = rt_all_55_1000.reset_index(drop=True)

rt_all_55_250.to_csv('results/rt_all_55_charge_250_weight.csv')
rt_all_55_750.to_csv('results/rt_all_55_charge_750_weight.csv')
rt_all_55_1000.to_csv('results/rt_all_55_charge_1000_weight.csv')

weighted_columns_comparison(
    rt_all_55_500,
    rt_all_55_1000,
    column="needed_energy_kwh",
    label="500 kWh → 1000 kWh"
)

#########################
## no charge dfs
rt_all_55 = pd.read_csv('results/rt_all_55.csv')
rt_all_60 = pd.read_csv('results/rt_all_60.csv')
rt_all_50 = pd.read_csv('results/rt_all_50.csv')
rt_all_45 = pd.read_csv('results/rt_all_45.csv')

rt_all_55 = rt_all_55.merge(weight_factor[['origin_code', 'destination_code', 'w_factor']],on=['origin_code', 'destination_code'], how='left')
rt_all_55 = rt_all_55.dropna(subset=['w_factor'])
rt_all_55 = rt_all_55.reset_index(drop=True)
rt_all_60 = rt_all_60.merge(weight_factor[['origin_code', 'destination_code', 'w_factor']],on=['origin_code', 'destination_code'], how='left')
rt_all_60 = rt_all_60.dropna(subset=['w_factor'])
rt_all_60 = rt_all_60.reset_index(drop=True)
rt_all_50 = rt_all_50.merge(weight_factor[['origin_code', 'destination_code', 'w_factor']],on=['origin_code', 'destination_code'], how='left')
rt_all_50 = rt_all_50.dropna(subset=['w_factor'])
rt_all_50 = rt_all_50.reset_index(drop=True)
rt_all_45 = rt_all_45.merge(weight_factor[['origin_code', 'destination_code', 'w_factor']],on=['origin_code', 'destination_code'], how='left')
rt_all_45 = rt_all_45.dropna(subset=['w_factor'])
rt_all_45 = rt_all_45.reset_index(drop=True)

rt_all_45.to_csv('results/rt_all_45_weight.csv')
rt_all_50.to_csv('results/rt_all_50_weight.csv')
rt_all_55.to_csv('results/rt_all_55_weight.csv')
rt_all_60.to_csv('results/rt_all_60_weight.csv')

weighted_columns_comparison(
    rt_all_60,
    rt_all_45,
    column="energy",
    label="60 mph → 45 mph (no charge)"
)
weighted_columns_comparison(
    rt_all_60,
    rt_all_45,
    column="needed_battery_capacity",
    label="60 mph → 45 mph (no charge)"
)

#########################
## no charge time dfs
rt_all_55 = pd.read_csv('results/rt_all_55_time.csv')
rt_all_60 = pd.read_csv('results/rt_all_60_time.csv')
rt_all_50 = pd.read_csv('results/rt_all_50_time.csv')
rt_all_45 = pd.read_csv('results/rt_all_45_time.csv')

rt_all_55 = rt_all_55.merge(weight_factor[['origin_code', 'destination_code', 'w_factor']],on=['origin_code', 'destination_code'], how='left')
rt_all_55 = rt_all_55.dropna(subset=['w_factor'])
rt_all_55 = rt_all_55.reset_index(drop=True)
rt_all_60 = rt_all_60.merge(weight_factor[['origin_code', 'destination_code', 'w_factor']],on=['origin_code', 'destination_code'], how='left')
rt_all_60 = rt_all_60.dropna(subset=['w_factor'])
rt_all_60 = rt_all_60.reset_index(drop=True)
rt_all_50 = rt_all_50.merge(weight_factor[['origin_code', 'destination_code', 'w_factor']],on=['origin_code', 'destination_code'], how='left')
rt_all_50 = rt_all_50.dropna(subset=['w_factor'])
rt_all_50 = rt_all_50.reset_index(drop=True)
rt_all_45 = rt_all_45.merge(weight_factor[['origin_code', 'destination_code', 'w_factor']],on=['origin_code', 'destination_code'], how='left')
rt_all_45 = rt_all_45.dropna(subset=['w_factor'])
rt_all_45 = rt_all_45.reset_index(drop=True)

weighted_columns_comparison(
    rt_all_60,
    rt_all_45,
    column="time_hw",
    label="60 mph → 45 mph (no charge)"
)