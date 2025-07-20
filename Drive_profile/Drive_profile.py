import pandas as pd
import numpy as np
from scipy.integrate import trapz

def split_drive_cycle(df):
    """Split the drive cycle into ramp-up/down and cruising sections."""
    hw_cruise = df.iloc[239:1570].copy()
    hw_ramping = pd.concat([df.iloc[0:238], df.iloc[1571:2083]]).copy()
    hw_ramping_up = pd.concat([df.iloc[0:238]]).copy()
    hw_ramping_down = pd.concat([df.iloc[1571:2083]]).copy()
    return hw_cruise, hw_ramping, hw_ramping_up, hw_ramping_down

def calculate_trapezoidal_distance(df):
    """Calculate the trapezoidal integral of velocity over time."""
    df = df.copy()
    df["time"] = np.arange(1, len(df) + 1)  # Reset time index
    velocity_mps = df["velocity"] / 2.237  # Convert mph to m/s
    return trapz(velocity_mps, df["time"])

def process_drive_cycle(file_path, adjusted_speed):
    """Main function to process and analyze the drive cycle data."""
    hw_profile_adjusted = pd.read_csv(file_path, names=["time", "velocity"])

    # Adjust velocities
    hw_profile_adjusted["velocity"] *= adjusted_speed / 55
    hw_cruise_adjusted, hw_ramping_adjusted, hw_ramping_up_adjusted, hw_ramping_down_adjusted = split_drive_cycle(hw_profile_adjusted)

    # Compute distances for adjusted speed
    ordist_cruise = calculate_trapezoidal_distance(hw_cruise_adjusted)
    ordist_ramping = calculate_trapezoidal_distance(hw_ramping_adjusted)
    ordist_ramping_up = calculate_trapezoidal_distance(hw_ramping_up_adjusted)
    ordist_ramping_down = calculate_trapezoidal_distance(hw_ramping_down_adjusted)

    hw_ramping_up = hw_profile_adjusted.iloc[0:238].copy()
    hw_cruise = hw_profile_adjusted.iloc[239:1570].copy()
    hw_ramping_down = hw_profile_adjusted.iloc[1571:2083].copy()
    hw_ramping = pd.concat([hw_ramping_up, hw_ramping_down], axis=0, ignore_index=True)

    hw_ramping_up["time"] = np.arange(1, len(hw_ramping_up) + 1)
    hw_ramping_down["time"] = np.arange(1, len(hw_ramping_down) + 1)
    hw_ramping["time"] = np.arange(1, len(hw_ramping) + 1)
    hw_cruise["time"] = np.arange(1, len(hw_cruise) + 1)
    hw_ramping["velocity"] = hw_ramping["velocity"].fillna(0)
    hw_cruise["velocity"] = hw_cruise["velocity"].fillna(0)

    hw_ramping_up["flag"] = 0
    hw_cruise["flag"] = 1
    hw_ramping_down["flag"] = 2
    hw_ramping["flag"] = 0

    return hw_ramping_up, hw_cruise, hw_ramping_down, hw_ramping, ordist_cruise, ordist_ramping, ordist_ramping_up, ordist_ramping_down