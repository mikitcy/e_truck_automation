import pandas as pd
import os
import matplotlib.pyplot as plt
from Filepath.filepath import workspace_folder

os.chdir(workspace_folder)

rt_all_time_nocharge = pd.read_csv('results/rt_all_60_time_with_break_urban.csv')
rt_all_45_time = pd.read_csv('results/rt_all_45_time_charge_withurban.csv')
rt_all_60_time = pd.read_csv('results/rt_all_60_time_charge_withurban.csv')

# Plot
plt.figure(figsize=(7, 7))
plt.scatter(rt_all_time_nocharge["miles"], rt_all_time_nocharge["time_total"], color="#F28522", s=10,
            label="60 mph - human drive", zorder=1)
plt.scatter(rt_all_60_time["miles"], rt_all_60_time["time_total"], color="#FF1F58", s=10, label="60 mph", zorder=1)
plt.scatter(rt_all_45_time["miles"], rt_all_45_time["time_total"], color="#00CD6C", s=10, label="45 mph", zorder=1)
plt.xlabel("Route distance (mile)", fontsize=18)
plt.ylabel("Travel duration (hours)", fontsize=18)
plt.xlim(0, 3500)
plt.xticks(fontsize=18)
plt.yticks(fontsize=18)
plt.grid(False)
#plt.legend(title="Speed", fontsize=18, title_fontsize=18)
for spine in plt.gca().spines.values():
    spine.set_visible(True)

plt.gca().set_facecolor("white")
plt.gca().spines["top"].set_visible(False)
plt.gca().spines["right"].set_visible(False)
plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'{y / 60:.0f}'))

# Add shades
plt.axvspan(650, plt.xlim()[1], color='#CDE5D2', alpha=0.3, zorder=0)
plt.axvspan(250, 650, color='#FFF3B2', alpha=0.3, zorder=0)
plt.axvspan(0, 250, color='#F0F0F0', alpha=0.3, zorder=0)

plt.tight_layout()
plt.show()


# Plot - less than 600 miles
plt.figure(figsize=(7, 7))
plt.scatter(rt_all_time_nocharge["miles"], rt_all_time_nocharge["time_total"], color="#F28522", s=10,
            label="60 mph - human drive", zorder=1)
plt.scatter(rt_all_60_time["miles"], rt_all_60_time["time_total"], color="#FF1F58", s=10, label="60 mph", zorder=1)
plt.scatter(rt_all_45_time["miles"], rt_all_45_time["time_total"], color="#00CD6C", s=10, label="45 mph", zorder=1)
plt.xlabel("Route distance (mile)", fontsize=18)
plt.ylabel("Travel duration (hours)", fontsize=18)
plt.xlim(100, 800)
plt.ylim(0, 2000) #in minutes internally
plt.xticks(fontsize=18)
plt.yticks(fontsize=18)

plt.grid(False)
#plt.legend(title="Speed", fontsize=18, title_fontsize=18)
for spine in plt.gca().spines.values():
    spine.set_visible(True)

plt.gca().set_facecolor("white")
plt.gca().spines["top"].set_visible(False)
plt.gca().spines["right"].set_visible(False)
plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'{y / 60:.0f}'))

# Add shades
plt.axvspan(650, plt.xlim()[1], color='#CDE5D2', alpha=0.3, zorder=0)
plt.axvspan(250, 650, color='#FFF3B2', alpha=0.3, zorder=0)
plt.axvspan(0, 250, color='#F0F0F0', alpha=0.3, zorder=0)

plt.tight_layout()
plt.show()
