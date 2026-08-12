import runpy
import os
from datetime import datetime

run_folder = "this_pyfile_path/Workspace"

###################
### Base case (500kWh battery size, 243Wh/kg density, 45-60mph)
# Run electric scenario with charging on the way - 500kWh battery
os.chdir(run_folder)
runpy.run_path("Energy_analysis/Electric_charge_break.py")
os.chdir(run_folder)
runpy.run_path("Energy_analysis/Charge_location.py")
os.chdir(run_folder)
runpy.run_path("Energy_analysis/Weight_factor.py")

###################
# Run for externality
os.chdir(run_folder)
runpy.run_path("Externalities/Power_emission_calc.py")
os.chdir(run_folder)
runpy.run_path("Externalities/Diesel_damage_factor.py")
os.chdir(run_folder)
runpy.run_path("Externalities/Diesel_emission_calc.py")
os.chdir(run_folder)
