import runpy
import os
from datetime import datetime

run_folder = "this_pyfile_path/Workspace"
os.chdir(run_folder)

###################
### Base case (500kWh battery size, 243Wh/kg density, 45-60mph)
# Run electric scenario without charging on the way (no fixed battery size)
runpy.run_path("Energy_analysis/Electric_nocharge.py")
os.chdir(run_folder)

# Run electric scenario with charging on the way - 500kWh battery
runpy.run_path("Energy_analysis/Electric_charge_break.py")
os.chdir(run_folder)
runpy.run_path("Energy_analysis/Charge_location.py")
os.chdir(run_folder)
runpy.run_path("Externalities/Power_emission_calc.py")
os.chdir(run_folder)
runpy.run_path("Externalities/Power_emission_calc_timeline.py")
os.chdir(run_folder)

# Apply weight factor to the output csv (prep for plotting)
runpy.run_path("Energy_analysis/Weight_factor.py")
os.chdir(run_folder)

###################
# Run for diesel externality
runpy.run_path("Externalities/Diesel_damage_factor.py")
os.chdir(run_folder)
runpy.run_path("Externalities/Diesel_emission_calc.py")
os.chdir(run_folder)
