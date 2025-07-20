import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt

from Drive_profile.Drive_profile import process_drive_cycle
from Filepath.filepath import workspace_folder

os.chdir(workspace_folder)

# Run the processing function
file_path = "heavytruck_cruise_drivecycle.csv"

hw_ramping_up_60, hw_cruise_60, hw_ramping_down_60, hw_ramping_60, ordist_cruise_60, ordist_ramping_60, ordist_ramping_up_60, ordist_ramping_down_60 = process_drive_cycle(file_path, 60)
hw_ramping_up_55, hw_cruise_55, hw_ramping_down_55, hw_ramping_55, ordist_cruise_55, ordist_ramping_55, ordist_ramping_up_55, ordist_ramping_down_55 = process_drive_cycle(file_path, 55)
hw_ramping_up_50, hw_cruise_50, hw_ramping_down_50, hw_ramping_50, ordist_cruise_50, ordist_ramping_50, ordist_ramping_up_50, ordist_ramping_down_50 = process_drive_cycle(file_path, 50)
hw_ramping_up_45, hw_cruise_45, hw_ramping_down_45, hw_ramping_45, ordist_cruise_45, ordist_ramping_45, ordist_ramping_up_45, ordist_ramping_down_45 = process_drive_cycle(file_path, 45)

print(list(hw_ramping_45), ordist_cruise_45, ordist_ramping_45)
################################
# Plot
hw_profile_plot = pd.concat([hw_ramping_up_55, hw_cruise_55, hw_ramping_down_55])
hw_profile_plot["time"] = np.arange(1, len(hw_profile_plot) + 1)
hw_profile_plot_60 = pd.concat([hw_ramping_up_60, hw_cruise_60, hw_ramping_down_60])
hw_profile_plot_60["time"] = np.arange(1, len(hw_profile_plot) + 1)
hw_profile_plot_50 = pd.concat([hw_ramping_up_50, hw_cruise_50, hw_ramping_down_50])
hw_profile_plot_50["time"] = np.arange(1, len(hw_profile_plot) + 1)
hw_profile_plot_45 = pd.concat([hw_ramping_up_45, hw_cruise_45, hw_ramping_down_45])
hw_profile_plot_45["time"] = np.arange(1, len(hw_profile_plot) + 1)

color_map = {0: "#33a02c", 1: "#1f78b4", 2: "#b2df8a"}

plt.figure(figsize=(10, 5))
for flag, color in color_map.items():
    subset = hw_profile_plot[hw_profile_plot["flag"] == flag]
    plt.plot(subset["time"], subset["velocity"], color=color, linewidth=1, label=f"Flag {flag}")

plt.xlabel("Time", fontsize=16, fontweight="bold")
plt.ylabel("Velocity (mph)", fontsize=16, fontweight="bold")
plt.xticks(fontsize=14)
plt.yticks(fontsize=14)
plt.grid(True, linestyle="--", alpha=0.5)
plt.gca().set_facecolor("white")
plt.gca().spines["top"].set_visible(False)
plt.gca().spines["right"].set_visible(False)
plt.legend().set_visible(False)
plt.show()

plt.figure(figsize=(10, 6))
plt.plot(hw_profile_plot_60["time"], hw_profile_plot_60["velocity"], color="#FF1F58", linewidth=1, label="60 mph")
plt.plot(hw_profile_plot["time"], hw_profile_plot["velocity"], color="#FFC61E", linewidth=1, label="55 mph")
plt.plot(hw_profile_plot_50["time"], hw_profile_plot_50["velocity"], color="#009ADE", linewidth=1, label="50 mph")
plt.plot(hw_profile_plot_45["time"], hw_profile_plot_45["velocity"], color="#00CD6C", linewidth=1, label="45 mph")

# Labels and formatting
plt.xlabel("Time (s)", fontsize=18, fontweight="bold")
plt.ylabel("Velocity (mph)", fontsize=18, fontweight="bold")
plt.xticks(fontsize=18)
plt.yticks(fontsize=18)
plt.grid(True, linestyle="--", alpha=0.5)
plt.gca().set_facecolor("white")
plt.gca().spines["top"].set_visible(False)
plt.gca().spines["right"].set_visible(False)

# Remove legend
plt.legend(loc='center left', bbox_to_anchor=(0.8, 0.8), fontsize=18).set_visible(True)
plt.savefig("results/SVG/drive_profile.svg", format='svg', transparent=True)
# Show the plot
plt.show()