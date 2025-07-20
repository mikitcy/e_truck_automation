import pandas as pd
import numpy as np

def emissions_weight(df, df_weight):
    # Add opposite OD combination to df_weight and clean ID format
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

    df = df.merge(weight_factor[['origin_code', 'destination_code', 'w_factor']],
                                        on=['origin_code', 'destination_code'], how='left')
    df = df.dropna(subset=['w_factor'])
    df = df.reset_index(drop=True)

    return df
