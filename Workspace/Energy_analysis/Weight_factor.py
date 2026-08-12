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

weight_factor = (
    df_weight.assign(w_factor=df_weight["WGT_FACTOR"] * df_weight["SHIPMT_WGHT"] / 2000)
    .groupby(["origin_code", "destination_code"])["w_factor"]
    .sum()
    .reset_index()
)
weight_factor.to_csv('results/weight_factor_calc.csv')

#########################
# apply weight factor to output files
rt_all_45_charge = pd.read_csv('results/rt_all_45_charge.csv')
rt_all_60_charge = pd.read_csv('results/rt_all_60_charge.csv')

rt_all_60_charge = rt_all_60_charge.merge(weight_factor[['origin_code', 'destination_code', 'w_factor']],on=['origin_code', 'destination_code'], how='left')
rt_all_60_charge = rt_all_60_charge.dropna(subset=['w_factor'])
rt_all_60_charge = rt_all_60_charge.reset_index(drop=True)
rt_all_45_charge = rt_all_45_charge.merge(weight_factor[['origin_code', 'destination_code', 'w_factor']],on=['origin_code', 'destination_code'], how='left')
rt_all_45_charge = rt_all_45_charge.dropna(subset=['w_factor'])
rt_all_45_charge = rt_all_45_charge.reset_index(drop=True)

rt_all_45_charge.to_csv('results/rt_all_45_charge_weight.csv')
rt_all_60_charge.to_csv('results/rt_all_60_charge_weight.csv')
