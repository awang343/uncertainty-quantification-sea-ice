# Uncertainty Quantification for Sea Ice Motion

## Install
Set up mamba environment using the provided env file
```
mamba create -f env.yml
```

## Data
The buoy dataset used in this project comes from a network of autonomous, ice-tethered buoys deployed starting from 2003. The data is the Level 1 data found at the bottom of this [IABP webpage](https://iabp.apl.uw.edu/data.html).

The frequencies of the buoys were assigned by taking the median of time differences between observations. If the median was below 30 or in between 30 and 65, 30 min or 60 min were assigned to frequency respectively. Otherwise, the frequency was assigned to the median rounded to the nearest 10 minutes.

### Steps taken for QC
Quality control was performed using the functions found in scripts/icedrift/cleaning.py. The cleaning algorithm is as follows:

1. Remove duplicated and fix reversed dates
2. Remove duplicated positions (where both longitude and latitude stayed the same between two observations)
3. Segment the observations into groups that have gaps larger than the threshold. Then, remove segments that are too short.
4. Check for anomalous speeds between consecutive buoy positions

### Steps taken for Interpolation
Interpolation was done to regrid the buoys to the more standard calculated buoy frequencies above. This was done separately on each segment identified previously. The algorithm used for interpolation is interp1d with cubic splines from the scipy package.

### Calculating the meander coefficient

# Task List





