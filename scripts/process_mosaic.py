"""Data cleaning for MOSAiC data. 

Modify this script as you see fit!
"""
import pandas as pd
import json
import numpy as np
import os
import sys
# sys.path.append('../../') # path to drifter package
from icedrift import cleaning
from icedrift import interpolation
import xarray as xr
import pyproj

dataloc = '../data/adc_dn_tracks/'

# There were two main deployments, one north of the Laptev Sea,
# and a second summer deployment near the North Pole
saveloc_dn1 = '../data/qc_buoys/mosaic_dn1/'
saveloc_dn2 = '../data/qc_buoys/mosaic_dn2/'

interploc_dn1 = '../data/interp_buoys/mosaic_dn1/'
interploc_dn2 = '../data/interp_buoys/mosaic_dn2/'

for dir in [saveloc_dn1, saveloc_dn2, interploc_dn1, interploc_dn2]:
    if not os.path.exists(dir):
        os.makedirs(dir)

files = os.listdir(dataloc)
files = [f for f in files if f[0] not in ['.', 'S', 'D']]
files = [f for f in files if 'summary' not in f]

metadata = pd.read_csv('../data/adc_dn_tracks/DN_buoy_list_v2.csv').set_index('Sensor ID')

## List of V buoys with missing (-) in longitudes after crossing meridian
# Thanks Angela for finding these! Should be updated in the ADC drift set v3.
v_fix_list = {'M2_300234067064490_2019V2.csv': '2020-07-26 17:58:08',
              'M3_300234067064370_2019V3.csv': '2020-07-11 23:58:05',
              'M5_300234067066520_2019V4.csv': '2020-07-10 00:58:09'}

def get_frequency(buoy_df):
    """Calculates the median frequency and returns as
    an integer number of minutes. Prints warning if the
    maximum and minimum of 7D aggregates is different."""
    t = buoy_df.index.to_series()
    dt = t - t.shift(1)
    f = int(np.round(dt.median().total_seconds()/60, 0))
    # Check if representative of weekly data
    fmax = int(np.round(dt.resample('7D').median().max().total_seconds()/60, 0))
    fmin = int(np.round(dt.resample('7D').median().min().total_seconds()/60, 0))
    if (np.abs(f - fmax) > 0) | (np.abs(f - fmin) > 0):
        print('Warning: buoy has varying frequency. fmin=', fmin, 'fmax=', fmax, 'f=', f)
        
    if f <= 30:
        interp_freq = '30min'
    elif f <= 65: # There's a couple that are at 61, which is certainly an error (either human or computer)
        interp_freq = '60min'
    else:
        interp_freq = str(np.round(f, -1)) + 'min'


    return interp_freq

for file in files:
    buoy = file.split('_')[-1].replace('.csv', '')
    df = pd.read_csv(dataloc + file, index_col='datetime', parse_dates=True)

    # Adjust V buoys to UTC from Beijing time
    # This is also an example of user error affecting a small set of buoys.
    # All the other buoys are set to UTC, which is how they should be.
    if 'V' in buoy:
        df.index = df.index - pd.to_timedelta('8H')

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

    # The "standard_qc" function can be adjusted if needed
    # It's in the "icedrift.cleaning" module and strings together
    # the QC steps
    df_qc = cleaning.standard_qc(df,
                        min_size=100,
                        gap_threshold='6H',                
                        segment_length=24,
                        lon_range=(-180, 180),
                        lat_range=(50, 90),
                        max_speed=1.5,
                        speed_window='3D',
                        verbose=False)

    if df_qc is not None:
        df = df_qc.loc[~df_qc.flag, ['latitude', 'longitude']]
        
        if metadata.loc[buoy, 'Deployment Leg'] == 5:
            df.to_csv(saveloc_dn2 + buoy + '.csv')
        else:
            df.to_csv(saveloc_dn1 + buoy + '.csv')
            
        freq = get_frequency(df)
        print(buoy, freq)
        maxgap = 4 * int(freq.replace('min', ''))
        df = interpolation.interpolate_buoy_track(df,
                                                  xvar='longitude', yvar='latitude', 
                                                  freq=freq, maxgap_minutes=max(maxgap, 120))
                
        if metadata.loc[buoy, 'Deployment Leg'] == 5:
            df.to_csv(interploc_dn2 + buoy + '.csv')
        else:
            df.to_csv(interploc_dn1 + buoy + '.csv')
          