"""Data cleaning for MOSAiC data. 

Modify this script as you see fit!
"""
import pandas as pd
import json
import numpy as np
import os
import sys
from icedrift import cleaning
from icedrift import interpolation
import xarray as xr
import pyproj


def get_frequency(buoy_df):
    """Calculates the median frequency and returns as
    an integer number of minutes. Prints warning if the
    maximum and minimum of 7D aggregates is different."""
    t = buoy_df.index.to_series()
    dt = t - t.shift(1)
    f = int(np.round(dt.median().total_seconds()/60, 0))

    # Check if representative of weekly data
    # fmax = int(np.round(dt.resample('7D').median().max().total_seconds()/60, 0))
    # fmin = int(np.round(dt.resample('7D').median().min().total_seconds()/60, 0))
    
    #if (np.abs(f - fmax) > 0) | (np.abs(f - fmin) > 0):
    #    print('Warning: buoy has varying frequency. fmin=', fmin, 'fmax=', fmax, 'f=', f)
        
    if f <= 30:
        interp_freq = '30min'
    elif f <= 65: # There's a couple that are at 61, which is certainly an error (either human or computer)
        interp_freq = '60min'
    else:
        interp_freq = str(np.round(f, -1)) + 'min'


    return interp_freq

dataloc = '../data/adc_dn_tracks/'

# There were two main deployments, one north of the Laptev Sea,
# and a second summer deployment near the North Pole

files = os.listdir(dataloc)
files = [f for f in files if f[0] not in ['.', 'S', 'D']]
files = [f for f in files if 'summary' not in f]

for dir in ["../data/qc_buoys/mosaic_dn1",
                    "../data/qc_buoys/mosaic_dn1",
                    "../data/interp_buoys/mosaic_dn1",
                    "../data/interp_buoys/mosaic_dn1"]:
            if not os.path.exists(dir):
                os.makedirs(dir)

## List of V buoys with missing (-) in longitudes after crossing meridian
# Thanks Angela for finding these! Should be updated in the ADC drift set v3.
v_fix_list = {'M2_300234067064490_2019V2.csv': '2020-07-26 17:58:08',
              'M3_300234067064370_2019V3.csv': '2020-07-11 23:58:05',
              'M5_300234067066520_2019V4.csv': '2020-07-10 00:58:09'}

metadata = pd.read_csv(f'{dataloc}/DN_buoy_list_v2.csv').set_index("Sensor ID")

freqs = []
interp = []
lengths = []
for progress, file in enumerate(files):
    buoy = file.split('_')[-1].replace('.csv', '')
    df = pd.read_csv(dataloc + file, index_col='datetime', parse_dates=True)

    # Adjust V buoys to UTC from Beijing time
    # This is also an example of user error affecting a small set of buoys.
    # All the other buoys are set to UTC, which is how they should be.
    if 'V' in buoy:
        df.index = df.index - pd.to_timedelta('8h')

    # Apply correction to longitude issue for 3 V buoys
    # This issue appears if the programmer forgets to set the data
    # type to allow an extra character for a minus sign. So when 
    # the data cross the Greenwich meridian, the longitude values 
    # erroneously stayed positive
    if file in v_fix_list:
        time = pd.to_datetime(v_fix_list[file])
        df_subset = df[time:]
        df_subset.loc[:, 'longitude'] = df_subset.loc[:, 'longitude']*-1
        df.update(df_subset)
        if 'M5' in file.split('_'):        
            df_subset = df['2020-07-10 07:58:06':'2020-07-10 09:58:28'].copy()
            df_subset.longitude = df_subset.longitude*-1
            df.update(df_subset)
    
    # Calculate the frequency
    freq = get_frequency(df)
    freqs.append([buoy, freq])

    freq_hrs = str(int(freq.replace('min',''))//60 * 3) + 'h'

    # The "standard_qc" function can be adjusted if needed
    # It's in the "icedrift.cleaning" module and strings together
    # the QC steps
    
    df_qc = cleaning.standard_qc(df,
                        min_size=100,
                        gap_threshold=freq_hrs,                
                        segment_length=24,
                        lon_range=(-180, 180),
                        lat_range=(50, 90),
                        max_speed=1.5,
                        speed_window='3D',
                        verbose=False)
    
    interpolatable = df_qc is not None

    interp.append([buoy, interpolatable])
    if interpolatable:
        df = df_qc.loc[~df_qc.flag, ['latitude', 'longitude']]
        
        dn = 2 if metadata.loc[buoy, 'Deployment Leg'] == 5 else 1
        df.to_csv(f"../data/qc_buoys/mosaic_dn{dn}/{buoy}.csv")

        
        
        maxgap = 4 * int(freq.replace('min', ''))
        df = interpolation.interpolate_buoy_track(df,
                                                xvar='longitude', yvar='latitude', 
                                                freq=freq, maxgap_minutes=max(maxgap, 120))
        
        df.to_csv(f"../data/interp_buoys/mosaic_dn{dn}/{buoy}.csv")
    

    sys.stdout.write('\r')
    # the exact output you're looking for:
    count = (progress + 1) / len(files)
    sys.stdout.write("[%-20s] %d%%" % ('='*int(20*count), int(100/len(files)*progress + 1)))
    sys.stdout.flush()

freq_lookup = pd.DataFrame(freqs, columns=['Sensor ID', 'Calculated Frequency'])
interp_lookup = pd.DataFrame(interp, columns=['Sensor ID', 'Interp'])

metadata = metadata.reset_index()
metadata = pd.merge(metadata, freq_lookup, on="Sensor ID", how="outer")
metadata = pd.merge(metadata, interp_lookup, on='Sensor ID', how="outer")

metadata = metadata.set_index("Sensor ID")

metadata.to_csv("../data/metadata/buoy_metadata.csv")