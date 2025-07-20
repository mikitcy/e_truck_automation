import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.ticker import PercentFormatter
from Filepath.filepath import workspace_folder

os.chdir(workspace_folder)

rt_all_45 = pd.read_csv('results/rt_all_45_charge_weight.csv')
rt_all_50 = pd.read_csv('results/rt_all_50_charge_weight.csv')
rt_all_55 = pd.read_csv('results/rt_all_55_charge_weight.csv')
rt_all_60 = pd.read_csv('results/rt_all_60_charge_weight.csv')

rt_all_55_500 = rt_all_55
rt_all_55_250 = pd.read_csv('results/rt_all_60_charge_250_weight.csv')
rt_all_55_750 = pd.read_csv('results/rt_all_60_charge_750_weight.csv')
rt_all_55_1000 = pd.read_csv('results/rt_all_60_charge_1000_weight.csv')

custom_palette = {
    "45 mph": "#00CD6C",
    "50 mph": "#009ADE",
    "55 mph": "#FFC61E",
    "60 mph": "#FF1F58"
}
custom_palette_batterysize = {
    "250 kWh": "#00CD6C",
    "500 kWh": "#009ADE",
    "750 kWh": "#FFC61E",
    "1000 kWh": "#FF1F58"
}

# box plot - weight factor
for df_hist, speed in zip([rt_all_45, rt_all_60], ["45 mph", "60 mph"]):
    df_hist["charge_break"] = df_hist["charge_break"].astype(int)
    df_hist["speed"] = speed
combined_df = pd.concat([rt_all_45, rt_all_60])

combined_df['int_weight'] = np.round(combined_df['w_factor']).astype(int)
print(combined_df.columns)

# Repeat df rows to reflect weight factor
def repeat_rows(df, weight_col):
    return df.loc[df.index.repeat(df[weight_col])].reset_index(drop=True)
repeat_df = repeat_rows(combined_df, 'int_weight')

# Box plot
plt.figure(figsize=(12, 8))
sns.boxplot(data=repeat_df, x="charge_break", y="miles", hue="speed", palette=custom_palette, showfliers=False)

plt.xlabel("Number of charge Break (500kWh Battery)", fontsize=18)
plt.ylabel("Route Distance (miles)", fontsize=18)
plt.xticks(fontsize=18)
plt.yticks(fontsize=18)
plt.legend(title="Speed", fontsize=18, title_fontsize=18)
plt.grid(False)
plt.gca().set_facecolor("white")
plt.gca().spines["top"].set_visible(False)
plt.gca().spines["right"].set_visible(False)
plt.savefig("results/SVG/box_mile_charge_speed.svg", format='svg', transparent=True)
plt.show()

##############
# Print numbers
avg_charge_breaks = repeat_df.groupby("speed")["charge_break"].mean().reset_index()
avg_charge_breaks.columns = ["speed", "avg_charge_breaks"]
print(avg_charge_breaks)
charge_break_stats = repeat_df.groupby("speed")["charge_break"].agg(
    median="median",
    q1=lambda x: x.quantile(0.25),
    q3=lambda x: x.quantile(0.75)).reset_index()
print(charge_break_stats)

repeat_df["mile_per_charge"] = repeat_df.apply(
    lambda row: row["miles"] / row["charge_break"] if row["charge_break"] > 0 else None,axis=1)
mile_per_charge_stats = repeat_df.groupby("speed")["mile_per_charge"].agg(
    median="median",
    q1=lambda x: x.quantile(0.25),
    q3=lambda x: x.quantile(0.75)
).reset_index()
print(mile_per_charge_stats)

summary_stats = repeat_df.groupby(['speed', 'charge_break'])['miles'].agg(
    median='median',
    q1=lambda x: x.quantile(0.25),
    q3=lambda x: x.quantile(0.75)).reset_index()
print(summary_stats)

##################
# Create vertically stacked plots (box + histogram)
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6),sharex=True,gridspec_kw={'height_ratios': [3, 1]})

sns.boxplot(data=repeat_df,x="charge_break",y="miles",hue="speed",palette=custom_palette,
            showfliers=False,dodge=True,ax=ax1)

ax1.set_ylabel("Route Distance (miles)", fontsize=18)
ax1.set_xlabel("")
ax1.tick_params(labelsize=18)
#ax1.legend(title="Speed", fontsize=14, title_fontsize=14)
ax1.legend_.remove()
ax1.grid(False)
ax1.set_facecolor("white")
ax1.spines["top"].set_visible(False)
ax1.spines["right"].set_visible(False)

sns.histplot(data=repeat_df,x="charge_break",hue="speed",multiple="dodge",shrink=0.8,element="bars",
             stat="probability",discrete=True,palette=custom_palette,alpha=0.6,ax=ax2)
ax2.yaxis.set_major_formatter(PercentFormatter(xmax=1))

ax2.set_ylabel("Probability", fontsize=18)
ax2.set_xlabel("Number of charge Break (500kWh Battery)", fontsize=18)
ax2.tick_params(labelsize=18)
ax2.grid(False)
ax2.set_facecolor("white")
ax2.spines["top"].set_visible(False)
ax2.spines["right"].set_visible(False)
ax2.legend_.remove()

plt.tight_layout(h_pad=0.5)
plt.savefig("results/SVG/box_mile_charge_speed_with_hist_below.svg", format='svg', transparent=True)
plt.show()

###################
# Battery size
for df_hist in [rt_all_55_250, rt_all_55_500, rt_all_55_750, rt_all_55_1000]:
    df_hist["charge_break"] = df_hist["charge_break"].astype(int)
rt_all_55_250["Battery"] = "250 kWh"
rt_all_55_500["Battery"] = "500 kWh"
rt_all_55_750["Battery"] = "750 kWh"
rt_all_55_1000["Battery"] = "1000 kWh"
combined_df_batterysize = pd.concat([rt_all_55_250, rt_all_55_500, rt_all_55_750, rt_all_55_1000])
combined_df_batterysize['int_weight'] = np.round(combined_df_batterysize['w_factor']).astype(int)
repeat_df_batterysize = repeat_rows(combined_df_batterysize, 'int_weight')

##############
# Print numbers
print("battery size:")
charge_break_stats = repeat_df_batterysize.groupby("Battery")["charge_break"].agg(
    median="median",
    q1=lambda x: x.quantile(0.25),
    q3=lambda x: x.quantile(0.75)).reset_index()
print(charge_break_stats)
median_miles_by_charge = rt_all_55_500.groupby("charge_break")["miles"].median()
print("500:", median_miles_by_charge)
median_miles_by_charge = rt_all_55_1000.groupby("charge_break")["miles"].median()
print("1000:", median_miles_by_charge)
##############

plt.figure(figsize=(12, 8))
sns.boxplot(data=repeat_df_batterysize, x="charge_break", y="miles", hue="Battery", palette=custom_palette_batterysize, showfliers=False)

plt.xlabel("Number of charge Break (55mph speed)", fontsize=18)
plt.ylabel("Route Distance (miles)", fontsize=18)
plt.xticks(fontsize=18)
plt.yticks(fontsize=18)
plt.xlim(0,14)
plt.legend(title="Battery", fontsize=18)
plt.grid(False)
plt.gca().set_facecolor("white")
plt.gca().spines["top"].set_visible(False)
plt.gca().spines["right"].set_visible(False)
plt.savefig("results/SVG/box_mile_charge_kwh.svg", format='svg', transparent=True)
plt.show()

# Create vertically stacked plots (box + histogram)
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6),sharex=True,gridspec_kw={'height_ratios': [3, 1]})

### box plot
df_box = repeat_df_batterysize[repeat_df_batterysize["charge_break"] <= 14].copy()
sns.boxplot(data=df_box,x="charge_break",y="miles",hue="Battery",palette=custom_palette_batterysize,
            showfliers=False,dodge=True,ax=ax1)

ax1.set_ylabel("Route Distance (miles)", fontsize=18)
ax1.set_xlabel("")
ax1.tick_params(labelsize=18)
#ax1.legend(title="Speed", fontsize=14, title_fontsize=14)
ax1.legend_.remove()
ax1.set_xlim(0, 14)
ax1.grid(False)
ax1.set_facecolor("white")
ax1.spines["top"].set_visible(False)
ax1.spines["right"].set_visible(False)

### histogram
# getting probability for x>14
df_hist = repeat_df_batterysize.copy()
df_hist["charge_break_sum_if_+14"] = df_hist["charge_break"].apply(lambda x: 14 if x >= 14 else x)

sns.histplot(data=df_hist, x="charge_break_sum_if_+14", hue="Battery", multiple="dodge", shrink=0.8, element="bars",
             stat="probability", discrete=True, palette=custom_palette_batterysize, alpha=0.6, ax=ax2)
ax2.yaxis.set_major_formatter(PercentFormatter(xmax=1))

ax2.set_ylabel("Probability", fontsize=18)
ax2.set_xlabel("Number of charge Break (55mph speed)", fontsize=18)
ax2.tick_params(labelsize=18)
ax2.grid(False)
ax2.set_xlim(0, 14)
ax2.set_facecolor("white")
ax2.spines["top"].set_visible(False)
ax2.spines["right"].set_visible(False)
ax2.legend_.remove()

xticks = ax2.get_xticks()
xtick_labels = [f"{int(t)}+" if t == 14 else f"{int(t)}" for t in xticks]
ax2.set_xticks(xticks)
ax2.set_xticklabels(xtick_labels)

plt.tight_layout(h_pad=0.5)
plt.savefig("results/SVG/box_mile_charge_batterysize_with_hist_below.svg", format='svg', transparent=True)
plt.show()