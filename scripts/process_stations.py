import pandas as pd
from helpers import *

def best_from_station(station_df):
    tbuoys = station_df[station_df["Buoy Type"] == "Thermistor"]
    if len(tbuoys) > 0:
        return tbuoys.idxmax().loc["length"]
    else:
        return station_df.idxmax().loc["length"]

buoy_meta = buoy_metadata()

all_buoys = buoy_meta.index.to_list()

valid_buoys = [buoy for buoy in all_buoys if usable_buoy(buoy)]


interp_lens = pd.DataFrame([{"Sensor ID": buoy, "length": len(buoy_data(buoy, "interp"))} for buoy in valid_buoys])
interp_lens = interp_lens.set_index("Sensor ID")

valid_buoys = buoy_meta.merge(interp_lens, how="right", left_index=True, right_index=True)

grouped_stations = valid_buoys[["DN Station ID", "Buoy Type", "length"]].groupby("DN Station ID")

# Maybe use gap filling algo here instead of directly getting data from the best buoy

for dir in ["../data/daily_stations/mosaic_dn1",
            "../data/daily_stations/mosaic_dn2"]:
    if not os.path.exists(dir):
        os.makedirs(dir)

best_buoys = []
for station in grouped_stations:
    station_buoy = best_from_station(station[1])
    downsample_data = buoy_data(station_buoy).set_index("datetime").between_time("11:59","12:01")

    dn = 2 if buoy_metadata().loc[station_buoy, "Deployment Leg"] == 5 else 1
    downsample_data.to_csv(f"../data/daily_stations/mosaic_dn{dn}/{station[0]}.csv")
    best_buoys.append([station[0], station_buoy, buoy_meta.loc[station_buoy, "Deployment Leg"]])

pd.DataFrame(best_buoys, columns=["Station ID", "sensor_id", "Deployment Leg"]).set_index("Station ID").to_csv("../data/metadata/station_metadata.csv")