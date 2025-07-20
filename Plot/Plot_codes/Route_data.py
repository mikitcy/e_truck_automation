import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import gaussian_kde
from Filepath.filepath import workspace_folder

os.chdir(workspace_folder)

df = pd.read_csv("results/rt_all_60_charge_weight.csv")

df = df[['miles', 'w_factor']].dropna()
x = df['miles'].values
w = df['w_factor'].values

# kde
kde = gaussian_kde(x, weights=w)
x_grid = np.linspace(0, x.max(), 1000)
y_kde = kde(x_grid)

# cdf
cdf = np.cumsum(y_kde)
cdf = cdf / cdf[-1]

# plot
fig, ax1 = plt.subplots(figsize=(8, 3))
plt.plot(x_grid, cdf, color='#F28522', linewidth=2)
plt.fill_between(x_grid, cdf, color='#F28522', alpha=0.4)
plt.xlabel('Route distance (miles)', fontsize=18)
plt.ylabel('Cumulative shipped\nweight (%)', fontsize=18)
plt.title('')
plt.xlim(0, 3500)
plt.xticks(fontsize=18)
plt.ylim(0, 1)
plt.yticks(np.linspace(0, 1, 6), fontsize=18)
plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'{y * 100:.0f}'))

# Line for median
quantiles = [0.25, 0.5, 0.75]
colors = ['#F28522', '#F28522', '#F28522']
line_styles = [':', '--', ':']
line_widths = [2, 2, 2]

for q, color, style, lw in zip(quantiles, colors, line_styles, line_widths):
    idx = np.searchsorted(cdf, q)
    q_x = x_grid[idx]
    q_y = cdf[idx]
    plt.plot([q_x, q_x], [0, q_y], linestyle=style, color=color, linewidth=lw)

plt.grid(False)
plt.gca().spines["top"].set_visible(False)
plt.gca().spines["right"].set_visible(False)
plt.tight_layout()
plt.savefig("results/SVG/route_cdf.svg", format='svg', transparent=True)
plt.show()

x_target = 1000
y_at_1000 = np.interp(x_target, x_grid, cdf)
print(f"CDF value at x = {x_target} miles: {y_at_1000:.4f} ({y_at_1000*100:.2f}%)")
x_target = 650
y_at_1000 = np.interp(x_target, x_grid, cdf)
print(f"CDF value at x = {x_target} miles: {y_at_1000:.4f} ({y_at_1000*100:.2f}%)")
x_target = 250
y_at_1000 = np.interp(x_target, x_grid, cdf)
print(f"CDF value at x = {x_target} miles: {y_at_1000:.4f} ({y_at_1000*100:.2f}%)")