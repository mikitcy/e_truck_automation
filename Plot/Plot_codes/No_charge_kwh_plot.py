import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
from Filepath.filepath import workspace_folder

os.chdir(workspace_folder)

rt_all_55 = pd.read_csv('results/rt_all_55_weight.csv')
rt_all_60 = pd.read_csv('results/rt_all_60_weight.csv')
rt_all_50 = pd.read_csv('results/rt_all_50_weight.csv')
rt_all_45 = pd.read_csv('results/rt_all_45_weight.csv')

rt_all_60_500d = pd.read_csv('results/rt_all_60_batterydensity500_weight.csv')

# plot for distance vs kwh
plt.figure(figsize=(8, 4))
plt.scatter(rt_all_55["miles"], rt_all_55["needed_battery_capacity"], color="#FFC61E", s=10, label="55 mph")
plt.scatter(rt_all_60["miles"], rt_all_60["needed_battery_capacity"], color="#FF1F58", s=10, label="60 mph")
plt.scatter(rt_all_50["miles"], rt_all_50["needed_battery_capacity"], color="#009ADE", s=10, label="50 mph")
plt.scatter(rt_all_45["miles"], rt_all_45["needed_battery_capacity"], color="#00CD6C", s=10, label="45 mph")
plt.xlabel("Route Distance (mile)", fontsize=18)
plt.ylabel("Needed Battery \nCapacity (kWh)", fontsize=18)
plt.title("", fontsize=18, fontweight="bold")
plt.grid(False)
#plt.legend(title="Speed", fontsize=18, title_fontsize=18)

plt.xticks(fontsize=18)
plt.yticks(fontsize=18)
plt.xlim(0, 3500)
plt.ylim(0, 15000)
for spine in plt.gca().spines.values():
    spine.set_visible(True)
    #spine.set_linewidth(2)
plt.gca().set_facecolor("white")
plt.gca().spines["top"].set_visible(False)
plt.gca().spines["right"].set_visible(False)
plt.tight_layout()
plt.savefig("results/SVG/no_charge_mile_kwh.svg", format='svg', transparent=True)
plt.show()

# only under 500 miles
plt.figure(figsize=(8, 3))
plt.scatter(rt_all_55["miles"], rt_all_55["needed_battery_capacity"], color="#FFC61E", s=10, label="55 mph")
plt.scatter(rt_all_60["miles"], rt_all_60["needed_battery_capacity"], color="#FF1F58", s=10, label="60 mph")
plt.scatter(rt_all_50["miles"], rt_all_50["needed_battery_capacity"], color="#009ADE", s=10, label="50 mph")
plt.scatter(rt_all_45["miles"], rt_all_45["needed_battery_capacity"], color="#00CD6C", s=10, label="45 mph")
plt.xlabel("Route Distance (mile)", fontsize=18)
plt.ylabel("Needed Battery \nCapacity (kWh)", fontsize=18)
plt.title("", fontsize=18)
plt.grid(False)
#plt.legend(title="Speed", fontsize=18, title_fontsize=18)

plt.xticks(fontsize=18)
plt.yticks(fontsize=18)
plt.xlim(100, 600)
plt.ylim(0, 1200)
for spine in plt.gca().spines.values():
    spine.set_visible(True)
    #spine.set_linewidth(2)
plt.gca().set_facecolor("white")
plt.gca().spines["top"].set_visible(False)
plt.gca().spines["right"].set_visible(False)
plt.tight_layout()
plt.savefig("results/SVG/no_charge_mile_kwh_under600.svg", format='svg', transparent=True)
plt.show()

# plot for distance vs kwh - battery density
plt.figure(figsize=(8, 3))
plt.scatter(rt_all_60["miles"], rt_all_60["needed_battery_capacity"], color="#FF1F58", s=10, label="Baseline")
plt.scatter(rt_all_60_500d["miles"], rt_all_60_500d["needed_battery_capacity"], color="#F28522", s=10, label="Double battery density")
plt.xlabel("Route Distance (mile)", fontsize=18)
plt.ylabel("Needed Battery \nCapacity (kWh)", fontsize=18)
plt.title("", fontsize=18)
plt.grid(False)
#plt.legend(title="Speed", fontsize=18, title_fontsize=18)
plt.xticks(fontsize=18)
plt.yticks(fontsize=18)
plt.xlim(0, 3500)
plt.ylim(0, 15000)
for spine in plt.gca().spines.values():
    spine.set_visible(True)
    #spine.set_linewidth(2)
plt.gca().set_facecolor("white")
plt.gca().spines["top"].set_visible(False)
plt.gca().spines["right"].set_visible(False)
plt.tight_layout()
plt.savefig("results/SVG/no_charge_mile_kwh_density.svg", format='svg', transparent=True)
plt.show()

# battery weight
packing_f = 0.48
rt_all_60['ton'] = (rt_all_60["needed_battery_capacity"] / 0.243) / packing_f / 1000
rt_all_60_500d["ton"] = (rt_all_60_500d["needed_battery_capacity"] / 0.5) / packing_f / 1000
plt.figure(figsize=(8, 3))
plt.scatter(rt_all_60["miles"], rt_all_60["ton"], color="#FF1F58", s=10, label="Baseline")
plt.scatter(rt_all_60_500d["miles"], rt_all_60_500d["ton"], color="#F28522", s=10, label="Double battery density")
plt.xlabel("Route Distance (mile)", fontsize=18)
plt.ylabel("Battery weight \n(ton)", fontsize=18)
plt.title("", fontsize=18)
plt.grid(False)
#plt.legend(title="Speed", fontsize=18, title_fontsize=18)
plt.xticks(fontsize=18)
plt.yticks(fontsize=18)
plt.xlim(0, 3500)
plt.ylim(0, 50)
for spine in plt.gca().spines.values():
    spine.set_visible(True)
    #spine.set_linewidth(2)
plt.gca().set_facecolor("white")
plt.gca().spines["top"].set_visible(False)
plt.gca().spines["right"].set_visible(False)
plt.tight_layout()
plt.savefig("results/SVG/no_charge_mile_ton_density.svg", format='svg', transparent=True)
plt.show()

sorted_df = rt_all_60_500d.sort_values("miles")
x_vals = sorted_df["miles"].values
y_vals = sorted_df["ton"].values
f_interp = interp1d(y_vals, x_vals, bounds_error=False)
y_target = 10
x_at_y_10 = f_interp(y_target)
print(f"x value(s) where battery weight is 10 tons: {x_at_y_10}")

########################
### cdf
color_map = {
    "45 mph": "#00CD6C",
    "50 mph": "#009ADE",
    "55 mph": "#FFC61E",
    "60 mph": "#FF1F58"
}

def get_cdf(df, label):
    sorted_df = df.sort_values("needed_battery_capacity").copy()
    sorted_df["cum_weight"] = sorted_df["w_factor"].cumsum()
    sorted_df["cum_weight_norm"] = sorted_df["cum_weight"] / sorted_df["w_factor"].sum()
    return sorted_df["needed_battery_capacity"].values, sorted_df["cum_weight_norm"].values

threshold = 1000
speeds = ["45 mph", "50 mph", "55 mph", "60 mph"]
print(f"Proportion of routes requiring ≤ {threshold} kWh battery:")
for df, label in zip([rt_all_45, rt_all_50, rt_all_55, rt_all_60], speeds):
    y_vals, x_vals = get_cdf(df, label)
    y_vals = np.array(y_vals)
    x_vals = np.array(x_vals)

    # Interpolate to find x (cumulative proportion) where y reaches 1000
    if threshold <= y_vals.max():
        x_at_threshold = np.interp(threshold, y_vals, x_vals)
        print(f"{label}: {x_at_threshold:.4f}")
    else:
        print(f"{label}: Not reached (max: {y_vals.max():.1f})")

# plot cdf
plt.figure(figsize=(8, 5))

for df, label in zip([rt_all_45, rt_all_50, rt_all_55, rt_all_60], ["45 mph", "50 mph", "55 mph", "60 mph"]):
    x, y = get_cdf(df, label)
    plt.plot(y, x, label=label, color=color_map[label])

plt.xlabel("Cumulative shipped weights (%)", fontsize=18)
plt.ylabel("Needed Battery \nCapacity (kWh)", fontsize=18)
plt.title("", fontsize=18, fontweight="bold")
plt.grid(False)
plt.gca().spines["top"].set_visible(False)
plt.gca().spines["right"].set_visible(False)
#plt.legend(title="Speed", fontsize=18, title_fontsize=18)
plt.xticks(np.linspace(0, 1, 11))
plt.gca().xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{x * 100:.0f}')) # Display as 0–100%
plt.xlim(0, 1)
plt.ylim(0, 20000)
plt.xticks(fontsize=18)
plt.yticks(fontsize=18)
plt.tight_layout()
plt.savefig("results/SVG/no_charge_cdp_kwh.svg", format='svg', transparent=True)
plt.show()
