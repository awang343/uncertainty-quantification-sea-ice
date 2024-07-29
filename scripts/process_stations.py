import pandas as pd
from helpers import *

def best_from_station(station_df):
    #tbuoys = station_df[station_df["Buoy Type"] == "Thermistor"]
    #if len(tbuoys) > 0:
    #    return tbuoys.idxmax().loc["length"]
    #else:
    return station_df.idxmax().loc["length"]

for dir in ["../data/daily_stations",
            "../data/daily_stations/mosaic_dn1",
            "../data/daily_stations/mosaic_dn2"]:
    if not os.path.exists(dir):
        os.makedirs(dir)

buoy_meta = buoy_metadata()
all_buoys = buoy_meta.index.to_list()

valid_buoys = buoy_meta[buoy_meta["Interp"] == True].index
interp_lens = pd.DataFrame([{"Sensor ID": buoy, 
                             "length": buoy_data(buoy)["datetime"].max() - buoy_data(buoy)["datetime"].min()} 
                             for buoy in valid_buoys])
interp_lens = interp_lens.set_index("Sensor ID")

valid_buoy_meta = buoy_meta.merge(interp_lens, how="right", left_index=True, right_index=True)

grouped_stations = valid_buoy_meta[["DN Station ID", "Buoy Type", "length"]].groupby("DN Station ID")

best_buoys = []
for station in grouped_stations:
    #if station[0] == "CO1":
    #    test = station[1].head(2)
    #    for sensor in test.index:
    #        print(buoy_data(sensor))

    station_buoy = best_from_station(station[1])
    downsample_data = buoy_data(station_buoy).set_index("datetime").resample("1d", offset="12h").asfreq().dropna()
    downsample_data_mn = buoy_data(station_buoy).set_index("datetime").resample("1d").asfreq().dropna()
    
    dn = 2 if buoy_metadata().loc[station_buoy, "Deployment Leg"] == 5 else 1
    downsample_data.to_csv(f"../data/daily_stations/mosaic_dn{dn}/{station[0]}.csv")
    best_buoys.append([station[0], station_buoy, buoy_meta.loc[station_buoy, "Deployment Leg"], len(downsample_data)])

pd.DataFrame(best_buoys, columns=["Station ID", "sensor_id", "Deployment Leg", "# Days"]).set_index("Station ID").to_csv("../data/metadata/station_metadata.csv")