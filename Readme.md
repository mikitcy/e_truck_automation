**Model instructions**
-
This project consists of the following contents. 

**1. Filepath setting**
- Set filepath for the project input/output folder.

**2. Workspace codes**
- Run for all following codes in the order:
  - Energy analysis: Estimate electric truck's energy use, required charge breaks (# of breaks and location coordinates), and travel duration. 
  - Externalities: Calculate externalities per route (GHG and air pollution) for both electric and diesel vehicles
 
**3. Plot codes**
- Run to generate plots used in the manuscript.

**4. Functions folders (These python files are not for run)**
- Drive_profile: Functions to read drive velocity profile and extract parameters needed for the further analyses 
- Energy_analysis: Functions to calculate energy usage, number of required charge stops, and travel distance.
- Externality: Functions to calculate externalities (GHG and air pollution) generated for each route 
- Map: Functions to get location of charge points and to plot map for the locations

**Raw Data**
- 
The following data is downloaded from external data portal and used in this model as csv files.
- Commodity Flow Survey
  - 2017 Commodity Flow Survey Datasets; Public Use File (PUF)
    https://www.census.gov/data/datasets/2017/econ/cfs/historical-datasets.html
  - The 2022 Commodity Flow Survey Public Use File (PUF) is scheduled to be released in August 2025.
    https://www.census.gov/data/datasets/2022/econ/cfs/historical-datasets.html

*** Google Direction API (currently only in R code); "rt_final.csv" was created through the R code. 
*** For a sample input dataset, see the "rt_final_sample.csv"