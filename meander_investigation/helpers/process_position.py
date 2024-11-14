import pandas as pd
import numpy as np
from icedrift import cleaning
from icedrift import interpolation

def get_frequency(buoy_df, warning=False):
    """Calculates the median frequency and returns as
    an integer number of minutes. Prints warning if the
    maximum and minimum of 7D aggregates is different."""
    t = buoy_df.index.to_series()
    dt = t - t.shift(1)
    f = int(np.round(dt.median().total_seconds()/60, 0))

    # Check if representative of weekly data
    fmax = int(np.round(dt.resample('7D').median().max().total_seconds()/60, 0))
    fmin = int(np.round(dt.resample('7D').median().min().total_seconds()/60, 0))
    
    if (np.abs(f - fmax) > 0) | (np.abs(f - fmin) > 0) and warning:
       print('Warning: buoy has varying frequency. fmin=', fmin, 'fmax=', fmax, 'f=', f)
        
    if f <= 30:
        interp_freq = '30min'
    elif f <= 65: # There's a couple that are at 61, which is certainly an error (either human or computer)
        interp_freq = '60min'
    else:
        interp_freq = str(np.round(f, -1)) + 'min'


    return interp_freq

def clean_location_df(loc_df):
    buoy = loc_df["BuoyID"]

    if len(buoy) == 1:
        return None
    
    # Calculate the frequency
    freq = get_frequency(loc_df)
    freq_hrs = str(int(freq.replace('min','')) * 3) + 'min'

    # The "standard_qc" function can be adjusted if needed
    # It's in the "icedrift.cleaning" module and strings together
    # the QC steps
    
    df_qc = cleaning.standard_qc(loc_df,
                        min_size=100,
                        gap_threshold=freq_hrs,                
                        segment_length=24,
                        lon_range=(-180, 180),
                        lat_range=(50, 90),
                        max_speed=1.5,
                        speed_window='3D',
                        verbose=False)
    
    
    interpolatable = df_qc is not None
    if interpolatable:
        df = df_qc[df_qc["flag"] == False]

        maxgap = 4 * int(freq.replace('min', ''))
        df = interpolation.interpolate_buoy_track(df,
                                                xvar='longitude', yvar='latitude', 
                                                freq=freq, maxgap_minutes=max(maxgap, 120))
        
        return df
    
    return None