import pandas as pd
import proplot as pplt
import numpy as np
import os

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

for buoy in aux_data:
    # print(aux_data[buoy])
    data = aux_data[buoy]

    data["Date/Time"] = pd.to_datetime(data["Date/Time"])
    valid = data["Date/Time"] - data["Date/Time"].dt.floor('30min') < pd.to_timedelta("1min")
    valid_data = data[valid]

    valid_data.loc[:, "Date/Time"] = valid_data["Date/Time"].dt.floor('30min')

    valid_data.to_csv(saveloc + buoy + '.csv')