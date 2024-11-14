import pandas as pd
import proplot as pplt
import numpy as np
import os
from scipy.interpolate import interp1d
from helpers import *

dataloc = '../data/simba_data/raw/'
saveloc = '../data/simba_data/clean/'
os.makedirs(saveloc, exist_ok=True)

def readTab(filepath):
    with open(filepath) as f:
        lines = f.readlines()

        idx = 0
        # Figure out where the comment ends, marked by idx
        for l in lines:
            if '*/' in l:
                break
            else:
                idx += 1
        
        return pd.read_table(filepath, skiprows=idx + 1, parse_dates=True)

metadata = readTab("../data/simba_data/overview.tab").set_index("ID (Meereisportal name)")
metadata["hasCompass"] = False


aux_data = {}

for file in os.listdir(dataloc):
    data = readTab(dataloc+file)
    if 'Compass bearing [deg]' in data.columns:
        aux_data[file.split('_')[0]] = data

    metadata.loc[file.split('_')[0], "hasCompass"] = 'Compass bearing [deg]' in data.columns

metadata.to_csv("../data/metadata/simba_metadata.csv")

aux_data = {buoy: aux_data[buoy] for buoy in aux_data if 'Compass bearing [deg]' in aux_data[buoy].columns}

####
# can add some steps here for cleaning 
# in particular, I think some buoys have reversals in the time series
####

def interpolate_rotation(buoy_df, cpvar='Compass bearing [deg]', 
                           freq='1H', maxgap_minutes=120):
    """Applies interp1d with cubic splines to the rotation specified by cpvar. 
    Assumes that the dataframe buoy_df has a datetime index. Frequency should 
    be in a form understandable to pandas date_range, e.g. '1H' for hourly.
    """

    buoy_df = buoy_df.dropna(subset=[cpvar]).copy()

    # Force the time to start at 0 minutes after the hour
    t = pd.Series(buoy_df.index)
    dt = pd.to_timedelta(t - t.min()).dt.total_seconds()
    tnew = pd.date_range(start=t.min().round(freq), end=t.max().round(freq), freq=freq).round(freq)
    dtnew = pd.to_timedelta(tnew - t.min()).total_seconds()
    
    X = buoy_df[[cpvar]].T
    time_till_next = t.shift(-1) - t
    time_since_last = t - t.shift(1)

    time_till_next = time_till_next.dt.total_seconds()
    time_since_last = time_since_last.dt.total_seconds()

    Xnew = interp1d(dt, X.values, bounds_error=False, kind='cubic')(dtnew).T

    # add information on initial time resolution 
    data_gap = interp1d(dt, np.sum(np.array([time_till_next.fillna(0),
                                             time_since_last.fillna(0)]), axis=0),
                  kind='previous', bounds_error=False)(dtnew)

    df_new = pd.DataFrame(data=np.round(Xnew, 5), 
                          columns=[cpvar],
                          index=tnew)
    df_new.index.names = ['datetime']
    
    df_new['data_gap_minutes'] = np.round(data_gap/60)/2 # convert from sum to average gap at point
    df_new = df_new.where(df_new.data_gap_minutes < maxgap_minutes).dropna()
    
    return df_new

for buoy in aux_data:
    data = aux_data[buoy]

    data["Date/Time"] = pd.to_datetime(data["Date/Time"])
    data = data.set_index("Date/Time")
    
    # valid = data["Date/Time"] - data["Date/Time"].dt.floor('30min') < pd.to_timedelta("1min")
    # valid_data = data[valid]
    freq = buoy_metadata(buoy)["Calculated Frequency"]
    freq_int = int(freq.replace("min", ""))
    interp_data = interpolate_rotation(data, freq=freq, maxgap_minutes=freq_int*3)

    interp_data.to_csv(saveloc + buoy + '.csv')