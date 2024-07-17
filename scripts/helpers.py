import os
import pandas as pd
import proplot as pplt

SUPPORTED_VERSIONS = ["interp", "qc", "original"]

def print(*val):
    display(*val)

def buoy_metadata(buoy=None):
    all = pd.read_csv("../data/metadata/buoy_metadata.csv", index_col=0)
    if buoy:
        return all.loc[buoy]
    else:
        return all

def station_metadata():
    return pd.read_csv("../data/metadata/station_metadata.csv", index_col=0)

def simba_metadata():
    return pd.read_csv("../data/metadata/simba_metadata.csv", index_col='ID (Meereisportal name)')

def buoy_data(buoy, version="interp"):
    """
    buoy: The Sensor ID of the buoy whose data is being fetched
    version: Which version to fetch, see SUPPORTED_VERSIONS

    This function gets the original, quality control, and interpolated data for a given buoy
    """

    if version not in SUPPORTED_VERSIONS:
        raise("Version not supported")
    
    buoy_meta = buoy_metadata().loc[buoy]

    if version == "original":
        original_file = buoy_meta['DN Station ID'] + '_' + buoy_meta['IMEI'] + '_' + buoy
        original_folder = '../data/adc_dn_tracks/'
        orig_data = pd.read_csv(original_folder + original_file + '.csv')
        orig_data['datetime'] = pd.to_datetime(orig_data['datetime'])
        return orig_data
    else:
        dn = '2' if buoy_meta.loc['Deployment Leg'] == 5 else '1'
        
        saveloc = f"../data/{version}_buoys/mosaic_dn{dn}/"
        data = pd.read_csv(saveloc + buoy + '.csv')

        data["datetime"] = pd.to_datetime(data['datetime'])
        return data


def station_data(station):
    """
    station: The station ID

    This function gets the representative interpolated daily data for buoys starting at a given station
    """
    
    meta = station_metadata().loc[station]

    dn = '2' if meta.loc['Deployment Leg'] == 5 else '1'
    
    saveloc = f"../data/daily_stations/mosaic_dn{dn}/{station}.csv"
    data = pd.read_csv(saveloc)

    data["datetime"] = pd.to_datetime(data['datetime'])
    return data

def simba_data(buoy):
    saveloc = f"../data/simba_data/clean/{buoy}.csv"
    return pd.read_csv(saveloc, index_col=0, parse_dates=True)

def era5_data(buoy):
    saveloc = f"../data/interp_buoys_era5/mosaic_dn1/{buoy}_era5.csv"
    return pd.read_csv(saveloc)

def plot_path(buoys):
    fig, axs = pplt.subplots(ncols=1, refwidth=7, proj=('npstere'))
    fig.format(suptitle='Buoy Paths')
    axs.format(land=True)

    axs[0].format(boundinglat=60)
    for b in buoys:
        axs[0].plot(buoy_data(b)['longitude'], buoy_data(b)['latitude'], color="red")