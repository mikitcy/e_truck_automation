import runpy
import os

run_folder = "this_pyfile_path/Plot"
os.chdir(run_folder)

# Generate plots for route characteristics / drive profiles
runpy.run_path("Plot_codes/Route_data.py")
os.chdir(run_folder)
runpy.run_path("Plot_codes/Drive_profile_setup.py")
os.chdir(run_folder)

# Generate plots for with-charge scenarios
runpy.run_path("Plot_codes/Charge_mile_plot.py")
os.chdir(run_folder)
runpy.run_path("Plot_codes/Charge_time_plot.py")
os.chdir(run_folder)

# Generate plots for externalities
runpy.run_path("Plot_codes/Emission_damage_plot.py")
os.chdir(run_folder)
runpy.run_path("Plot_codes/Emission_damage_grid_timeline_plot.py")
os.chdir(run_folder)

# Generate map images
runpy.run_path("Plot_codes/Route_sample_map.py")
os.chdir(run_folder)
runpy.run_path("Plot_codes/H3_map_plot.py")
os.chdir(run_folder)