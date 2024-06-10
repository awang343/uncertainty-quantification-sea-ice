# Uncertainty Quantification for Sea Ice Motion

## Install
Set up mamba environment using the provided env file
```
mamba create -f env.yml
```

## Data
TBD: Description of the MOSAiC buoy dataset

Surface meteorological data was obtained from the ECMWF ERA5 reanalysis via the Copernicus Climate Data Store (CDS). The script `prepare_era_data.py` uses the `cdsapi` library to download hourly ERA5 data on a 0.25 degree latitude-longitude grid, then uses `xesmf` to regrid the data to a regular 25-km north polar stereographic grid (NSIDC North Polar Stereographic, EPSG code 3413).

TBD: 
