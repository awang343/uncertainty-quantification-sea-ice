# Uncertainty Quantification for Sea Ice Motion

## Install
Set up mamba environment using the provided env file
```
mamba create -f env.yml
```

## Data
The buoy dataset used in this project comes from a network of autonomous, ice-tethered buoys deployed during the MOSAiC experiment. The dataset consists of 216 buoys of various types covering the period from 26 September 2019 to 23 May 2021. The lengths of buoy data range from just 4 observations to 52998 observations. The median length is 5698.

The frequencies of the buoys were assigned by taking the median of time differences between observations. If the median was below 30 or in between 30 and 65, 30 min or 60 min were assigned to frequency respectively. Otherwise, the frequency was assigned to the median rounded to the nearest 10 minutes. The following frequencies were observed:

| Buoy Frequency  | # of Buoys |
| ------------- | ------------- |
| 30min  | 79 |
| 60min  | 100 |
| 120min  |  24 |
| 180min  | 7 |
| 240min  | 4 |
| 720min  | 2 |
| Total | 216 |

### Steps taken for QC
Quality control was performed using the functions found in scripts/icedrift/cleaning.py. The cleaning algorithm is as follows:

1. Remove duplicated and fix reversed dates
2. Remove duplicated positions (where both longitude and latitude stayed the same between two observations)
3. Segment the observations into groups that have gaps larger than the threshold. Then, remove segments that are too short.
4. Check for anomalous speeds between consecutive buoy positions

### Steps taken for Interpolation
Interpolation was done to regrid the buoys to the more standard calculated buoy frequencies above.

## Explore Further
Choosing representative buoys - metadata files tell you which sites have multiple. Preference to use the “T” buoys because there’s extra data from those that we’ll need to study ice floe rotation.
Gap filling - try out some things for using nearby buoys. You can test a method by pretending data is missing by masking it, estimating the masked data, and looking at the error. 

Surface meteorological data was obtained from the ECMWF ERA5 reanalysis via the Copernicus Climate Data Store (CDS). The script `prepare_era_data.py` uses the `cdsapi` library to download hourly ERA5 data on a 0.25 degree latitude-longitude grid, then uses `xesmf` to regrid the data to a regular 25-km north polar stereographic grid (NSIDC North Polar Stereographic, EPSG code 3413).

TBD: The regrid step in `prepare_era_data` needs to be adjusted so that a single netCDF file is created rather than a separate file for each month and for each variable.

# Task List
* (Alan) Add description of MOSAiC buoy data and processing routine
* (Alan) Downsample the MOSAiC buoy data to get daily positions for aligning with the SIC data
* (Daniel) Add the NSIDC Sea Ice Concentration to the daily buoy positions (SIC data is only available at daily resolution)
* Download the MASIE 1 km imagery for the periods where the buoys are getting close to ice edge to verify buoy end dates
* Set up script to automatically check whether a buoy was in the 
* Find subset of buoys where compass data is available -- perhaps on Pangaea for the SIMBA buoys?
