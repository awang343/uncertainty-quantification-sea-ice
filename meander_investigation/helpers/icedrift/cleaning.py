"""Utility functions for flagging nonphysical behavior in drift tracks.

Functions starting with "check" return a boolean Series with True where the 
data is likely bad.



TBD: Currently, columns are added. This should be optional.
"""

import pandas as pd
import numpy as np
import pyproj
from .analysis import compute_velocity

def check_positions(data, pairs_only=False,
                   latname='latitude', lonname='longitude'):
    """Looks for duplicated or nonphysical position data. Defaults to masking any 
    data with exact matches in latitude or longitude. Setting pairs_only to false 
    restricts the check to only flag where both longitude and latitude are repeated
    as a pair.
    """

    lats = data[latname].round(10)
    lons = data[lonname].round(10)
    
    invalid_lats = np.abs(lats) > 90
    if np.any(lons < 0):
        invalid_lons = np.abs(lons) > 180
    else:
        invalid_lons = lons > 360
        
    invalid = invalid_lats | invalid_lons
    
    repeated = lats.duplicated(keep='first') | lons.duplicated(keep='first')
    
    duplicated = pd.Series([(x, y) for x, y in zip(lons, lats)],
                                  index=data.index).duplicated(keep='first')
    
    if pairs_only:
        return data.loc[~(duplicated | invalid)]
    
    else:
        return data.loc[~(repeated | duplicated | invalid)]


def check_dates(data, precision='1min', date_col=None):
    """Check if there are reversals in the time or duplicated dates. Optional: check
    whether data are isolated in time based on specified search windows and the threshold
    for the number of buoys within the search windows. Dates are rounded to <precision>,
    so in some cases separate readings that are very close in time will be flagged
    as duplicates. Assumes date_col is in a format readable by pandas to_datetime.
    """

    if date_col is None:
        date_values = data.index.values
        date = pd.Series(pd.to_datetime(date_values).round(precision),
                     index=data.index)
    else:
        date = pd.to_datetime(data[date_col]).round(precision)
    duplicated_times = date.duplicated(keep='first')
    
    time_since_last = date - date.shift(1)

    negative_timestep = time_since_last.dt.total_seconds() < 0

    return data.loc[~(negative_timestep | duplicated_times)]
    

def check_gaps(data, threshold_gap='4h', threshold_segment=12, date_col=None):
    """Segments the data based on a threshold of <threshold_gap>. Segments shorter
    than <threshold_segment> are flagged. If <date_col> not specified, then assumes
    that the data has a time index."""
    
    if date_col is None:
        date_values = data.index.values
        date = pd.Series(pd.to_datetime(date_values),
                     index=data.index)
    else:
        date = pd.to_datetime(data[date_col])
    
    time_till_next = date.shift(-1) - date
    
    segment = pd.Series(0, index=data.index)
    counter = 0
    tg = pd.to_timedelta(threshold_gap)
    
    for t in segment.index:
        segment.loc[t] = counter
        if time_till_next[t] > tg:
            counter += 1
    
    # apply_filter
    new = data.groupby(segment).filter(lambda x: len(x) > threshold_segment).index
    
    flag = pd.Series(True, index=data.index)
    flag.loc[new] = False
    return data[~flag]


def check_speed(buoy_df, date_index=True, window='3day', sigma=5, max_speed=1.5):
    """If the position of a point is randomly offset from the path, there will
    be a signature in the velocity. The size of the anomaly will differ depending
    on the time resolution. 
    
    Update to check sequentially, or to update if something is masked.
    
    window can be either time or integer, it is passed to the pandas rolling
    method for calculating anomalies. Default is to use 24 observations for the calculations.
    Data near endpoints are compared to 
    
    method will have more options eventually, for now just z score.
    
    In this method, I first calculate a Z-score for the u and v velocity components, using the 
    forward-backward difference method. This method calculates velocity with forward differences and
    with backward differences, and returns the value with the smallest magnitude. It is therefore
    designed to catch when there is a single out-of-place point. Z-scores are calcuted by first 
    removing the mean over a centered period with the given window size (default 3 days), then
    dividing by the standard deviation over the same period. The Z-scores are then detrended by
    subtracting the median over the same window. When a data point has a Z-score larger than 3, the 
    nearby Z-scores are recalculated with that value masked. Finally, Z-scores larger than 6 are masked.
    """

    if date_index:
        date = pd.Series(pd.to_datetime(buoy_df.index.values).round('1min'),
                         index=pd.to_datetime(buoy_df.index))
    else:
        date = pd.to_datetime(buoy_df.date).round('1min')

    window = pd.to_timedelta(window)
    
    n_min = 0.4*buoy_df.rolling(window, center=True).count()['latitude'].median()

    if n_min > 0:
        n_min = int(n_min)
    else:
        # print('n_min is', n_min, ', setting it to 10.')
        n_min = 10
        
    def zscore(df, window, n_min):
        uscore = (df['u'] - df['u'].rolling(
                    window, center=True, min_periods=n_min).mean()) / \
                 df['u'].rolling(window, center=True, min_periods=n_min).std()
        vscore = (df['v'] - df['v'].rolling(
                    window, center=True, min_periods=n_min).mean()) / \
                 df['v'].rolling(window, center=True, min_periods=n_min).std()

        zu_anom = uscore - uscore.rolling(window, center=True, min_periods=n_min).median()
        zv_anom = vscore - vscore.rolling(window, center=True, min_periods=n_min).median()
        
        return zu_anom, zv_anom

    # First calculate speed using backward difference and get Z-score
    df = compute_velocity(buoy_df, date_index=True, method='fb')

    zu_init, zv_init = zscore(df, window, n_min)
    zu, zv = zscore(df, window, n_min)

    # Anytime the Z score for U or V velocity is larger than 3, re-calculate Z
    # scores leaving that value out.
    # Probably should replace with a while loop so that it can iterate a few times
    for date in df.index:
        if (np.abs(zu[date]) > 3) | (np.abs(zv[date]) > 3):
            # Select part of the data frame that is 2*n_min larger than the window
            idx = df.index[np.abs(df.index - date) < (1.5*window)].drop(date)
            df_new = compute_velocity(df.drop(date).loc[idx,:], method='fb')
            zu_idx, zv_idx = zscore(df_new, window, n_min)

            idx = zu_idx.index[np.abs(zu_idx.index - date) < (0.5*window)]
            zu.loc[idx] = zu_idx.loc[idx]
            zv.loc[idx] = zv_idx.loc[idx]

    flag = df.u.notnull() & ((np.abs(zu) > sigma) | (np.abs(zv) > sigma))
    df = compute_velocity(buoy_df.loc[~flag], method='fb')
    if np.any(df.speed > max_speed):
        flag = flag | (df.speed > max_speed)

    return buoy_df[~flag]

#### Define QC algorithm ####
def standard_qc(buoy_df,
                min_size=100,
                gap_threshold='6H',                
                segment_length=24,
                lon_range=(-180, 180),
                lat_range=(65, 90),
                max_speed=1.5,
                speed_window='3D',
                speed_sigma=4,
                verbose=False):
    """QC steps applied to all buoy data. Wrapper for functions in drifter.clean package.
    min_size = minimum number of observations
    gap_threshold = size of gap between observations that triggers segment length check
    segment_length = minimum size of segment to include
    lon_range = tuple with (min, max) longitudes
    lat_range = tuple with (min, max) latitudes
    verbose = if True, print messages to see where data size is reduced
    
    Algorithm
    1. Check for duplicated and reversed dates with check_dates()
    2. Check for duplicated positions with check_positions() with pairs_only set to True.
    3. Check for gaps and too-short segments using check_gaps()
    4. Check for anomalous speeds using check_speed()
    """
    buoy_df_init = buoy_df.copy()
    n = len(buoy_df)
    buoy_df_init = check_dates(buoy_df_init)
    buoy_df_init = check_positions(buoy_df_init, pairs_only=True)
    
    if len(buoy_df_init) < min_size:
        if verbose:
            print('Observations in bounding box', n, 'less than min size', min_size)
        return None

    def bbox_select(df):
        """Restricts the dataframe to data within
        the specified lat/lon ranges. Selects data from the earliest
        day that the data is in the range to the last day the data
        is in the range. In between, the buoy is allowed to leave
        the bounding box."""
        lon = df.longitude
        lat = df.latitude
        lon_idx = (lon > lon_range[0]) & (lon < lon_range[1])
        lat_idx = (lat > lat_range[0]) & (lat < lat_range[1])
        idx = df.loc[lon_idx & lat_idx].index
        if len(idx) > 0:
            return df.loc[(df.index >= idx[0]) & (df.index <= idx[-1])].copy()
    
    buoy_df_init = bbox_select(buoy_df_init)
    
    # Return None if there's insufficient data
    if buoy_df_init is None or len(buoy_df_init) < min_size:
        if verbose:
            print('Observations in bounding box', n, 'less than min size', min_size)
        return None
    
    buoy_df_init = check_gaps(buoy_df_init,
                           threshold_gap=gap_threshold,
                           threshold_segment=segment_length)
    
    # Check speed
    buoy_df_init = check_speed(buoy_df_init, window=speed_window, max_speed=max_speed, sigma=speed_sigma)

    
    if len(buoy_df_init) < min_size:
        return None
    else:
        return buoy_df_init