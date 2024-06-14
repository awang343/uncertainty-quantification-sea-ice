import os
import pandas as pd
import proplot as pplt

SUPPORTED_VERSIONS = ["interp", "qc", "original"]

def buoy_metadata():
    return pd.read_csv("../data/metadata/buoy_metadata.csv", index_col=0)

def station_metadata():
    return pd.read_csv("../data/metadata/station_metadata.csv", index_col=0)

def usable_buoy(buoy):
    exclude_buoys = ["2019P101"]
    return buoy not in exclude_buoys and buoy+'.csv' in os.listdir('../data/interp_buoys/mosaic_dn2') + os.listdir('../data/interp_buoys/mosaic_dn1')

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