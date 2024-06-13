import os
import pandas as pd
import proplot as pplt

SUPPORTED_VERSIONS = ["interp", "qc", "original"]

def get_metadata():
    metadata = pd.read_csv('../data/adc_dn_tracks/DN_buoy_list_v2.csv')
    freq_lookup = pd.read_csv('../data/postqc_freqs.csv')

    metadata = pd.merge(metadata, freq_lookup, left_on='Sensor ID', right_on='sensor_id', how="outer")
    metadata = metadata.drop(columns='sensor_id').rename(columns={'freq':'Calculated Frequency'}).set_index("Sensor ID")

    return metadata

def usable_buoy(buoy):
    return buoy+'.csv' in os.listdir('../data/interp_buoys/mosaic_dn2') + os.listdir('../data/interp_buoys/mosaic_dn1')

def buoy_data(buoy, version="interp"):
    """
    buoy: The Sensor ID of the buoy whose data is being fetched
    version: Which version to fetch, see SUPPORTED_VERSIONS

    This function gets the original, quality control, and interpolated data for a given buoy
    """

    if version not in SUPPORTED_VERSIONS:
        raise("Version not supported")
    
    buoy_meta = get_metadata().loc[buoy]

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

def graph_data(buoy, include=["original", "qc", "interp"], showcleaned=False):
    """
    Graphs the data for a given buoy sensor id and returns the graph objects

    include: Choose which steps in the data processing to graph
    showcleaned: If True, mark the data removed by quality control with scatter points
    """
    fig = pplt.figure(refwidth=6, refheight=2, share=False)
    axs = fig.subplots(nrows=len(include), ncols=2)

    all_data = {key: buoy_data(buoy, key) for key in SUPPORTED_VERSIONS}

    for i, name in enumerate(include):
        axs[2*i].plot(all_data[name]["datetime"], all_data[name]["latitude"], marker='.', ms=1, lw=0) # this way it's easy to see where gaps are
        axs[2*i].format(xlocator='month',
                        xformatter='%b %d',
                        title=f"{name}: Latitude of {buoy}, Length: {len(all_data[name])}", xlabel="", ylabel="latitude")

        axs[2*i+1].plot(all_data[name]['datetime'], all_data[name]["longitude"], marker='.', ms=1, lw=0)
        axs[2*i+1].format(xlocator='month',
                          xformatter='%b %d',
                          title=f"{name}: Longitude of {buoy}, Length: {len(all_data[name])}",
                          xlabel="", # Since the x ticks are dates, we don't need the extra text
                          ylabel="longitude")

        if showcleaned:
            merged = all_data['original'].merge(all_data['qc'], on='datetime', how='left', indicator=True)
            flagged = merged[merged['_merge'] == 'left_only']
            
            axs[2*i].scatter(flagged['datetime'], flagged["latitude_x"], s=0.2)
            axs[2*i].format(xlocator='month', xformatter='%b %d', xlabel="")

            axs[2*i+1].scatter(flagged['datetime'], flagged["longitude_x"], s=0.2)
            axs[2*i+1].format(xlocator='month', xformatter='%b %d', xlabel="")
        fig.format(xrotation=45)
    return fig, axs
