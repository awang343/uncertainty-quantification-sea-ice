# Uncertainty Quantification for Sea Ice Motion

## Install
Set up mamba environment using the provided env file
```
mamba create -f env.yml
```

## Data
TBD: Description of the MOSAiC buoy dataset

Surface meteorological data was obtained from the ECMWF ERA5 reanalysis via the Copernicus Climate Data Store (CDS). The script `prepare_era_data.py` uses the `cdsapi` library to download hourly ERA5 data on a 0.25 degree latitude-longitude grid, then uses `xesmf` to regrid the data to a regular 25-km north polar stereographic grid (NSIDC North Polar Stereographic, EPSG code 3413).

TBD: The regrid step in `prepare_era_data` needs to be adjusted so that a single netCDF file is created rather than a separate file for each month and for each variable.


# Task List
* (Alan) Add description of MOSAiC buoy data and processing routine
* (Alan) Downsample the MOSAiC buoy data to get daily positions for aligning with the SIC data
* (Daniel) Add the NSIDC Sea Ice Concentration to the daily buoy positions (SIC data is only available at daily resolution)
* Download the MASIE 1 km imagery for the periods where the buoys are getting close to ice edge to verify buoy end dates
* Set up script to automatically check whether a buoy was in the 
* Find subset of buoys where compass data is available -- perhaps on Pangaea for the SIMBA buoys?